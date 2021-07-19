# -*- encoding: utf-8 -*-
"""
@File    :   suffix.py
@Time    :   2021/07/15 09:17:40
@Author  :   Xing Yun
"""



def construct_suffix(perturb_args) -> str:
    mode = perturb_args['mode']
    var = perturb_args['var']
    base = var+'.'+mode

    if mode == 'consistent':
        return base+'.'+str(perturb_args['mode_args']['severity'])
    elif mode == 'random':
        return base+'.'+str(perturb_args['mode_args']['max_pos_count']) + '_'+ str(perturb_args['mode_args']['max_frame_count'])
    elif mode == 'smooth':
        return base+'.'+perturb_args['mode_args']['order']+'_'+str(perturb_args['mode_args']['max_level'])
    elif mode == 'burst':
        return base+'.'+perturb_args['mode_args']['order']+'_'+str(perturb_args['mode_args']['severity'])+'_'+str(perturb_args['mode_args']['burst_pos'])
    else:
        raise ValueError(f'Invalid mode setting: {mode}')
