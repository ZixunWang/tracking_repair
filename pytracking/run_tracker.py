import os
import sys
import argparse
import yaml
from easydict import EasyDict

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)

from pytracking.evaluation.datasets import get_dataset, get_perturb_dataset
from pytracking.evaluation.running import run_dataset
from pytracking.evaluation.tracker import Tracker

def main():
    parser = argparse.ArgumentParser(description='arguments for evaluation')
    parser.add_argument('-c', '--config', type=str, help='path to evaluation configuration')
    args = parser.parse_args()

    # load configurations
    try:
        with open(args.config, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            cfg = EasyDict(config)
    except:
        raise Exception('Unable to open configuration file: {}'.format(args.config))

    # assemble trackers
    trackers = []
    for idx, tracker in enumerate(cfg.trackers):
        trackers.append(Tracker(tracker, cfg.parameters[idx], cfg.run_id)) #NOTE is run_id influences tracker construction

    # load and evaluate
    if cfg.perturb:
        for perturb_info in cfg.perturbations:
            dataset = get_perturb_dataset(perturb_info, cfg.dataset)
            if cfg.sequence is not None:
                dataset = [dataset[cfg.sequence]] # get sequence with specified sequence name

            run_dataset(dataset, trackers, cfg.debug, cfg.threads, cfg.visdom, perturb_info)
    else:
        dataset = get_dataset(cfg.dataset)
        if cfg.sequence is not None:
            dataset = [dataset[cfg.sequence]]

        run_dataset(dataset, trackers, cfg.debug, cfg.threads, cfg.visdom)

if __name__ == '__main__':
    main()
