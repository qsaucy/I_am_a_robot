import os

import torch
import torch.nn as nn
import torch.utils.data

from PIL import Image
import torchvision.transforms as transforms
import numpy as np
from glob import glob

from config import DELIMITER
from .configure_model import DEFAULT_MODEL, DEFAULT_MODEL_KNOWNLEDGE, SPECIFIC_MODEL
#create the tmp directory if not exist
storage_tmp_captcha = "solver"+DELIMITER+"tmp_split"
if not os.path.exists(storage_tmp_captcha):
    os.mkdir(storage_tmp_captcha)
# defined on which device the model will run cpu or gpu(cuda)
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
# a transform to create tensor from value
transform = transforms.Compose(
    [transforms.ToTensor()])


def select_model(to_search, captcha_format):
    """Select the good model for specific target

    :param to_search: target to solve
    :param captcha_format: is a 3x3 or 4x4 captcha
    :return: model name to use
    """
    if captcha_format != 4 and to_search in SPECIFIC_MODEL:
        return SPECIFIC_MODEL[to_search]
    return DEFAULT_MODEL


def get_box(nbr_col, height, width):
    """ get pil box to crop in nbr_col^2 boxes

    :param nbr_col: nbr of line and column
    :param height: height of the image
    :param width: width of the image
    :return: an array contaning 4 positions that represent the square of the box
    """
    boxes = []
    for line in range(nbr_col):
        y = height // nbr_col
        for col in range(nbr_col):
            x = width // nbr_col
            boxes.append((col * x, line * y, col * x + x, line * y + y))
    return boxes


def split_image(nbr_col, src, dest):
    """ Take an image path split it to nbr_col ^2 save at dest folder
        Open the image with PIL and use crop function
        Can not defined number of rows and column to split. Only in nbr_col length array
    :param nbr_col: number of column and rows to split
    :param src: path of the source image
    :param dest: path of the destination folder
    :return: None
    """
    img = Image.open(src).convert("RGB")
    width, height = img.size
    boxes = get_box(nbr_col, height, width)
    for i, box in enumerate(boxes):
        cropped_img = img.crop(box)
        cropped_img.save(
            dest + DELIMITER + src.split(DELIMITER)[-1].split(".")[0] + str(i) + ".png")


def predict_captcha(img, to_search, captcha_format):
    # Google recaptcha use multiple labels for the same idea.
    map_location = device
    if to_search == "cars":
        to_search = "car"
    if to_search == "crosswalks":
        to_search = "crosswalk"
    if to_search == "buses":
        to_search = "bus"
    if to_search == "traffic lights":
        to_search = "traffic light"
    if to_search == "bicycles":
        to_search = "bicycle"
    if to_search == "motorcycles":
        to_search = "motorcycle"
    model_name = select_model(to_search, captcha_format)
    model_name = os.getcwd()+model_name
    model = torch.load(model_name, map_location=map_location)
    to_select = []
    if model_name.split(DELIMITER)[-1] == DEFAULT_MODEL.split(DELIMITER)[-1]:

        if to_search not in DEFAULT_MODEL_KNOWNLEDGE:
            return [False] * 16
        if to_search == "vehicles":
            to_search = ["car", "truck", "bus", "motorcycle", "bicycle"]
        img = Image.open(img).convert("RGB")

        img = transform(img)
        img = np.reshape(img, (1, img.shape[0], img.shape[1], img.shape[2]))
        with torch.no_grad():
            prediction = model([img[0].to(device)])
            if len(prediction) == 0 or len(prediction[0]["masks"].cpu().numpy()) == 0:
                return [False]
            predict = prediction[0]["masks"].cpu().numpy()
            # predict is an array of multiple mask, to print every mask on only one image we add the mask value then multiply by 255
            # (if greater than 255 pil will store 255)
            first_mask = predict[0] * 0
            for i, mask in enumerate(predict):
                if DEFAULT_MODEL_KNOWNLEDGE[prediction[0]["labels"][i]] in to_search:
                    first_mask = first_mask + mask
            boxes = get_box(captcha_format, first_mask.shape[2], first_mask.shape[1])
            for box in boxes:
                # use pillow image to crop squared image then reconvert to ndarray
                to_select.append((np.asarray(Image.fromarray((first_mask * 255)[0]).crop(box)) != 0).any())

    else:
        split_image(captcha_format, img, storage_tmp_captcha)
        for i, file in enumerate(glob(os.path.join(storage_tmp_captcha, "*"))):
            img = Image.open(file).convert("RGB")

            #add one dimension to have same format as model
            img = transform(img)
            img = np.reshape(img, (1, img.shape[0], img.shape[1], img.shape[2]))
            if str(device) == "cuda":
                img = img.to(device)
            outputs = model(img.to(device))
            # use softmax to calculate the confidence score
            sm = nn.Softmax(dim=1)
            outputs = sm(outputs)
            _, predictions = torch.max(outputs, 1)
            # if the model doesn't detect the element(or identify a better one) or if the confidence score is lower than 0.7
            if predictions[0].cpu().numpy() == 0 or outputs[0].detach().cpu().numpy()[1] < 0.7:
                to_select.append(False)
            else:

                to_select.append(True)

            os.remove(file)
    return to_select
