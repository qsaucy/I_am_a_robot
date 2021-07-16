from solver.ascii_art_captcha import get_ascci_captcha
from solver.predict_captcha import predict_captcha
from config import DELIMITER
import asyncio
import random
import os
import string
from pypeteer_utils import load_page, locate_captcha, locate_challenge, click_element
import time
import argparse
import shutil
import re


def url_format(url_value, pat=re.compile(r"(http[s]?://)?(.*@)?(www\.)?([0-9a-z\-_]+\.)+[a-z]{1,5}(:[0-9]{1,5})?/?.*")):
    """Check if the url has a correct format


    :param url_value:  the url to verify
    :param pat: a regex to verify url
    :return: the url. If url has not http[s] add https at the beginning
    """
    if not pat.match(url_value):
        raise argparse.ArgumentTypeError
    if "http" not in url_value:
        url_value = "https://" + url_value
    return url_value


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with -- are optional
    url(required) : url of the website to solve captcha. This url has to have a captcha
    --form : how to find the form to fill in the page.
        - for a html id, need to add # before idname
        - for a html class, need to add . before classname
        - for the form tag, nothing to add
    --num-form : select the nth form in the page. Default value 0
    --params : form field to fill. If none search required one. If at least one is given, doesn't fill other field, optionnal or required
    --values : fill the --params field with user values. If values is not given or not enough values given, fill randomly
    --ascii  : remove message (type of captcha, google result...) and replace it with ascii art /\ clear terminal /\
    --headed : run in front pypeteer, usally use for debugging
    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Solve Captcha.')
    parser.add_argument('url', type=url_format)
    parser.add_argument("--form", dest='form', help="if the form has an id add # before the idname\n"
                                                    "if has a class add . before the classname\n"
                                                    "else give the name\n"
                                                    "not required but use to provide better attack")
    parser.add_argument('--params', dest='params', nargs="*",
                        help='form parameters(name field) , if none automatically fill required field with random value depending of the type')
    parser.add_argument('--values', dest='values', nargs="*",
                        help='parameters value, if none add random value')
    parser.add_argument('--num_form', dest='num_form', default=0, type=int,
                        help='if the page has multiple forms specify the good one, default value 0')
    parser.add_argument('--ascii', dest='ascii', default=False, action="store_true",
                        help='disable information and print ascii captcha /\\ clear terminal /\\')
    parser.add_argument('--headed', dest='headed', default=False, action="store_true",
                        help='show the program')
    args = parser.parse_args()
    if (args.params is None and args.values is not None) or (
            args.params is not None and args.values is not None and len(args.params) < len(args.values)):
        raise Exception("Too many value for form params")
    return args


async def fill_randomly(element, type, page):
    """ fill html element with correct typed value

    :param element: html to fill
    :param type: Support type of form element :
                - passowrd : write 8 to 15 char between the python printable : 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
                - text  : write 8 to 15 lowercase letter
                - textarea : same as text
                - email : same as text then add @, add 8 to 15 lowercase letter then add . and 2 to 3 lowercase letter
                - tel : write a swiss number like +41 and 9 number
                - select-one : choose first element of the select
    :param page: pypeteer page element for select-one. Because we need to send keyboard input to choose the first element
    :return:
    """
    to_print = ""
    if type == "password":
        text_len = random.randint(8, 15)

        for i in range(text_len):
            to_print += random.choice(string.printable)
    elif type == "email" or type == "text" or type == "textarea":
        text_len = random.randint(8, 15)
        for i in range(text_len):
            to_print += random.choice(string.ascii_lowercase)
        if type == "email":
            to_print += "@"
            for i in range(text_len):
                to_print += random.choice(string.ascii_lowercase)
            to_print += "."
            text_len = random.randint(2, 3)
            for i in range(text_len):
                to_print += random.choice(string.ascii_lowercase)
    if type == "tel":
        to_print += "+41"
        for i in range(9):
            to_print += str(random.randint(0, 9))
    await element.type(to_print)
    if type == "select-one":
        # simulate keyboard, TODO find a better way to select in a select-one
        await element.click()
        await page.waitFor(300)
        await page.keyboard.press('ArrowDown')
        await page.keyboard.press('Enter')

        # cannot give the dom element to select, doesnt work if the select has no id
        # await page.select("#"+await(await element.getProperty("id")).jsonValue() ,"Kurrier" )
    # await element.screenshot({'path': str(random.random())+"here.png"})


async def locate_form(page, form, url, num_form=0):
    """ locate the form to fill
    Can raise error:
        - if no form respect form format are located in the page
        - if trying to select num_form th bigger than number of form respect form format
    :param page: Pypeteer page object
    :param form: how to find the form to fill in the page
    :param url: use to print usefull error
    :param num_form: select the num_formth.
    :return: html form element
    """
    if form is None:
        form = "form"
    forms = await page.querySelectorAll(form)
    if not forms:
        raise Exception("No form with this name " + form + " has been found")
    if len(forms) < num_form:
        raise Exception(
            f"the website {url} has only {len(forms)} forms, can not reach the  {num_form + 1}th forms")
    return forms[num_form]


async def fill_form(page, form, params, values):
    """ fill form with user values or randomly
    Can raise error if an input that user want to fill does not exist
    :param page: Pypeteer page object
    :param form: html form element
    :param params: user name form field
    :param values: user values for field
    :return: None
    """
    toFill = []
    if params is not None:
        for param in params:
            # has form a input named param
            input_value = await form.querySelector(f"input[name=\"{param}\"]")
            if input_value is None:
                # has form a textarea named param
                input_value = await form.querySelector(f"textarea[name=\"{param}\"]")
                if input_value is None:
                    raise Exception(f"cannot find input with name : {param}")
            toFill.append(input_value)
        # fill the first len(values) with user values then randomly
        for i, element in enumerate(toFill):
            if len(values) - 1 < i:
                await fill_randomly(element, await(await element.getProperty("type")).jsonValue(), page)
            else:
                await element.type(values[i])
    else:
        # locate field with required or aria-required
        qsl = await form.querySelectorAll(
            "input[required=true],input[aria-required=true],textarea[required=true],textarea[aria-required=true],select[required=true],select[aria-required=true]")

        for selector in qsl:
            await fill_randomly(selector, await(await selector.getProperty("type")).jsonValue(), page)


