from var import var2func

consistent = ' '*4 + "mode: 'consistent'\n" + ' '*4 + "mode_args:\n" + \
    ' '*6 + "severity: 3\n"
smooth = ' '*4 + "mode: 'smooth'\n" + ' '*4 + "mode_args:\n" + \
    ' '*6 + "order: 'ascending'\n" + ' '*6 + "max_level: 5\n"
random = ' '*4 + "mode: 'random'\n" + ' '*4 + "mode_args:\n" + \
    ' '*6 + "max_pos_count: 1\n" + ' '*6 + "max_frame_count: 3\n"
burst = ' '*4 + "mode: 'burst'\n" + ' '*4 + "mode_args:\n" + \
    ' '*6 + "order: 'ascending'\n" + ' '*6 + "severity: 5\n" + \
    ' '*6 + "burst_pos: null\n"

f = open('../configs/perturbation/OTB.yaml', 'w')
f.write("ROOT: '/DATASET/tracking'\n")
f.write("DATASET: 'OTB'\n")
f.write("SPLIT: 'test'\n")
f.write("perturbations:\n")
f.flush()

for c in var2func.keys():
    if c in ['snow', 'pedestrian']:
        continue
    s = ' '*2 + '-\n' + ' '*4 + f"var: '{c}'\n"
    f.write(s)
    f.write(consistent)
    f.write(s)
    f.write(smooth)
    f.write(s)
    f.write(random)
    f.write(s)
    f.write(burst)
    f.flush()

f.close()
