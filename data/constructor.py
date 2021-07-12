import os
import sys
import shutil
import time
import logging
from multiprocessing import Pool
from pathlib import Path
import argparse

import numpy as np
from PIL import Image
import cv2

from mode import get_severity
from var import *


def main():

    parser = argparse.ArgumentParser(description='arguments for perturb datasets')

    # Dataset Info
    parser.add_argument('root', type=str, default='/DATASET/tracking/', help='where the datasets are stored')
    parser.add_argument('dataset', type=str, help='name of dataset')
    parser.add_argument('split', type=str,  help='split of dataset to perturb')

    # Perturbation Info
    ## basic
    parser.add_argument('--mode', type=str, help='perturbation mode [consistent|burst|random|smooth]')
    parser.add_argument('--var', type=str, help='the perturbation variable')
    ## details
    parser.add_argument('--severity', type=int, default=1, help='severity of consistent and burst perturbation mode')
    parser.add_argument('--max_pos_count', type=int, default=1, help='maximum count of position to perturb in random mode')
    parser.add_argument('--max_frame_count', type=int, default=1, help='maximum count of frame at a position to perturb in random mode')
    parser.add_argument('--max_level', type=int, default=1, help='the maximum level of severity in smooth mode')
    parser.add_argument('--order', type=str, default='ascending', help='the trending of smooth and burst mode, [ascending|descending]')
    parser.add_argument('--burst_pos', type=int, default=None, help='where the severity is suddenly changed')

    ARGS = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a %d %b %Y %H:%M:%S')

    if not os.path.exists(ARGS.root):
        raise ValueError('dataset root not found: {}'.format(ARGS.root))

    if not ARGS.split: # for those dataset without predefined splits
        dataset_path = os.path.join(ARGS.root, ARGS.dataset)
    else:
        dataset_path = os.path.join(ARGS.root, ARGS.dataset, ARGS.split)
    
    # check perturbation info

    # find the path to all the clip

    # for each clip, perturb the images

    # copy all the other files into the same root except for the top-level folder


    logging.info(f'construction begins...') #TODO more info
    process_single_clip(input_path, output_path, ARGS)
    logging.info(f'construction is done')

if __name__ == '__main__':
    start = time.time()
    main()
    logging.info(f'time consuming: {time.time()-start}')