async def main():
    user_arguments = manage_parameters()
    browser, page = await load_page(user_arguments.url, headed=user_arguments.headed)
    frame = await locate_captcha(page, user_arguments.url, "#recaptcha-anchor", user_arguments.ascii)
    form = await locate_form(page, user_arguments.form, user_arguments.url, num_form=user_arguments.num_form)
    await fill_form(page, form, user_arguments.params, user_arguments.values)

    element_to_click = await frame.querySelector("#recaptcha-anchor")
    await click_element(element_to_click)

    time.sleep(1)
    frame = await locate_captcha(page, user_arguments.url, "#recaptcha-verify-button", user_arguments.ascii)

    success_after = 0
    # delay the printing ascii_art after locating the verify button, because it show the beginrobot
    if user_arguments.ascii:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(get_ascci_captcha("click", "undefined", "undefined"))
    while True:
        success_after += 1
        time.sleep(1)

        captcha_format, table, target, to_search = await locate_challenge(frame)

        if user_arguments.ascii:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(get_ascci_captcha("challenge", captcha_format, to_search))
        if not user_arguments.ascii:
            print(to_search)
        if not os.path.exists("solver" + DELIMITER + "captcha"):
            os.mkdir("solver" + DELIMITER + "captcha")
        path = f"solver" + DELIMITER + f"captcha" + DELIMITER + f"{captcha_format}{to_search}.png"
        await target.screenshot({'path': path})
        to_select = predict_captcha(path, to_search, captcha_format)
        os.remove(path)
        # select the element that the predict_captcha give
        for i in range(captcha_format ** 2):
            if to_select[i]:
                await click_element(table[i])
                random_time = random.randrange(2, 10, 1) / 10
                time.sleep(random_time)
        # The 3x3 challenge can give some new challenge after the first image
        if captcha_format == 3:
            new_image = True
            already_test = []
            increment = 0
            random_value = random.random()
            nbr_reload_image = 0
            while new_image:
                # wait time to google show new challenge.
                time.sleep(6)
                new_tiles = await frame.querySelectorAll(".rc-image-tile-11")
                new_image = False
                if not os.path.exists("solver" + DELIMITER + "tmp"):
                    os.mkdir("solver" + DELIMITER + "tmp")
                for i, image in enumerate(new_tiles):
                    # check if the tile 1-1 has already been tested,  not possible to check if the ElementHandle equal between different loop, cannot get the src image, using pos in page works
                    if ((await image.boundingBox())["x"], (await image.boundingBox())["y"]) in already_test:
                        continue
                    if os.path.exists("solver" + DELIMITER + "tmp" + DELIMITER + "tile1-1.png"):
                        os.remove("solver" + DELIMITER + "tmp" + DELIMITER + "tile1-1.png")
                    tmpPath = "solver" + DELIMITER + "tmp" + DELIMITER + "tile1-1" + str(random_value) + "_" + str(
                        increment) + ".png"
                    increment += 1
                    # screenshot only the new tile. When project is in the headed mode seems like reloading
                    await image.screenshot({'path': tmpPath})
                    to_select = predict_captcha(tmpPath, to_search, 1)
                    os.remove(tmpPath)
                    # if has already reload 5 times the challenge stop it. Captcha will never be solve after that
                    if True in to_select and nbr_reload_image < 5:
                        await click_element(new_tiles[i])
                        time.sleep(1.5)
                        new_image = True
                    else:
                        already_test.append(((await image.boundingBox())["x"], (await image.boundingBox())["y"]))
                    nbr_reload_image += 1
        # await frame.click("#recaptcha-reload-button")
        verify = await frame.querySelector("#recaptcha-verify-button")
        await click_element(verify)
        time.sleep(1)
        response = await page.querySelectorEval("#g-recaptcha-response", 'node => node.value')
        if response != "":
            if not user_arguments.ascii:

                print("in " + str(success_after) + " captcha")
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(get_ascci_captcha("end"))
                time.sleep(2)
            await browser.close()
            return success_after

        # if the captcha breaker cannot identify any item or has problem, reload a new captcha
        # if the captcha breaker make too many tries, the google api reload automatically
        # node.style return {} if no problem, else return {'0':'display} because the node has "display=none" when everything is correct
        breaker_missed_lot = await frame.querySelectorEval(".rc-imageselect-error-select-more",
                                                           "node=> node.style") == {}
        breaker_dont_find_new_one = await frame.querySelectorEval(".rc-imageselect-error-dynamic-more",
                                                                  "node=> node.style") == {}
        breaker_dont_select_any = await frame.querySelectorEval(".rc-imageselect-error-select-something",
                                                                "node=> node.style") == {}
        time.sleep(1)
        if breaker_missed_lot or breaker_dont_find_new_one or breaker_dont_select_any:
            await frame.click("#recaptcha-reload-button")


try:
    nbr_captcha = asyncio.get_event_loop().run_until_complete(main())
    print(f"solved in {nbr_captcha}")
finally:
    # cleaning tmp directories
    shutil.rmtree("solver" + DELIMITER + "tmp_split")
    shutil.rmtree("solver" + DELIMITER + "tmp")
    shutil.rmtree("solver" + DELIMITER + "captcha")
