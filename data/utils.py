import os
import shutil
from multiprocessing import Pool

import yaml
from easydict import EasyDict
import numpy
from PIL import Image
import cv2

from mode import get_severity_sequence
from var import var2func
from mode import random, burst, consistent, smooth


def process_single_image(i, o, var, severity):
    # im = cv2.imread(str(i))
    im = Image.open(str(i))
    p_im = var2func[var](im, severity)
    cv2.imwrite(str(o), p_im)


def process_single_clip(i, o, perturb_info, logger=None):
    if i.is_file():
        shutil.copy(i, o)
        return
        
    o.mkdir(parents=True, exist_ok=True)
    img_list = []
    for x in os.listdir(i):
        if x.endswith('.jpg') or x.endswith('.png'):
            img_list.append(x)
        else:
            process_single_clip(i / x, o / x, perturb_info)

    img_list.sort()
    img_list = list(filter(lambda x: not (o / x).exists(), img_list)) # resume
    if len(img_list) == 0:
        return 

    severity_seq = get_severity_sequence(len(img_list), perturb_info['mode'], perturb_info['mode_args'])
    # var_func = var2func[perturb_info['var']]
    tasks = [(i / img_list[k], o / img_list[k], perturb_info['var'], severity_seq[k]) for k in range(len(img_list))]

    if logger is not None:
        logger.info(f'processing {i}...')

    pool = Pool(10)

    pool.starmap(process_single_image, tasks)
    pool.close()
    pool.join()


def cfg_from_yaml_file(cfg_file):

    with open(cfg_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    return config

def validate_perturbation(perturbations: list) -> bool:
    """Check whether the perturbation settings in the input setting list are valid.

    NOTE: Variable 'which' represents which perturbation setting is invalid, and 0 represents overall invalidation.

    Args:
        perturbation: list; set of perturbation settings

    Return:
        valid: bool; result of validation
        which: int; which perturbation setting is invalid
    """
    valid = True
    which = -1

    for idx, perturbation in enumerate(perturbations):
        mode_args = perturbation['mode_args'].keys()

        if perturbation['var'] not in var2func.keys():
            valid = False
        elif perturbation['mode'] == 'consistent': # severity
            valid = 'severity' in mode_args
        elif perturbation['mode'] == 'random': # max_pos_count/max_frame_count
            valid = 'max_pos_count' in mode_args and 'max_frame_count' in mode_args
        elif perturbation['mode'] == 'burst': # order/severity/burst_pos
            valid = 'order' in mode_args and 'severity' in mode_args and 'burst_pos' in mode_args
        elif perturbation['mode'] == 'smooth': # order, max_level
            valid = 'order' in mode_args and 'max_level' in mode_args
        else:
            raise ValurError('Unrecognized mode: {}'.format(perturbation['mode']))
        
        if not valid:
            which = idx+1
        
        return valid, which
    return valid, which


def get_perturbation_name(head: str, info: dict) -> str:
    """Construct the name for perturbation"""
    mode_args = info['mode_args'].values()
    args_name = '_'.join([str(arg) for arg in mode_args])
    return '.'.join([head, info['var'], info['mode'], args_name])