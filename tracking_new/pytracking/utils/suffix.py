# -*- encoding: utf-8 -*-
"""
@File    :   suffix.py
@Time    :   2021/07/04 17:33:00
@Author  :   Xing Yun
"""


def construct_suffix(perturb_args) -> str:
    mode = perturb_args['mode']
    var = perturb_args['variable']
    base = var+'.'+mode

    if mode == 'consistent':
        return base+'_'+perturb_args['setting']['severity']
    elif mode == 'random':
        return base+'_'+perturb_args['setting']['max_position']+'_'+perturb_args['setting']['max_frame']
    elif mode == 'smooth':
        return base+'_'+perturb_args['setting']['order']+'_'+perturb_args['setting']['max_level']
    elif mode == 'burst':
        return base+'_'+perturb_args['setting']['order']+'_'+perturb_args['setting']['severity']+'_'+perturb_args['setting']['burst_position']
    else:
        raise ValueError(f'Invalid mode setting: {mode}')