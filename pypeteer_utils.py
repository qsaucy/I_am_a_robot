import os
import random
from pyppeteer import launch
from pyppeteer_stealth import stealth

from solver.ascii_art_captcha import get_ascci_captcha


async def load_page(url, headed=False):
    """ create a browser show it if headed has True value
    page.goto can raise errors :
        - there's an SSL error (e.g. in case of self-signed certificates)
        - target URL is invalid
        - the ``timeout`` is exceeded during navigation
        - then main resource failed to load
    :param url: url to load
    :param headed: has to show the chromium app
    :return: pypeteer page object and browser to close it at the end
    """
    browser = await launch({"headless": not headed})
    # browser = await launch()
    page = await browser.newPage()

    await stealth(page)  # <-- Here
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en'
    })

    await page.goto(url)
    return browser, page


async def locate_captcha(page, url, id, ascii=False):
    """ Try to find captcha in the page. Captcha is store in iframe, open iframe then check if id id exist.
    This id represent the checkbox recaptcha v2 button
    Can raise error if no captcha found in the page.

    :param page: Pypeteer page object
    :param url:  use to print usefull error
    :param id : identifiant of recaptcha object ( normaly recaptcha anchor or recaptcha verify button)
    :param ascii: if true, print the beginrobot (locate in ascii_art_captcha)
    :return: the frame contains captcha
    """
    captcha_iframe = -1
    for i in range(len(page.frames)):
        frame = page.frames[i]
        if await frame.querySelector(id) is not None:
            captcha_iframe = i
            break
    if ascii:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(get_ascci_captcha("begin", "undefined", "undefined"))
    if captcha_iframe == -1:
        raise Exception("No captcha found on this page : " + url)
    return page.frames[captcha_iframe]


async def locate_challenge(frame):
    """ locate the captcha challenge then return usefull value
    Can raise error if google banned you. Is check if the label can not be found. This can happen if you close the browser too.
    :param frame: pypeteer frame object
    :return: tuple
            - captcha_format if the captcha is a 3x3 (3) or 4x4 (4)
            - table is an array of the html td of the challenge
            - target is an html div to screenshot containing the captcha
            - to_search is the label to search in the challenge
    """
    # if search label is not found, probably has an error when loading challenge
    if await frame.querySelector(".rc-imageselect-instructions strong") is None:
        raise Exception(
            "you are probably banned of recaptcha for too many tries, you can wait some time or change your external IP")
    to_search = await frame.querySelectorEval(".rc-imageselect-instructions strong", 'node => node.innerText')

    size1 = await  frame.querySelector(".rc-image-tile-44")
    target = await frame.querySelector("#rc-imageselect-target")
    captcha_format = 4
    if size1 is None:
        captcha_format = 3

    table = await target.querySelectorAll('tr td')
    return captcha_format, table, target, to_search


async def click_element(element_to_click):
    """ send click event to element_to_click

    :param element_to_click: html element
    :return:
    """
    return await element_to_click.click(options={"delay": random.randint(10, 100)})