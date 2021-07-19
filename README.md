- [I'am a robot ]( #I-am-a-bot )
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
I'am a robot is a bachelor project to help pentesters to automatise web attacks. 
This project targets to solve recaptcha v2 without user interaction. The project use machine learning to solve captcha.

Google use 2 types of captcha. The first use 9 distinct pictures, the second split in 16 part a single picture. The way to solve 
is very different. The first captcha can be split in 9 pictures and trying to know if this has or not the label. 
For the second the model have to draw a mask and identify in which sub picture the mask is.

The following data have been collect between 21.05.21 and 28.05.21. The ratio can change in the futur

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

The pourcentage represent for one splitted image. A captcha is 9 images but sometimes can reload some image. To calculate passing captcha ratio : %<sup>9 or 12</sup>

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



Notice: tests did not show any difference between different website or location from where the script is run.   

## install downloader

The following command will install pypeteer and pypeteer-stealth with their dependances.

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

### example

```
python downloader.py https://www.google.com/recaptcha/api2/demo
```

## improvement downloader

* Download only targeted captcha label
* Continue download after ban
  * Waiting time 
  * Changing IP


# Annotator

## install annotator

## use annotator

## improvement annotator

# Learner

## install learner

## use learner

## improvement learner

# Solver

## install solver

## use solver

## improvement solver

# credits