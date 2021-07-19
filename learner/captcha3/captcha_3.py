import argparse
import os

import torch.utils.data
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim

from LearningDataset3 import LearningDataset
from train_model import train_model
from config import DELIMITER


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with -- are optional
    dataset_path(required) : Root directory to load dataset for learning. Your annotated pictures must be on a "annotated" sub directory
    --batch_size : Size of the batch, reducing times to check prediction with expected values. Default value 32
    --ratio : The ratio between pictures used for learning and images to do validation. Having a high value can produce overfitting. Default value 75
    --num_workers : Number of logical worker like thread. Can be set upper if you have mutliple GPU. Can produce error on Windows. Default value 0
    --lr : learning rate for the training. Default value 0.001
    --momentum: Momentum use for the training. Default value 0.9
    --num_epochs: Number of epoch to do before finishing training. Default value 25
    --num_classes: Number of classes to train for your model. Every model and datasets given has 2 classes (is or is not target)
    --name : Name of the .pt file to save in trained_model directory

    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Annotated Dataset.')
    parser.add_argument('dataset_path', help="Dataset to load")
    parser.add_argument('--batch_size', dest='batch_size', default=32, type=int,
                        help="size of the batch to load. Can be reduce if your memory is limited. Default 32")
    parser.add_argument("--ratio", dest='ratio', default=75, type=int,
                        help="ratio between number of picture for learning and testing. Default 75")
    parser.add_argument("--num_workers", dest='num_workers', default=0, type=int,
                        help="Can be used to make evolution on multiple GPU. Default 0.")
    parser.add_argument("--lr", dest='lr', default=0.001, type=float,
                        help="Learning rate at the beggining or the learning. Default 0.001 ")
    parser.add_argument("--momentum", dest='momentum', default=0.9, type=float, help="momentum for learning. Default 0.9")
    parser.add_argument("--num_epochs", dest='num_epochs', default=25, type=int, help="Number of epoch during training. Default 25")
    parser.add_argument("--num_classes", dest='num_classes', default=2, type=int,
                        help="Number of class in the dataset. The solver use only 2 classes (has target or not)"
                             "Can be changed to improve learning and modifying model format. Default 2")
    parser.add_argument("--name", dest='name', required=True, help="Name of the trained model")
    args = parser.parse_args()

    return args


def main():
    """
    Learn from use argument with vgg13 model and save the model in a directory named trained_model
    The model can be changed with https://pytorch.org/vision/stable/models.html different model. Use can create your own as well.
    :return:
    """
    user_arguments = manage_parameters()
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    if str(device) =="cpu":
        print("WARNING : you are running on your CPU, it will take much more time to run on cpu instead of cuda. "
              "Please check https://pytorch.org/get-started/locally/")
    transform = transforms.Compose(
        [transforms.ToTensor()])

    batch_size = user_arguments.batch_size
    trainset = LearningDataset(root=user_arguments.dataset_path,
                               transform=transform)
    indices = torch.randperm(len(trainset)).tolist()
    ratio = user_arguments.ratio

    if ratio < 1 or ratio > 99:
        raise Exception("ratio can not be smaller than 1 or bigger than 99")
    dataset = torch.utils.data.Subset(trainset, indices[:int(len(indices) * (ratio / 100))])
    trainloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                              shuffle=True, num_workers=user_arguments.num_workers)

    testset = torch.utils.data.Subset(trainset, indices[int(len(indices) * (ratio / 100)):])
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                             shuffle=False, num_workers=user_arguments.num_workers)

    loaded_model = torchvision.models.vgg13(False, True, num_classes=user_arguments.num_classes)

    loaded_model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(loaded_model.parameters(), lr=user_arguments.lr, momentum=user_arguments.momentum)

    dataloaders_dict = {"train": trainloader, "val": testloader}
    train_model(loaded_model, device, dataloaders_dict, criterion, optimizer, num_epochs=user_arguments.num_epochs)
    if not os.path.exists("trained_model"):
        os.mkdir("trained_model")
    torch.save(loaded_model, "trained_model" + DELIMITER + user_arguments.name + ".pt")


if __name__ == '__main__':
    main()
