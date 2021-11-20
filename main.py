# encoding: utf-8
import json
import sys
import time
import traceback

from bs4 import BeautifulSoup
from random import uniform
from lib.check_code import Checkcode
from lib.mail import send_email
from lib.session import MySession
from lib.utils import create_logger, parse_args

login_asp = "https://yjs.ustc.edu.cn/default_yjsy.asp"
check_code_asp = 'https://yjs.ustc.edu.cn/checkcode.asp'

speech_asp = "http://yjs.ustc.edu.cn/bgzy/m_bgxk.asp"
speech_global_asp = "https://yjs.ustc.edu.cn/bgzy/m_bgxk_up.asp"
speech_private_asp = "https://yjs.ustc.edu.cn/bgzy/m_bgxk_down.asp"
page_suffix = "?querytype=kc&amp;page=2"

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/77.0.3865.75 Safari/537.36',
    "Host": "yjs.ustc.edu.cn"
}


def login(s):
    # get check code
    login_txt = s.get(login_asp).text
    img = s.get(check_code_asp).content
    with open('check_code.png', 'wb') as f:
        f.write(img)
    check_code = Checkcode()
    print("check code: " + check_code)

    # login
    login_dict = {
        'userid': userid,
        'userpwd': userpwd,
        'txt_check': check_code
    }
    login_result = s.post(login_asp, data=login_dict)
    login_status_code = login_result.status_code
    if login_status_code == 200:
        print("Login succeed!")


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
    login(s)

    while True:
        try:
            # get speech table
            speech_global_table = s.get(speech_global_asp)
            global_soup = BeautifulSoup(speech_global_table.text, 'lxml')
            global_speeches = global_soup.find_all('tr', class_="bt06")

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

            for global_speech in global_speeches:
                global_speech_name = global_speech.contents[5].contents[1].contents[0].strip()
                if global_speech_name in private_names:
                    logger.info("无需选课(已选): " + global_speech_name)
                    continue
                elif "计算机学院研究生学术论坛系列" not in global_speech_name and \
                     "研究生高水平学术报告" not in global_speech_name:
                    logger.info("无需选课(无学分): " + global_speech_name)
                    continue
                logger.info("!*** 需要选课: {} ***!".format(global_speech_name))
                send_email("!*** 需要选课: {} ***!".format(global_speech_name), mail_server, mail_address, mail_passwd)

                select_form = {"selectxh": str(global_speech.contents[3].contents[0]),
                               "select": "true"}
                select_response = s.post(speech_global_asp, select_form).status_code
                if select_response == 200 and check_selected(global_speech_name):
                    send_email("*** O(∩_∩)O~~ 选上报告: {} ***!".format(global_speech_name), mail_server, mail_address, mail_passwd)
            random_sleep = uniform(120, 180)
            time.sleep(random_sleep)
        except KeyboardInterrupt:
            sys.exit()
        else:
            traceback.print_exc()
            login(s)
            continue
