import os

import torch
import torch.utils.data
from config import DELIMITER
from glob import glob
from PIL import Image


class LearningDataset(torch.utils.data.Dataset):
    def __init__(self, root, transform=None):
        self.root = root
        self.transform = transform

        # load all image files, sortinag them to
        # ensure that they are aligned
        # self.imgs = list(sorted(glob(os.path.join(root, "img/leftImg8bit/train",city,"interesting","*"))))
        self.imgs = list(glob(os.path.join(root, "annotated", "*")))
        self.classes = [int(i.split(DELIMITER)[-1].split("_")[0][0]) for i in self.imgs]
        # self.masks = list(sorted(glob(os.path.join(root,"gtFine_trainvaltest/gtFine/train",city,"interesting","*.json"))))

    def __getitem__(self, idx):
        # load images ad mask
        img_path = self.imgs[idx]
        target = 1
        if self.classes[idx] == 0:
            target = 0
        img = Image.open(img_path).convert("RGB")
        # img=img_output.convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        return img, torch.tensor(target)

    def __len__(self):
        return len(self.imgs)