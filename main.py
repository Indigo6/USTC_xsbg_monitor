# encoding: utf-8
import json
import ssl
import sys
import time
import datetime
import traceback

import requests
import urllib3
from bs4 import BeautifulSoup
from random import uniform
from lib.login import login_platform
from lib.mail import send_email
from lib.session import MySession
from lib.utils import create_logger, parse_args
from lib.urls import *


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/77.0.3865.75 Safari/537.36',
    "Host": "yjs.ustc.edu.cn"
}


def check_selected(tried_speech_name):
    selected_table = s.get(speech_private_asp)
    selected_table = BeautifulSoup(selected_table.text, 'lxml')
    selected_speeches = selected_table.find_all('tr', class_="bt06")
    selected_names = set()
    for selected_speech in selected_speeches:
        selected_name = selected_speech.contents[5].contents[1].contents[0].strip()
        if selected_name in selected_names:
            continue
        selected_names.add(selected_name)
    if tried_speech_name in selected_names:
        return True
    return False


def speech_filter(speech, selected_names):
    speech_name = speech.contents[5].contents[1].contents[0].strip()
    speech_time = speech.contents[15].contents[0]
    speech_year = int(speech_time.split('年')[0])
    speech_month = int(speech_time.split('年')[1].split('月')[0])
    speech_day = int(speech_time.split('年')[1].split('月')[1].split('日')[0])
    speech_datetime = datetime.datetime(speech_year, speech_month, speech_day)
    now = datetime.datetime.now()
    if speech_datetime < now:
        logger.info("无需选课(已过期): " + speech_name)
        return "end"    # reach date end of valid speeches

    if speech_name in selected_names:
        logger.info("无需选课(已选): " + speech_name)
    elif "计算机学院研究生学术论坛系列" not in speech_name \
            and "研究生高水平学术报告系列" not in speech_name:
        logger.info("无需选课(无学分): " + speech_name)
    else:
        return "need"    # need selection
    return "no need"


if __name__ == "__main__":
    args = parse_args()
    logger = create_logger('log/speech.log')

    # read the configuration in the json file
    logger.info("Loading configurations...")
    with open(args.cfg, encoding='utf-8') as f:
        js = json.load(f)
    userid = js['userid']
    userpwd = js['userpwd']
    order_flag = js['enable.order']

    mail_server = js['mail_server']
    mail_address = js["mail_address"]
    mail_passwd = js["mail_passwd"]

    # create session
    logger.info("Logging in...")
    s = MySession()
    s.headers.update(default_headers)
    login_platform(s, yjs_login_asp, yjs_check_code_asp, userid, userpwd)

    while True:
        try:
            speech_private_table = s.get(speech_private_asp)
            private_soup = BeautifulSoup(speech_private_table.text, 'lxml')
            private_speeches = private_soup.find_all('tr', class_="bt06")

            private_names = set()
            now_time = time.asctime( time.localtime(time.time()) )
            logger.info("\n\n\n****** {} ******".format(now_time))
            failed_num = 0
            succeed_num = 0
            doing_num = 0
            for private_speech in private_speeches:
                private_name = private_speech.contents[5].contents[1].contents[0].strip()
                if private_name in private_names:
                    continue
                private_names.add(private_name)
                if private_speech.contents[19].contents[0] == "不通过":
                    failed_num += 1
                elif private_speech.contents[19].contents[0] == "通过":
                    succeed_num += 1
                else:
                    doing_num += 1
            logger.info("已选 {} 次学术报告, {} 次通过, {} 次未批改, {} 次不通过".format(len(private_names),
                                                                       succeed_num, doing_num, failed_num))
            if succeed_num >= 15:
                logger.info("\n\n!!!!!!已选满 15 次学术报告, 可以去申请获得学分, 别搁着玩了!!!!!!")
                sys.exit()

            # get speech table
            for page_idx in range(1, 3):
                speech_global_url = speech_global_asp.format(page_idx)
                speech_global_table = s.get(speech_global_url)
                global_soup = BeautifulSoup(speech_global_table.text, 'lxml')
                global_speeches = global_soup.find_all('tr', class_="bt06")
                filter_result = 0
                for global_speech in global_speeches:
                    global_speech_name = global_speech.contents[5].contents[1].contents[0].strip()
                    filter_result = speech_filter(global_speech, private_names)
                    if filter_result == "no need":      # no need for selection
                        continue
                    elif filter_result == "end":    # reach date end of valid speeches
                        break
                    logger.info("!*** 需要选课: {} ***!".format(global_speech_name))
                    send_email("!*** 需要选课: {} ***!".format(global_speech_name),
                               mail_server, mail_address, mail_passwd)

                    select_form = {"selectxh": str(global_speech.contents[3].contents[0]),
                                   "select": "true"}
                    select_response = s.post(speech_global_asp, select_form).status_code
                    # unselect_form = {"xuhao": str(global_speech.contents[3].contents[0]),
                    #                  "tuixuan": "true"}
                    # unselect_response = s.post(speech_private_asp, unselect_form).status_code
                    if select_response == 200 and check_selected(global_speech_name):
                        send_email("*** O(∩_∩)O~~ 选上报告: {} ***!".format(global_speech_name),
                                   mail_server, mail_address, mail_passwd)
                if filter_result == "end":  # reach date end of valid speeches
                    break
            random_sleep = uniform(120, 180)
            time.sleep(random_sleep)
        except KeyboardInterrupt:
            sys.exit()
        except requests.exceptions.SSLError or ssl.SSLEOFError or urllib3.exceptions.MaxRetryError:
            traceback.print_exc()
            login_platform(s, yjs_login_asp, yjs_check_code_asp, userid, userpwd)
            continue
        else:
            traceback.print_exc()
            login_platform(s, yjs_login_asp, yjs_check_code_asp, userid, userpwd)
            continue
