import os
import sys
import shutil
import time
from multiprocessing import Pool
from pathlib import Path

import argparse
import numpy as np
from PIL import Image
import cv2

from mode import get_severity
from var import *


var2func = {
    'motion_blur': motion_blur,
    'fog': fog,
}


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path', type=str, help='where is your dataset')
    parser.add_argument('-o', '--output_path', type=str, help='where to store the new dataset')
    parser.add_argument('-m', '--mode', type=str, help='time series mode [consisten|burst|random|smooth]')
    parser.add_argument('-v', '--var', type=str, help='corruption or perturbation type')
    parser.add_argument('--severity', type=int, default=1, help='severity of consistent and burst perturbation mode')
    parser.add_argument('--max_pos_count', type=int, default=1, help='maximum count of position to perturb in random mode')
    parser.add_argument('--max_frame_count', type=int, default=1, help='maximum count of frame at a position to perturb in random mode')
    parser.add_argument('--max_level', type=int, default=1, help='the maximum level of severity in smooth mode')
    parser.add_argument('--order', type=str, default='ascending', help='the trending of smooth and burst mode, [ascending|descending]')
    parser.add_argument('--burst_pos', type=int, default=None, help='where the severity is suddenly changed')
    args = parser.parse_args()
    return args


def process_single_image(i, o, var_func, severity):
    # im = cv2.imread(str(i))
    im = Image.open(str(i))
    p_im = var_func(im, severity)
    cv2.imwrite(str(o), p_im)


def process_single_clip(i, o, args):
    if i.is_file():
        shutil.copy(i, o)
        return
    o.mkdir(parents=True, exist_ok=True)
    img_list = []
    for x in os.listdir(i):
        if x.endswith('.jpg') or x.endswith('.png'):
            img_list.append(x)
        else:
            process_single_clip(i / x, o / x, args)
    img_list.sort()
    series = get_severity(len(img_list), args)
    var_func = var2func[args.var]
    tasks = [(i / img_list[k], o / img_list[k], var_func, series[k]) for k in range(len(img_list))]
    print(f'processing {i}...')
    pool = Pool(10)
    pool.starmap(process_single_image, tasks)
    pool.close()
    pool.join()


def main():
    args = parseargs()
    if args.output_path is None:
        output_path = args.input_path.rstrip('/') + '.' + args.var + '.' + args.mode
        if args.mode == 'consistent':
            output_path += '_' + str(args.severity)
        elif args.mode == 'random':
            output_path += '_' + str(args.max_pos_count) + '_' + str(args.max_frame_count)
        elif args.mode == 'smooth':
            output_path += '_' + str(args.max_level)
        elif args.mode == 'burst':
            output_path = '_' + str(args.order) + '_' + str(args.severity) + '_' + str(args.burst_pos)
    else:
        output_path = args.output_path
    input_path = Path(args.input_path)
    output_path = Path(output_path)
    print('construction begins...')
    process_single_clip(input_path, output_path, args)
    print('construction is done')

if __name__ == '__main__':
    start = time.time()
    main()
    print(f'time consuming: {time.time()-start}')
