import os
import time

import argparse
import numpy as np
import cv2
import visdom
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def vis_images_seq(img_root, bbox=None):
    env = visdom.Visdom(env='Test')
    meta = env.image(np.zeros((3, 256, 256)))
    im_list = [i for i in os.listdir(img_root) if i.endswith('jpg')]
    im_list.sort()
    if bbox is not None:
        bboxes = []
        color = (255, 0, 0)
        with open(bbox, 'r') as f:
            for line in f.readlines():
                bboxes.append([int(x) for x in line.strip().split()])
    for k, im in enumerate(im_list):
        i = cv2.imread(os.path.join(img_root, im))[:, :, ::-1].copy()
        if bbox is not None:
            cv2.rectangle(i, (bboxes[k][0], bboxes[k][1]), (bboxes[k][0]+bboxes[k][2],bboxes[k][1]+bboxes[k][3]), color, 2)
        env.image(i.transpose(2, 0, 1), win=meta)
        time.sleep(0.1)
    logger.info('visualization is done')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, help='where are the images')
    parser.add_argument('-b', type=str, help='where is the bbox.txt')
    args = parser.parse_args()
    vis_images_seq(args.i, args.b)

if __name__ == '__main__':
    main()
