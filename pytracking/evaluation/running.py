import numpy as np
import multiprocessing
import os
import sys
from itertools import product
from collections import OrderedDict
from pytracking.evaluation import Sequence, Tracker
from ltr.data.image_loader import imwrite_indexed
from pytracking.utils.suffix import construct_suffix


def _save_tracker_output(seq: Sequence, tracker: Tracker, output: dict, perturb_info: dict):
    """Saves the output of the tracker."""

    if not os.path.exists(tracker.results_dir):
        os.makedirs(tracker.results_dir)

    #TODO default to save test results, revise to suit other splits
    if perturb_info:
        perturb_suffix = construct_suffix(perturb_info)
        base_results_path = os.path.join(tracker.results_dir, seq.dataset, 'test.{}'.format(perturb_suffix), seq.name)
        segmentation_path = os.path.join(tracker.segmentation_dir, seq.dataset, 'test.{}'.format(perturb_suffix), seq.name)
    else:
        base_results_path = os.path.join(tracker.results_dir, seq.dataset, 'test', seq.name)
        segmentation_path = os.path.join(tracker.segmentation_dir, seq.dataset, 'test', seq.name)

    frame_names = [os.path.splitext(os.path.basename(f))[0] for f in seq.frames]

    # ==== update ====
    def check_exist(file):
        file = os.path.abspath(file)
        parent = file[:file.rfind('/')]
        if not os.path.exists(parent):
            os.makedirs(parent)
    def save_bb(file, data):
        check_exist(file)
        tracked_bb = np.array(data).astype(int)
        np.savetxt(file, tracked_bb, delimiter='\t', fmt='%d')

    def save_time(file, data):
        check_exist(file)
        exec_times = np.array(data).astype(float)
        np.savetxt(file, exec_times, delimiter='\t', fmt='%f')

    def _convert_dict(input_dict):
        data_dict = {}
        for elem in input_dict:
            for k, v in elem.items():
                if k in data_dict.keys():
                    data_dict[k].append(v)
                else:
                    data_dict[k] = [v, ]
        return data_dict

    for key, data in output.items():
        # If data is empty
        if not data:
            continue

        if key == 'target_bbox':
            if isinstance(data[0], (dict, OrderedDict)):
                data_dict = _convert_dict(data)

                for obj_id, d in data_dict.items():
                    bbox_file = '{}_{}.txt'.format(base_results_path, obj_id)
                    save_bb(bbox_file, d)
            else:
                # Single-object mode
                bbox_file = '{}.txt'.format(base_results_path)
                save_bb(bbox_file, data)

        elif key == 'time':
            if isinstance(data[0], dict):
                data_dict = _convert_dict(data)

                for obj_id, d in data_dict.items():
                    timings_file = '{}_{}_time.txt'.format(base_results_path, obj_id)
                    save_time(timings_file, d)
            else:
                timings_file = '{}_time.txt'.format(base_results_path)
                save_time(timings_file, data)

        elif key == 'segmentation':
            assert len(frame_names) == len(data)
            if not os.path.exists(segmentation_path):
                os.makedirs(segmentation_path)
            for frame_name, frame_seg in zip(frame_names, data):
                imwrite_indexed(os.path.join(segmentation_path, '{}.png'.format(frame_name)), frame_seg)


def run_sequence(seq: Sequence, tracker: Tracker, debug: bool, visdom_info: dict, perturb_info: dict):
    """Runs a tracker on a sequence."""

    def _results_exist():
        """Default to find results of test split."""
        if perturb_info is not None:
            suffix = construct_suffix(perturb_info)
            if seq.object_ids is None:
                bbox_file = '{}/{}/{}.txt'.format(tracker.results_dir, seq.dataset, 'test.{}'.format(suffix), seq.name)
                return os.path.isfile(bbox_file)
            else:
                bbox_files = ['{}/{}/{}_{}.txt'.format(tracker.results_dir, seq.dataset, 'test.{}'.format(suffix), seq.name, obj_id) for obj_id in seq.object_ids]
                missing = [not os.path.isfile(f) for f in bbox_files]
                return sum(missing) == 0
        else:
            if seq.object_ids is None:
                bbox_file = '{}/{}/{}/{}.txt'.format(tracker.results_dir, seq.dataset, 'test', seq.name)
                return os.path.isfile(bbox_file)
            else:
                bbox_files = ['{}/{}/{}/{}_{}.txt'.format(tracker.results_dir, seq.dataset, 'test', seq.name, obj_id) for obj_id in seq.object_ids]
                missing = [not os.path.isfile(f) for f in bbox_files]
                return sum(missing) == 0

    if _results_exist() and not debug:
        print('FPS: {}'.format(-1))
        return

    print('Tracker: {} {} {} ,  Sequence: {}'.format(tracker.name, tracker.parameter_name, tracker.run_id, seq.name))

    if debug:
        output = tracker.run_sequence(seq, debug=debug, visdom_info=visdom_info)
    else:
        try:
            output = tracker.run_sequence(seq, debug=debug, visdom_info=visdom_info)
        except Exception as e:
            print(e)
            return

    sys.stdout.flush()

    if isinstance(output['time'][0], (dict, OrderedDict)):
        exec_time = sum([sum(times.values()) for times in output['time']])
        num_frames = len(output['time'])
    else:
        exec_time = sum(output['time'])
        num_frames = len(output['time'])

    print('FPS: {}'.format(num_frames / exec_time))

    if not debug:
        _save_tracker_output(seq, tracker, output, perturb_info)


def run_dataset(dataset, trackers, debug, threads, visdom_info=None, perturb_info=None):
    """Runs a list of trackers (tracker with different parameter) on a list of Sequence.
    args:
        dataset: list of Sequence instances, forming a dataset.
        trackers: list of Tracker instances.
        debug: debug level.
        threads: number of threads to use (default 0).
        visdom_info: dict containing information about the server for visdom
    """
    multiprocessing.set_start_method('spawn', force=True)

    print('Evaluating {:4d} trackers on {:5d} sequences'.format(len(trackers), len(dataset)))

    if threads <= 0:
        for seq in dataset:
            for tracker_info in trackers:
                run_sequence(seq, tracker_info, debug, visdom_info, perturb_info)
    else:
        param_list = [(seq, tracker_info, debug, visdom_info, perturb_info) for seq, tracker_info in product(dataset, trackers)]
        with multiprocessing.Pool(processes=threads) as pool:
            pool.starmap(run_sequence, param_list)
    print('Done')
