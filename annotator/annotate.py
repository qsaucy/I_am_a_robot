import os
import random
from glob import glob
import argparse
from shutil import copyfile, move
from config import DELIMITER


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with -- are optional
    dataset_path(required) : Root directory to load and save annotated dataset
    --dest_save : Path to the directory to save the annotated dataset
    --value_dataset : The value to set for picture with target element . Default value 0
    --ratio : The ratio for keeping picture without having target element.Usually captcha 3x3 has 6/9 pictures without target and 3/9. To keep a balanced dataset use 50. Default value 50.
    --src_dataset : name of the dataset filename. Default dataset

    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Annotated Dataset.')
    parser.add_argument('dataset_path')
    parser.add_argument('--dest_save', dest='dest_save', help="directory in dataset_path to save the file ")
    parser.add_argument("--value_dataset", dest='value_dataset',default=1,help="between 0 and 9 ")
    parser.add_argument("--ratio", dest='ratio',default=50, help="int between 0 and 100, ratio of keeping image without the target objective ")
    parser.add_argument("--src_dataset", dest='dataset',default="dataset", help="dataset name. Same as --dir for copy_captcha_with_condition")
    args = parser.parse_args()

    return args

def main ():
    """
    Loop over all file in dataset_path/dataset print the name of the file. User has to enter the --value_dataset if the picture show the target
    Else type anything else or just enter. The program does not show picture because is not effective. Can not keep the focus on the terminal.
    You can open the picture folder and watch the first image. Image will be copy in the dest_save then move to dataset.bak to keep your dataset fully untouched
    /!\ Windows doesnt sort file as python when starting with number, be carefull or use copy_captcha_with_condition. It will randomly rename picture with lowercase char
    :return:
    """
    user_args=manage_parameters()
    directory =user_args.dataset_path
    dest_save = user_args.dest_save
    dataset = user_args.dataset
    # create directory if not already exist
    if not os.path.exists(directory+DELIMITER+dest_save):
        os.mkdir(directory+DELIMITER+dest_save)
    if not os.path.exists(directory+DELIMITER+dataset):
        os.mkdir(directory+DELIMITER+dataset)
    if not os.path.exists(directory+DELIMITER+dataset+".bak"):
        os.mkdir(directory+DELIMITER+dataset+".bak")
    #loop over all the file, has to write the --value_dataset if the picture has the element, else just type enter
    for file in sorted(glob(os.path.join(directory,dataset,"*"))):
        user_annotate = input(file.split(DELIMITER)[-1]+" ")
        if user_annotate ==str(user_args.value_dataset) :
            copyfile(file, directory+DELIMITER+dest_save+DELIMITER+user_annotate+"_"+file.split(DELIMITER)[-1])
        else:
            user_annotate='0'
            if random.randrange(0,100,1)<int(user_args.ratio):
                copyfile(file, directory + DELIMITER+dest_save+DELIMITER + user_annotate + "_" + file.split(DELIMITER)[-1])

        move(file,directory+DELIMITER+dataset+".bak"+DELIMITER+file.split(DELIMITER)[-1])

if __name__ == '__main__':
    main()