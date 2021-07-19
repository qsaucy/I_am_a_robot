import argparse
import os

import torch.utils.data
from LearningDataset4 import LearningDataset, get_instance_segmentation_model
from config import DELIMITER

from lib import transforms as T, utils
from lib.engine import train_one_epoch, evaluate

def get_transform():
    transforms = []
    transforms.append(T.ToTensor())
    return T.Compose(transforms)


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with -- are optional
    dataset_path(required) : Root directory to load dataset for learning. Your annotated pictures must be on a "annotated" sub directory
    --batch_size : Size of the batch, reducing times to check prediction with expected values. Default value 2
    --ratio : The ratio between pictures used for learning and images to do validation. Having a high value can produce overfitting. Default value 75
    --num_workers : Number of logical worker like thread. Can be set upper if you have mutliple GPU. Can produce error on Windows. Default value 0
    --lr : learning rate for the training. Default value 0.001
    --momentum: Momentum use for the training. Default value 0.9
    --num_epochs: Number of epoch to do before finishing training. Default value 25
    --weight_decay: Weight decay adds a penalty term to the error function. Default 0.0005
    --gamma : factor to reduce the learning rate after step_size epochs. Default 0.1
    --step_size: Number of epoch to wait between learning rate reduction
    --name : Name of the .pt file to save in trained_model directory

    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Annotated Dataset.')
    parser.add_argument('dataset_path', help="Dataset to load")
    parser.add_argument('--batch_size', dest='batch_size', default=2, type=int,
                        help="size of the batch to load. Can be reduce if your memory is limited. Default 2")
    parser.add_argument("--ratio", dest='ratio', default=75, type=int,
                        help="ratio between number of picture for learning and testing. Default 25")
    parser.add_argument("--num_workers", dest='num_workers', default=0, type=int,
                        help="Can be used for doing evolution on multiple GPU. Default 0")
    parser.add_argument("--lr", dest='lr', default=0.001, type=float,
                        help="Learning rate at the beggining or the learning. Default 0.0001 ")
    parser.add_argument("--momentum", dest='momentum', default=0.9, type=float, help="momentum for learning. Default 0.9")
    parser.add_argument("--num_epochs", dest='num_epochs', default=10, type=int, help="Number of epoch during training. Default 10")
    parser.add_argument("--weight_decay",dest='weight_decay',default=0.0005,type=float,help="Weight decay adds a penalty term to the error function. Default 0.0005")
    parser.add_argument("--step_size",dest='step_size',default=3,type=int,help="number of epoch to wait to reduce learning rate. Default 3")
    parser.add_argument("--gamma",dest='gamma',default=0.1,type=float,help="factor to reduce learning rate. Default 0.1")
    parser.add_argument("--name", dest='name', required=True, help="Name of the trained model")
    args = parser.parse_args()

    return args


def main():
    user_arguments=manage_parameters()
    full_dataset = LearningDataset(user_arguments.dataset_path, get_transform())
    indices = torch.randperm(len(full_dataset)).tolist()
    ratio = user_arguments.ratio
    batch_size = user_arguments.batch_size
    if ratio < 1 or ratio > 99:
        raise Exception("ratio can not be smaller than 1 or bigger than 99")
    dataset = torch.utils.data.Subset(full_dataset, indices[int(len(indices) * (ratio / 100)):])
    dataset_test = torch.utils.data.Subset(full_dataset, indices[int(len(indices) * (ratio / 100)):int(len(indices) * (ratio / 100))+100])
    print(len( indices[int(len(indices) * (ratio / 100)):int(len(indices) * (ratio / 100))+100]))
    # define training and validation data loaders
    data_loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=True, num_workers=user_arguments.num_workers,
        collate_fn=utils.collate_fn)
    data_loader_test = torch.utils.data.DataLoader(
        dataset_test, batch_size=1, shuffle=False, num_workers=user_arguments.num_workers,
        collate_fn=utils.collate_fn)
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    if str(device) =="cpu":
        print("WARNING : you are running on your CPU, it will take much more time to run on cpu instead of cuda. "
              "Please check https://pytorch.org/get-started/locally/")

    #to_keep value and none
    num_classes = 7

    # get the model using our helper function
    model = get_instance_segmentation_model(num_classes)
    # move model to the right device
    model.to(device)

    # construct an optimizer
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=user_arguments.lr,
                                momentum=user_arguments.momentum, weight_decay=user_arguments.weight_decay)

    # and a learning rate scheduler which decreases the learning rate by
    # 1/gamma every step epochs
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                   step_size=user_arguments.step_size,
                                                   gamma=user_arguments.gamma)
    # let's train it for 10 epochs
    num_epochs = user_arguments.num_epochs
    for epoch in range(num_epochs):
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        # update the learning rate
        lr_scheduler.step()
        # evaluate on the test dataset
        evaluate(model, data_loader_test, device=device)
    if not os.path.exists("trained_model"):
        os.mkdir("trained_model")
    torch.save(model, "trained_model" + DELIMITER + user_arguments.name + ".pt")


if __name__ == '__main__':
    main()