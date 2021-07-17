import json

import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

import os
import numpy as np
import torch
import torch.utils.data
from PIL import Image, ImageDraw
from glob import glob


#cityscapes as more label than we are looking for.
to_keep = ['bicycle', 'car', 'truck', 'bus', 'motorcycle', 'traffic light']


class LearningDataset(torch.utils.data.Dataset):
    """
    Based on pytorch tutorial : https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
    Data from cityscape dataset : https://www.cityscapes-dataset.com/
    """
    def __init__(self, root, transforms=None):
        self.root = root
        self.transforms = transforms
        # load all image files, sortinag them to
        self.imgs = list(sorted(glob(os.path.join(root, "pictures", "*"))))
        self.masks = list(sorted(glob(os.path.join(root, "masks", "*.json"))))

    def __getitem__(self, idx):
        # load images ad mask
        img_path = self.imgs[idx]
        mask_path = self.masks[idx]
        img = Image.open(img_path).convert("RGB")
        boxes = []
        labels = []
        with open(mask_path) as f:
            data = json.load(f)
            width = data["imgWidth"]
            height = data["imgHeight"]
            nbr_element = 0
            MyImage = Image.new(mode="L", size=(width, height))
            for json_object in data["objects"]:
                # check if the current mask is a targeted object or not
                if json_object["label"] in to_keep:
                    xmin = width
                    xmax = 0
                    ymin = height
                    ymax = 0
                    pos = []
                    MyDraw = ImageDraw.Draw(MyImage)
                    for polygon in json_object["polygon"]:
                        if polygon[0] < xmin:
                            xmin = polygon[0]
                        if polygon[0] > xmax:
                            xmax = polygon[0]
                        if polygon[1] < ymin:
                            ymin = polygon[1]
                        if polygon[1] > ymax:
                            ymax = polygon[1]
                        # to draw the mask
                        pos.append((polygon[0], polygon[1]))

                    boxes.append([xmin, ymin, xmax, ymax])
                    label_id = to_keep.index(json_object["label"])
                    # draw each mask with the label id
                    nbr_element += 1
                    MyDraw.polygon(pos, fill=f"#{nbr_element:02x}{nbr_element:02x}{nbr_element:02x}")

                    labels.append(label_id)
        iscrowd = torch.zeros((nbr_element,), dtype=torch.int64)

        mask = np.array(MyImage)
        obj_ids = np.unique(mask)
        # first id is the background, so remove it
        obj_ids = obj_ids[1:]

        # split the color-encoded mask into a set
        # of binary masks
        masks = mask == obj_ids[:, None, None]

        masks = torch.as_tensor(masks, dtype=torch.uint8)
        boxes = torch.as_tensor(boxes, dtype=torch.float32)

        labels = torch.as_tensor(labels, dtype=torch.int64)
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

        image_id = torch.tensor([idx])
        target = {}
        target["boxes"] = boxes
        target["masks"] = masks
        target["labels"] = labels
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd
        if self.transforms is not None:
            img, target = self.transforms(img, target)
        return img, target

    def __len__(self):
        return len(self.imgs)




def get_instance_segmentation_model(num_classes):
    # load an instance segmentation model pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

    # get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                       hidden_layer,
                                                       num_classes)

    return model