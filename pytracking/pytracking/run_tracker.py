import os
# from projects.tracking_repair.pytracking.pytracking.evaluation.datasets import get_perturb_dataset
import sys
import argparse

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)


from evaluation.datasets import get_dataset, get_perturb_dataset
from evaluation.running import run_dataset
from evaluation.tracker import Tracker


def run_tracker(tracker_name, tracker_param, run_id=None, dataset_name='otb', sequence=None, debug=0, threads=0,
                visdom_info=None, perturb_info=None):
    """Run tracker on sequence or dataset.
    args:
        tracker_name: Name of tracking method.
        tracker_param: Name of parameter file.
        run_id: The run id.
        dataset_name: Name of dataset (otb, nfs, uav, tpl, vot, tn, gott, gotv, lasot).
        sequence: Sequence number or name.
        debug: Debug level.
        threads: Number of threads.
        visdom_info: Dict optionally containing 'use_visdom', 'server' and 'port' for Visdom visualization.
    """

    #! visdom_info and perturb_info will never be None under this condition
    visdom_info = {} if visdom_info is None else visdom_info
    perturb_info = {} if perturb_info is None else perturb_info

    if not perturb_info:
        dataset = get_dataset(dataset_name)
    else:
        dataset = get_perturb_dataset(perturb_info, dataset_name)

    if sequence is not None:
        dataset = [dataset[sequence]]

    trackers = [Tracker(tracker_name, tracker_param, run_id)]

    run_dataset(dataset, trackers, debug, threads, visdom_info=visdom_info, perturb_info=perturb_info)


def main():
    parser = argparse.ArgumentParser(description='Run tracker on sequence or dataset.')
    parser.add_argument('tracker_name', type=str, help='Name of tracking method.')
    parser.add_argument('tracker_param', type=str, help='Name of parameter file.')
    parser.add_argument('--runid', type=int, default=None, help='The run id.')
    parser.add_argument('--dataset_name', type=str, default='otb', help='Name of dataset (otb, nfs, uav, tpl, vot, tn, gott, gotv, lasot).')
    parser.add_argument('--sequence', type=str, default=None, help='Sequence number or name.')
    parser.add_argument('--debug', type=int, default=0, help='Debug level.')
    parser.add_argument('--threads', type=int, default=0, help='Number of threads.')
    parser.add_argument('--use_visdom', type=bool, default=True, help='Flag to enable visdom.')
    parser.add_argument('--visdom_server', type=str, default='127.0.0.1', help='Server for visdom.')
    parser.add_argument('--visdom_port', type=int, default=8097, help='Port for visdom.')

    #! change for purpose
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

    try:
        seq_name = int(args.sequence)
    except:
        seq_name = args.sequence

    visdom_info = {
        'use_visdom': args.use_visdom,
        'server': args.visdom_server,
        'port': args.visdom_port
    }

    perturb_info = {
        'perturb_on': args.perturb,
        'mode':args.mode,
        'variable':args.var,
        'setting': {
            'severity':args.severity,
            'max_position':args.max_pos_count,
            'max_frame': args.max_frame_count,
            'max_level': args.max_level,
            'order': args.order,
            'burst_position': args.burst_pos
            }
        }

    run_tracker(args.tracker_name, args.tracker_param, args.runid, args.dataset_name, seq_name, args.debug,
                args.threads, visdom_info, perturb_info)


if __name__ == '__main__':
    main()
