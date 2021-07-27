import time
import os
beginrobot = r'''





┌------------------------------------------------┐
|                                                | 
|                                        _       |
|     ┌---┐                            |   |     |
|     |   |    am I a robot ?            —\      |
|     └---┘                             ┌---     |
|                                       └--┐     |
|                                       ---┘     |
|                                                |
└------------------------------------------------┘
'''
clickedrobot = r'''





┌------------------------------------------------┐
|                                                | 
|                                        _       |
|     ╔═══╗                            |   |     |
|     ║   ║    am I a robot ?            —\      |
|     ╚═══╝                             ┌---     |
|                                       └--┐     |
|                                       ---┘     |
|                                                |
└------------------------------------------------┘
'''
def challenge(format,to_print):
    if format==4:

        return f''' 
             ┌----------------------------------------------┐
             |                                              |
             |   {to_print.ljust(20)}                       |
             |                                              |
             ├-----------┬-----------┬-----------┬----------┤
┌------------|           |           |           |          |
|            |           |           |           |          |    
|            |-----------┼-----------┼-----------┼----------|
|     ╔═══╗ /            |           |           |          |
|     ║   ║<             |           |           |          |
|     ╚═══╝ \  ----------┼-----------┼-----------┼----------|
|            |           |           |           |          |
|            |           |           |           |          |
|            | ----------┼-----------┼-----------┼----------|
└------------|           |           |           |          |
             |           |           |           |          |
             └-----------┴-----------┴-----------┴----------┘
'''
    else:
        return  f''' 
             ┌----------------------------------------------┐
             |                                              |
             |   {to_print.ljust(20)}                       |
             |                                              |
             ├--------------┬---------------┬---------------┤
┌------------|              |               |               |
|            |              |               |               |    
|            |              |               |               |
|     ╔═══╗ /├ -------------┼---------------┼---------------|
|     ║   ║< |              |               |               |
|     ╚═══╝ \|              |               |               |
|            |              |               |               |
|            | -------------┼---------------┼---------------|
|            |              |               |               |
└------------|              |               |               |
             |              |               |               |       
             └--------------┴---------------┴---------------┘
'''
endrobot = r'''





┌------------------------------------------------┐
|                                                | 
|                                        _       |
|     ┌---┐                            |   |     |
|     | √ |    I am a robot              —\      |
|     └---┘                             ┌---     |
|                                       └--┐     |
|                                       ---┘     |
|                                                |
└------------------------------------------------┘
'''
def get_ascci_captcha(step, size=3, to_search="car"):
    os.system('cls' if os.name == 'nt' else 'clear')
    if step=="begin":
        return  beginrobot
    elif step =="click":
        return clickedrobot
    elif step=="challenge":
        return challenge(size,to_search)
    else:
        return endrobot