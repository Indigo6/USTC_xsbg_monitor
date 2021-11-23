from bs4 import BeautifulSoup
from .check_code import platform_check_code, universal_check_code


def login_platform(s, login_site, check_code_site, user_id, user_pwd):
    # get check code
    _ = s.get(login_site).text
    img = s.get(check_code_site).content
    with open('check_code.png', 'wb') as f:
        f.write(img)
    check_code = platform_check_code()
    print("check code: " + check_code)

    # login
    login_dict = {
        'userid': user_id,
        'userpwd': user_pwd,
        'txt_check': check_code
    }
    login_result = s.post(login_site, data=login_dict)
    login_status_code = login_result.status_code
    if login_status_code == 200:
        print("Login succeed!")
    else:
        print("Login failed!")


def login_universal(s, login_site, check_code_site, user_id, user_pwd):
    login_txt = s.get(login_site).text
    login_soup = BeautifulSoup(login_txt, 'lxml')
    login_inputs = login_soup.find_all('input')
    login_lt = login_inputs[2].attrs['value']

    img = s.get(check_code_site).content
    with open('check_code.png', 'wb') as f:
        f.write(img)
    check_code = universal_check_code()
    print("check code: " + check_code)

    # login
    login_dict = {
        "model": "uplogin.jsp",
        "CAS_LT": login_lt,
        "service": "http://yjs.ustc.edu.cn/default.asp",
        "warn": "",
        "showCode": "1",    # "showCode": "" means no need of check code
        "username": user_id,
        "password": user_pwd,
        "LT": check_code,   # comment this line when set "showCode" to ""
        "button": ""
    }
    login_result = s.post(login_site, data=login_dict)
    login_status_code = login_result.status_code
    if login_status_code == 200:
        print("Login succeed!")
    else:
        print("Login failed!")
