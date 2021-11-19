import json
import smtplib
import traceback

from email.mime.text import MIMEText
from email.header import Header


def send_email(mail_content, mail_server, mail_address, mail_passwd) :
    try:
        message = MIMEText(mail_content, 'plain', 'utf-8')
        message['From'] = Header("学术报告脚本", 'utf-8')   # 发送者
        message['To'] = Header("学术报告选课通知", 'utf-8')  # 接收者
        message['Subject'] = Header('学术报告选课通知', 'utf-8')

        mail_hosts = {
            "qq":   "smtp.qq.com",
            "ustc": "mail.ustc.edu.cn"
        }
        mail_host = mail_hosts[mail_server]

        server = smtplib.SMTP_SSL(mail_host, 465)
        server.login(mail_address, mail_passwd)

        server.sendmail(mail_address, [mail_address], message.as_string())
        server.quit()
    except smtplib.SMTPException as e:
        print("Send Email Failed")
        traceback.print_exc()


if __name__ == "__main__":
    with open('cfg/mine.json', encoding='utf-8') as f:
        js = json.load(f)
    mail_server = js['mail_server']
    mail_address = js["mail_address"]
    mail_passwd = js["mail_passwd"]
    send_email("test", mail_server, mail_address, mail_passwd)
