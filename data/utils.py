

def check_perturb(perturb_info: dict) -> bool:
    """Validate the perturb information."""
    pass

def find_jpg_dir(target: str) -> list:
    """Find all the position in target where exists images.

    NOTE: Under the discussion of object tracking, the target of this function is to find the clip's path where the frames are stored. Thus, a universe perturbation methos can be utilized for each video clip.
    
    Args:
        target: str, the target dataset path to find frames.

    Return:
        jpg_dir: list, contains all the path str where images are found.
    """

    pass

def perturb_sequence():
    """Perturb a sequence."""
    pass


# def process_img(img, mode, var):
#     """Perturb a image with given perturbation mode and variable."""
#     origin_img = Image.open(img)
#     perturb_img = var_func(im, severity)
#     cv2.imwrite(str(o), perturb_img)
#     return perturb_img


# def process_single_clip(i, o, ARGS):
#     if i.is_file():
#         shutil.copy(i, o)
#         return
#     o.mkdir(parents=True, exist_ok=True)
#     img_list = []
#     for x in os.listdir(i):
#         if x.endswith('.jpg') or x.endswith('.png'):
#             img_list.append(x)
#         else:
#             process_single_clip(i / x, o / x, ARGS)
#     img_list.sort()
#     img_list = list(filter(lambda x: not (o / x).exists(), img_list)) # resume
#     if len(img_list) == 0:
#         return 
#     series = get_severity(len(img_list), ARGS)
#     var_func = var2func[ARGS.var]
#     tasks = [(i / img_list[k], o / img_list[k], var_func, series[k]) for k in range(len(img_list))]
#     logging.info(f'processing {i}...')
#     pool = Pool(10)
#     pool.starmap(process_single_image, tasks)
#     pool.close()
#     pool.join()