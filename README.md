- [I'am a robot ]( #I-am-a-robot )
- [prerequisites]( #prerequisites )
- [Downloader]( #Downloader )
    - [install]( ##install-downloader )
    - [use]( #use-downloader )
    - [improvement]( #improvement-downloader )
- [Annotator]( #Annotator )
    - [install]( #install-annotator )
    - [use]( #use-annotator )
    - [improvement]( #improvement-annotator )
- [Learner]( #Learner )
    - [install]( #install-learner )
    - [use]( ##use-learner )
    - [improvement]( #improvement-learner )
- [Solver]( #Solver )
    - [install](#install-solver )
    - [use]( #use-solver )
    - [improvement](#improvement-solver)
- [Credits]( #Credits )



# I am a robot
I'am a robot is a bachelor project to help pentesters to automatize web attacks. 
This project targets to solve recaptcha v2 without user interaction. The project use machine learning to solve captcha.

Google use 2 types of captcha. The first use 9 distinct pictures, the second split in 16 part a single picture. The way to solve 
is very different. The first captcha can be split in 9 pictures and trying to know if this has or not the label. 
For the second the model have to draw a mask and identify in which sub picture the mask is.

The following data have been collect between 21.05.21 and 28.05.21. The ratio can change in the future

The ratio between 3x3 and 4x4 is not balanced and it is about 70% 3x3 and 30% 4x4.

Google recaptcha challenge ratio are not balanced. Google use about 15 different labels in both type of captcha but not in the same distribution.

The five most used labels for the 3x3 recaptcha represent 99.2 % of whole 3x3 captchas.

| Label        | %     |
| ------------ | ----- |
| Bus          | 28.09 |
| Crosswalk    | 21.05 |
| Fire hydrant | 18.13 |
| Bicycle      | 16.54 |
| Car          | 15.42 |

Recaptcha 4x4 has two main labels represent 67.69 %.

| Label         | %     |
| ------------- | ----- |
| Traffic light | 47.02 |
| Crosswalk     | 20.67 |
| Bicycle       | 6.26  |
| Bus           | 6.02  |
| Fire hydrant  | 5.55  |
| Motorbike     | 4.13  |

I'am a robot already have multiple model to identify different labels:

* Captcha 3x3

  All datasets have been manually  annotated from splitted captcha

  * Bus 82.39% : [bus_shufflenet_v2_x0_5.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/bus_shufflenet_v2_x0_5.pt) 
  * Crosswalk 89.37%: [crosswalk_shufflenet_v2_x0_5.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/crosswalk_shufflenet_v2_x0_5.pt)
  * Fire hydrant 95.04% : [fire_hydrant_shufflenet_v2_x0_5.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/fire_hydrant_shufflenet_v2_x0_5.pt)
  * Bicycle 83.38% : [bicycle_shufflenet_v2_x0_5.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/bicycle_shufflenet_v2_x0_5.pt)          
  * Car 78.93%: [car_shufflenet_v2_x0_5.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/car_shufflenet_v2_x0_5.pt)

The percentage represent for one splitted image. A captcha is 9 images but sometimes can reload some image. To calculate passing captcha ratio : %<sup>9 or 12</sup>

* Captcha 4x4 has two model based on the same dataset
  * [cityscape_25_model.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/cityscape_25_model.pt)
  * [cityscape_work_well.pt](https://github.com/qsaucy/I_am_a_robot/blob/readme/solver/model/cityscape_work_well.pt)          

# prerequisites

* Python, pip
* Cityscapes for *learning step*
* Datasets for *learning step* ( if not created before)
* cuda setup installation for *learning step* and *solver step*

# Downloader

This part of the program can download google recaptcha from website you want. This can be use to improve dataset by adding new pictures.



Captcha will be save in 4_4 or 3_3 folder. The file will be name as : *i_labelOfCaptcha.png* Where *i* is the iteration value and *labelOfCaptcha* the label of the captcha  



Notice: tests did not show any difference between different website or location from where the script is run.   

## install downloader

The following command will install pypeteer and pypeteer-stealth with their dependences.

run `pip install -r requirement/downloader_requirements.txt`



## use downloader

```python
downloader.py [-h] [--dest DEST] [--sleeping_time SLEEPING_TIME] [--threshold THRESHOLD] [--batch_name BATCH_NAME] url

```

* url: the url from where you want download captcha, must have a captcha on it
* --dest: the location to save you captcha, in downloader directory.  Default : downloaded_captcha
* --sleeping_time : time to wait between reloading captcha in second . If the value is too small can produce white picture, Google can ban your because your are detecting as a bot. Default : 10
* --threshold : Number of captcha to download, if you are not banned before. Default 100
* --batch_name : The name for saving batch in --dest directoy. You will have a warning if the batch already exist. Default dataset



## improvement downloader

* Download only targeted captcha label
* Continue download after ban
  * Waiting time 
  * Changing IP
  * Check user argument ( negative sleeping_time, etc)

# Annotator

This part of the project is use to create dataset. Currently, the project allow to annotate only 3x3 captcha. Models at the moment are use for only one label. This choice has been made for helping learning. When a model has a good score, it is kept and he does not to have good score for every labels.

## install annotator

The following command will install pillow package

run ``pip install -r requirement/annotator_requirements.txt `



## use annotator

Annotator has 2 parts located in annotator directory. 

* copy_captcha_with_condition is a utils command to copy file from download step and split it to get ready for annotating phase. Pictures will be store splitted and unsplitted to check if the script works. Will ignore folder 4_4 to keep only 3x3 captcha. Picture will be rename with random lowercase string.

  ```python
  copy_captcha_with_condition.py [-h] [--captcha_format CAPTCHA_FORMAT] --dest DEST [--dir DIR] --src SRC --target TARGET
  ```

  * --captcha_format : Number of column and line to split. Default 3
  * --dest : Directory to store unsplitted picture
  * --dir : Directory to store splitted picture. Default dataset
  * --src : Source directory to copy file to dir
  *  --target : Captcha to copy, label you want

* annotate: is the script to create dataset. The value annotated will be store in the picture filename. The first character is the class. The script will show a file name ( the first present in the dataset directory) and will wait for a value. You have to open the image or see it in the folder and if the picture has the target label enter the *value_dataset* else just type enter.

  ```
  annotate.py [-h] [--dest_save DEST_SAVE] [--value_dataset VALUE_DATASET] [--ratio RATIO] [--src_dataset DATASET] dataset_path
  ```

  * dataset_path: root directory of the dataset
  * --dest_save : directory to save annotated dataset in dataset_path
  * --value_dataset: Value to set to elements represent your target. default 1. Currently use values:
    * crosswalk : 1
    * fire_hydrant : 3
    * bus : 4
    * car : 5
    * bicycle : 6
  * --ratio : Ratio to keep image that not contain your target. recaptcha 3x3 has usually 3 pictures with label and 6 without. Default 50
  * --src_dataset : Dataset name, same as --dir for *copy_captcha_with_condition*. Default dataset

## improvement annotator

* Add question if user want to see picture ( currently not possible because of loosing focus when opening a picture)
* Change the value to annotate dataset, replace it with a understandable value
* Checking user_arguments 

# Learner

This part of the project as for objective to improve the different model. Currently the project has 2 learning ways.  Both use pytorch vision.

## install learner

The following command will install the base to do learning, but to improve performance, it is recommended to install pytorch in this way :

https://pytorch.org/get-started/locally/

Then you can run

*  captcha 3x3 

  * `pip install -r requirement/learner_captcha_3_requirements.txt`
  * You can manually build your dataset from [Downloader]( #Downloader ) and [Annotator]( #Annotator ) or a dataset already annotated can be downloaded at [captcha3 drive dataset](https://drive.google.com/drive/folders/1LSoEtU8nfA_Rdp71P09g7_iCG6X-puV4?usp=sharing)

  

* captcha 4x4 : `pip install -r requirement/learner_captcha_4_requirements.txt`

  * The dataset use is the [Cityscapes dataset](https://www.cityscapes-dataset.com/) with little modification like deleting pictures without any label in captcha. The modified dataset and their corresponding mask can be found at:[captcha4 drive dataset](https://drive.google.com/drive/folders/1EOGYfffct7kMwMdDgjy2heed7Xpf1K1X?usp=sharing) (unzip  6.6Go )

  The directory tree must be 

  ```
  root_directory
  └───pictures
  │   │.png
  │   
  └───masks
  │   |.json
  ```

  

## use learner

Captcha 3 command located at learner/captcha3 folder:

```
captcha_3.py [-h] [--batch_size BATCH_SIZE] [--ratio RATIO] [--num_workers NUM_WORKERS] [--lr LR]
                    [--momentum MOMENTUM] [--num_epochs NUM_EPOCHS] [--num_classes NUM_CLASSES] --name NAME
                    dataset_path
```

* dataset_path : Path to the dataset you create or download

* --batch_size: The size of the batch to do learning. Can be reduce if you have not enough memory. Default 32
* --ratio : How to divide the dataset between picture use for learning and picture to keep for testing. Default 75. The value represent percentage of picture for learning
* --num_workers : Can be used to make evolution on multiple GPU. Default 0
* --lr : Learning rate at the beginning of the learning. Default 0.001
* --momentum : momentum use for the learning. Default 0.9
* --num_epochs : Number of epoch before ending learning. Default 25
* --num_classes : Number of classes to identify in the dataset. Should be the same as the annotated dataset. Data should be name of class_filename where class start at 0 and increment by 1 for each different class. If using given dataset the value should **not** be changed. If using other dataset can be changed. Default 2 
* --name : Filename for the dataset without extension. The filename will finish with .pt

Captcha 4 command located at learner/captcha4 folder:

```
captcha_4.py [-h] [--batch_size BATCH_SIZE] [--ratio RATIO] [--num_workers NUM_WORKERS] [--lr LR] [--momentum MOMENTUM] [--num_epochs NUM_EPOCHS] [--weight_decay WEIGHT_DECAY] [--step_size STEP_SIZE] [--gamma GAMMA] --name
                    NAME
                    dataset_path

```

* dataset_path : Path to the dataset you create or download

* --batch_size: The size of the batch to do learning. Can be reduce if you have not enough memory. Default 2
* --ratio : How to divide the dataset between picture use for learning and picture to keep for testing. Default 75. The value represent percentage of picture for learning
* --num_workers : Can be used to make evolution on multiple GPU. Default 0
* --lr : Learning rate at the beginning of the learning. Default 0.001
* --momentum : momentum use for the learning. Default 0.9
* --num_epochs : Number of epoch before ending learning. Default 25
* --weight_decay : Weight decay adds a penalty term to the error function. Default 0.0005
* --step_size : Number of epoch to wait to reduce learning rate. Default 3
* -- gamma : Factor to reduce learning rate. Default 0.1
* --name : Filename for the dataset without extension. The filename will finish with .pt

## improvement learner

# Solver

## install solver

## use solver

## improvement solver

# credits

M. Cordts, M. Omran, S. Ramos, T. Rehfeld, M. Enzweiler, R. Benenson, U. Franke, S. Roth, and B. Schiele, “The Cityscapes Dataset for Semantic  Urban Scene Understanding,” in *Proc. of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*,  2016