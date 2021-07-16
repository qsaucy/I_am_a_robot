import argparse
import os
import random
import string
from glob import glob
from PIL import Image
from shutil import copyfile
from config import DELIMITER


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with
    captcha_format : number of column and line to split. Default value 3
    --dest  : absolute destination directory to store unsplitted captcha. Create a rawfile directory in it
    --dir : destination directory to store splitted captcha in dest directory.
    --src : Source directory to copy file.
    --target : label name to move
    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Copy file and split picture for annote picture.')
    parser.add_argument('--captcha_format', default=3,dest='captcha_format',help="Format to split picture. Captcha 4x4 has only"
                                                                                  "one picture in it. Do not split it ")
    parser.add_argument("--dest", dest='dest', required=True,help="directory to store unsplitted picture ")
    parser.add_argument("--dir", dest='dir', default="dataset", help="Directory to store the splitted image")
    parser.add_argument("--src", dest='src', required=True, help="Source to Directory to store the splitted image")
    parser.add_argument("--target", dest='target', required=True, help="Target to move and split. Ignore picture without target in the filename")
    args = parser.parse_args()

    return args


def copy_with_condition(root,dest,condition):
    """recursive function to copy png picture from root and subdirectories to dest directory. Only images with condition
    in filename are copied. Copied file will have a 30 long lowercase name
    Ignore 4_4 directory
    :param root: base directory
    :param dest: destination directory
    :param condition: condition to copied file. Basically it is the label name
    :return: None
    """

    if root.split(DELIMITER)[-1] =="4_4" or root.split("\\")[-1]=="node_modules":
        return
    for file in sorted(glob(os.path.join(root, "*"))):
        print(file)
        if os.path.isdir(file):
            copy_with_condition(file,dest,condition)
        elif condition in file.split(DELIMITER)[-1] :
            result_str = ''.join(random.choice(string.ascii_lowercase) for i in range(30))
            copyfile(file,dest+DELIMITER+result_str+".png")


def split_image(captcha_format,dest,dir_name):
    """
    Split all images in dest directory to captcha_format ^2 image.
    :param captcha_format: number^2 of subimage to create
    :param dest: base destination directory
    :param dir_name: directory to store splitted image
    :return: None
    """
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    for file in glob(os.path.join(dest + DELIMITER+"rawFile", "*")):
        img = Image.open(file).convert("RGB")
        width, height = img.size
        for line in range(captcha_format):
            y = height // captcha_format
            for col in range(captcha_format):
                x = width // captcha_format
                box = (col * x, line * y, col * x + x, line * y + y)
                cropped_img = img.crop(box)
                cropped_img.save(
                    dest + DELIMITER+dir_name+DELIMITER + file.split(DELIMITER)[-1].split(".")[0] + str(line * captcha_format + col) + ".png")


def prepare_picture():
    """

    :return:
    """
    user_args=manage_parameters()
    if not os.path.exists(user_args.dest):
        os.mkdir(user_args.dest)
    if not os.path.exists(user_args.dest + DELIMITER + "rawFile"):
        os.mkdir(user_args.dest + DELIMITER + "rawFile")
    if not os.path.exists(user_args.dest + DELIMITER + user_args.dir):
        os.mkdir(user_args.dest + DELIMITER + user_args.dir)

    copy_with_condition(user_args.src,user_args.dest+r"\rawFile","car")

    split_image(captcha_format=user_args.captcha_format,dest=user_args.dest,dir_name=user_args.dir)


if __name__ == '__main__':
    prepare_picture()
