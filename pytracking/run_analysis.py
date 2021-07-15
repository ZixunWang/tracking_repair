import os
import sys
import argparse

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
        sys.path.append(env_path)

from pytracking.evaluation.datasets import get_perturb_dataset, get_dataset
from pytracking.evaluation.tracker import Tracker
from pytracking.analysis.plot_results import plot_results, print_results
from pytracking.utils.suffix import construct_suffix

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--tracker_name', type=str, help='Name of tracking method.')
    parser.add_argument('--tracker_param', type=str, help='Name of parameter file.')
    parser.add_argument('--dataset_name', type=str, default='otb', help='Name of dataset (otb, nfs, uav, tpl, vot, tn, gott, gotv, lasot).')

    parser.add_argument('--plots', type=str, default='success')

    parser.add_argument('--perturb', action='store_true', help='whether test perturbed dataset')
    parser.add_argument('--mode', type=str, help='time series mode [consisten|burst|random|smooth]')
    parser.add_argument('--var', type=str, help='corruption or perturbation type')
    parser.add_argument('--severity', type=int, default=1, help='severity of consistent and burst perturbation mode')
    parser.add_argument('--max_pos_count', type=int, default=1, help='maximum count of position to perturb in random mode')
    parser.add_argument('--max_frame_count', type=int, default=1, help='maximum count of frame at a position to perturb in random mode')
    parser.add_argument('--max_level', type=int, default=1, help='the maximum level of severity in smooth mode')
    parser.add_argument('--order', type=str, default='ascending', help='the trending of smooth and burst mode, [ascending|descending]')
    parser.add_argument('--burst_pos', type=int, default=None, help='where the severity is suddenly changed')

    args = parser.parse_args()

    perturb_info = {
        'perturb_on': args.perturb,
        'mode': args.mode ,
        'variable': args.var ,
        'setting': {
            'severity': args.severity ,
            'max_position': args.max_pos_count,
            'max_frame': args.max_frame_count,
            'max_level': args.max_level,
            'order': args.order,
            'burst_position': args.burst_pos
        }
    }

    # for one tracker with various paramenters
    trackers = [Tracker(args.tracker_name, param) for param in args.tracker_param.split(' ')]
    if perturb_info['perturb_on']:
        dataset = get_perturb_dataset(perturb_info, args.dataset_name)
        suffix = construct_suffix(perturb_info)
        # plot_results(trackers, dataset, 'test.'+suffix, plot_types=args.plots.split(' '), suffix=suffix)
        print_results(trackers, dataset, 'test.'+suffix, plot_types=args.plots.split(' '), suffix=suffix)
    else:
        dataset = get_dataset(args.dataset_name)
        # plot_results(trackers, dataset, 'test', plot_types=args.plots.split(' '))
        print_results(trackers, dataset, 'test', plot_types=args.plots.split(' '))

if __name__ == '__main__':
    main()
