import os
import sys
import argparse
import yaml
from easydict import EasyDict

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
        sys.path.append(env_path)

from pytracking.evaluation.datasets import get_perturb_dataset, get_dataset
from pytracking.evaluation.tracker import Tracker
from pytracking.analysis.plot_results import plot_results, print_results
from pytracking.utils.suffix import construct_suffix

#TODO evaluate on multi-datasets for only one tracker
def main():
    parser = argparse.ArgumentParser(description='arguments for analysis')
    parser.add_argument('-c', '--config', type=str, help='path to anaysis configuration')
    args = parser.parse_args()

    # load configurations
    try:
        with open(args.config, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            cfg = EasyDict(config)
    except:
        raise Exception('Unable to open configuration file: {}'.format(args.config))

    # assemble various trackers with different parameters
    trackers = []
    for idx, tracker in enumerate(cfg.trackers):
        for param in cfg.parameters[idx]:
            trackers.append(Tracker(tracker, param))

    if cfg.perturb:
        # load datasets
        datasets = get_dataset(cfg.datasets) # for comparison baseline
        for perturbation in cfg.perturbations:
            datasets+=get_perturb_dataset(perturbation, cfg.datasets)

        plot_results(trackers, datasets, 'test_multi_tracker_perturb_datasets', plot_types=cfg.plots, perturb_info=perturbation)
        # print_results(trackers, dataset, report_name, plot_types=cfg.plots, perturb_info=perturbation)
    else:
        datasets = get_dataset(cfg.datasets)
        plot_results(trackers, datasets, 'test_multi_tracker_clean_datasets', plot_types=cfg.plots)
        # print_results(trackers, datasets, report_name, plot_types=cfg.plots)
    
# evaluate multi-trackers or one tracker with one datasets
# def main():
#     parser = argparse.ArgumentParser(description='arguments for analysis')
#     parser.add_argument('-c', '--config', type=str, help='path to anaysis configuration')
#     args = parser.parse_args()

#     # load configurations
#     try:
#         with open(args.config, 'r') as f:
#             config = yaml.load(f, Loader=yaml.FullLoader)
#             cfg = EasyDict(config)
#     except:
#         raise Exception('Unable to open configuration file: {}'.format(args.config))

#     # assemble various trackers with different parameters
#     trackers = []
#     for idx, tracker in enumerate(cfg.trackers):
#         for param in cfg.parameters[idx]:
#             trackers.append(Tracker(tracker, param)) 

#     if cfg.perturb:
#         # load datasets
#         for perturbation in cfg.perturbations:
#             datasets = get_perturb_dataset(perturbation, cfg.datasets)
#             report_name = '{}.test.{}'.format(cfg.datasets, construct_suffix(perturbation))
#             plot_results(trackers, datasets, report_name, plot_types=cfg.plots, perturb_info=perturbation)
#             # print_results(trackers, dataset, report_name, plot_types=cfg.plots, perturb_info=perturbation)
#     else:
#         report_name = '{}.test'.format(cfg.datasets)
#         datasets = get_dataset(cfg.datasets)
#         plot_results(trackers, datasets, report_name, plot_types=cfg.plots)
#         # print_results(trackers, datasets, report_name, plot_types=cfg.plots)

if __name__ == '__main__':
    main()


