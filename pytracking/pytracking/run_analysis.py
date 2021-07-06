import os
import sys

import argparse

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
        sys.path.append(env_path)

from evaluation.datasets import get_perturb_dataset, get_dataset
from evaluation.tracker import Tracker
from analysis.plot_results import plot_results
from utils.suffix import construct_suffix


def example():
    tracker_name, tracker_param = 'dimp', 'dimp50'
    trackers = [Tracker(tracker_name, tracker_param, None)]
    perturb_info = {
        'mode': 'consistent',
        'variable': 'motion_blur',
        'setting': {
            'severity': 5,
            'max_position': 1,
            'max_frame': 1,
            'max_level': 1,
            'order': 'ascending',
            'burst_position': 1,
        }
    }
    suffix = construct_suffix(perturb_info)
    dataset = get_perturb_dataset(perturb_info, 'got10k_test')
    plot_results(trackers, dataset, 'example_report', suffix=suffix)


def example_normal():
    trackers = [Tracker('dimp', 'dimp50')]
    dataset = get_dataset('got10k_test')
    plot_results(trackers, dataset, 'example_normal_report')


if __name__ == '__main__':
    example()
