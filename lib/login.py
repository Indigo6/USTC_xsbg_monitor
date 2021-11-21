from __future__ import absolute_import

from check_code import platform_check_code, universal_check_code


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


def login_universal(s, login_site, check_code_site, user_id, user_pwd):
    _ = s.get(login_site).text
    img = s.get(check_code_site).content
    with open('check_code.png', 'wb') as f:
        f.write(img)
    check_code = universal_check_code()
    print("check code: " + check_code)

    # login
    login_dict = {
        "model": "uplogin.jsp",
        "username": user_id,
        "password": user_pwd,
        # CAS_LT: LT - 3f008b0a42f647e6b3e3e251f3634c28
        "LT": check_code,
    }
    login_result = s.post(login_site, data=login_dict)
    login_status_code = login_result.status_code
    if login_status_code == 200:
        print("Login succeed!")
