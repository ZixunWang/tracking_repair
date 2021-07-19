import os
import time
import shutil
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import yaml
from easydict import EasyDict
import numpy as np
from PIL import Image
import cv2

from mode import get_severity_sequence
from var import var2func
from mode import random, burst, consistent, smooth


def process_single_sequence(task, chunk=128):
    """Accelerate I/O and perturbation by multi-threading and multi-processing respectively"""
    n = len(task['input'])
    var = task['var']
    for i in range(0, n, chunk):  # to avoid some menmory error
        start, end = i, i+chunk if i+chunk<=n else n
        inputs = task['input'][start:end]
        severities = task['severity'][start:end]
        outputs = task['output'][start:end]
        with ThreadPoolExecutor(max_workers=20) as executor:  # io intensive
            result_futures = map(lambda x: executor.submit(Image.open, str(x)), inputs)
            images = [f.result() for f in futures.as_completed(result_futures)]

        with ProcessPoolExecutor(max_workers=10) as executor:  # cpu intensive
            result_futures = map(lambda x: executor.submit(var2func[var], x[0], x[1]), zip(images, severities))
            p_images = [f.result() for f in futures.as_completed(result_futures)]

        with ThreadPoolExecutor(max_workers=20) as executor:  # io intensive
            result_futures = map(lambda x: executor.submit(cv2.imwrite, str(x[0]), x[1]), zip(outputs, p_images))
            result = [f.result() for f in futures.as_completed(result_futures)]
            assert np.alltrue(result), 'some error occurs when save images'


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
            process_single_clip(i / x, o / x, perturb_info, logger)

    img_list.sort()
    if len(img_list) == 0:
        return
    if len(list(filter(lambda x: not (o / x).exists(), img_list))) == 0:  # resume
        if logger is not None:
            logger.info(f'{i} has been done')
        return 
    severity_seq = get_severity_sequence(len(img_list), perturb_info['mode'], perturb_info['mode_args'])
    task = {
        'input': [i / im for im in img_list],
        'output': [o / im for im in img_list],
        'var': perturb_info['var'],
        'severity': severity_seq,
    }

    if logger is not None:
        logger.info(f'processing {i}...')
    start = time.time()
    process_single_sequence(task)
    time_cost = time.time() - start
    if logger is not None:
        logger.info('sequence time consuming: {} images within {:.2f} s. {:.2f} im/s'.format(len(img_list), time_cost, len(img_list)/time_cost))

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
            raise ValueError('Unrecognized mode: {}'.format(perturbation['mode']))
        
        if not valid:
            which = idx+1
        
        return valid, which
    return valid, which


def get_perturbation_name(head: str, info: dict) -> str:
    """Construct the name for perturbation"""
    mode_args = info['mode_args'].values()
    args_name = '_'.join([str(arg) for arg in mode_args])
    return '.'.join([head, info['var'], info['mode'], args_name])
