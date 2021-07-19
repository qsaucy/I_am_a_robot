import asyncio
import os
import time
import argparse
from config import DELIMITER
from pypeteer_utils import load_page, locate_captcha, click_element, locate_challenge
if not os.path.exists("downloader"):
    os.mkdir("downloader")
ROOT_DIRECTORY = "downloader"+DELIMITER


def manage_parameters():
    """get user input. Some arguments are required and other are optional. Arguments started with -- are optional
    url(required) : website to download captcha. Must have a captcha on the website
    --dest : name of the sub directory in "downloader" to save the downloaded dataset. Default value downloaded_captcha
    --sleeping_time : Time to wait between reloading captcha. If time is too small can produce white picture or google ban . Default value 10
    --threshold : Number of captcha to download if not ban. Default value 100.
    --batch_name : name of the dataset directory in --dest directory. Can produce a warning if the directory already exist. Default dataset

    :return: array with all user input
    """
    parser = argparse.ArgumentParser(description='Annotated Dataset.')
    parser.add_argument('url')
    parser.add_argument('--dest', dest='dest', default="downloaded_captcha", help="directory in downloader directory to save the pictures. Default downloaded_captcha ")
    parser.add_argument("--sleeping_time", dest='sleeping_time',default=10,help="Time in second to wait between each reload. Setting a low period will cause a faster ban from Google."
                                                                                "Having a too small period can cause white captcha. If you have internet issues. Default value 10")
    parser.add_argument("--threshold", dest='threshold',default=100, help="Number of captcha to download. Default 100. Can be stop earlier if google detect you as a bot and ban you IP ")
    parser.add_argument("--batch_name", dest='batch_name',default="dataset", help="directory name for this batch ")
    args = parser.parse_args()

    return args



async def main():
    user_arguments=manage_parameters()

    browser, page = await load_page(user_arguments.url)
    if not os.path.exists(ROOT_DIRECTORY+user_arguments.dest):
        os.mkdir(ROOT_DIRECTORY+user_arguments.dest)
    base_batch_directory =ROOT_DIRECTORY+user_arguments.dest+DELIMITER+user_arguments.batch_name
    if os.path.exists(base_batch_directory):
        user_choice =input("This batch already exist, if you continue, some of your old captcha will be replaced. Continue y [n]")
        if user_choice !="y":
            return -1
    else:
        os.mkdir(base_batch_directory)
    if not os.path.exists(base_batch_directory+DELIMITER+"3_3"):
        os.mkdir(base_batch_directory+DELIMITER+"3_3")
    if not os.path.exists(base_batch_directory+DELIMITER+"4_4"):
        os.mkdir(base_batch_directory+DELIMITER+"4_4")
    frame = await locate_captcha(page, user_arguments.url, "#recaptcha-anchor")
    element_to_click = await frame.querySelector("#recaptcha-anchor")
    await click_element(element_to_click)
    time.sleep(1)
    for i in range(user_arguments.threshold):

        frame = await locate_captcha(page, user_arguments.url, "#recaptcha-verify-button")
        captcha_format, _table, target, to_search = await locate_challenge(frame)
        if captcha_format == 4:
            await target.screenshot({'path': base_batch_directory+DELIMITER+'4_4'+DELIMITER+str(i)+'_'+to_search+'.png'})
        elif captcha_format == 3:
            await target.screenshot({'path': base_batch_directory+DELIMITER+'3_3'+DELIMITER+str(i)+'_'+to_search+'.png'})

        await frame.click("#recaptcha-reload-button")

        time.sleep(int(user_arguments.sleeping_time))
    await browser.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())