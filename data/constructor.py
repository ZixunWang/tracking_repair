import os
import sys
import time
from pathlib import Path
import logging
import argparse
import re
from easydict import EasyDict
import yaml

from utils import process_single_clip, get_perturbation_name, validate_perturbation


logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(message)s',
                datefmt='%a %d %b %Y %H:%M:%S')

def main():
    parser = argparse.ArgumentParser(description='arguments for perturbing datasets')
    parser.add_argument('-c', '--config', type=str, help='path to perturbation configuration')
    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            cfg = EasyDict(config)
    except:
        raise Exception('Unable to open configuration file: {}'.format(args.config))

    if not cfg.SPLIT: # for those datasets released without pre-defined split
        input_path = os.path.join(cfg.ROOT, cfg.DATASET)
    else:
        input_path = os.path.join(cfg.ROOT, cfg.DATASET, cfg.SPLIT)

    if not os.path.exists(input_path):
        raise FileNotFoundError('Dataset not found: {}'.format(input_path))

    valid_state, idx = validate_perturbation(cfg.perturbations)
    if valid_state:
        perturbation_list = cfg.perturbations
    else:
        raise ValueError('The {}th perturbation setting from config file {} is invalid.'.format(idx, args.config))

    logging.info('Perturbation for {} begins:'.format(input_path))

    for perturbation in perturbation_list:
    
        input_path_node = re.findall('\/\w+', input_path)
        output_path = os.path.join(''.join(input_path_node[:-1]), get_perturbation_name(input_path_node[-1].split('/')[-1], perturbation))

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        logging.info(f'peturbation configs:\n\t\t\t\t\t{perturbation}')
        process_single_clip(Path(input_path), Path(output_path), perturbation, logger=logging)
    logging.info('Perturbation is done.')

if __name__ == '__main__':
    start = time.time()
    main()
    logging.info(f'Time consuming: {time.time()-start}.')
