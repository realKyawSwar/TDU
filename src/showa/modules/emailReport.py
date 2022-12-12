import smtplib
from smtplib import SMTP
import os
import fnmatch
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from showa.modules import plotting


env = Environment(
    loader=FileSystemLoader('C:\\Users\\sputter.maint\\Desktop\\TDU_V5\\Automated TDU Torque Extraction\\src\\templates'))


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def ngLinks(line, listy, dateTime):
    linky = []
    filepath = plotting.newDir(dateTime, line)
    for chamber in listy:
        z = find(f'{line}_{chamber}_*', filepath)
        linky.append(z[0])
    newLinkList = []
    for i in linky:
        if i[:1] == "P":
            rDrive = "R:\\SPECIAL\\MEASUREMENT" + (i[2:])
            newLinkList.append(rDrive)
        else:
            pass
    if len(newLinkList) == 0:
        newLinkList = linky
    else:
        pass
    return newLinkList


def get_data(ngChLst, linky, tmaxlst, tminlst, CSRalst):
    nogLst = []
    tableHeaders = ["chamber", "link", "tmax", "tmin", "csra"]
    for i, j, k, l, m in zip(ngChLst, linky, tmaxlst, tminlst, CSRalst):
        nogLst.append({a: b for a, b in zip(tableHeaders, [i, j, k, l, m])})
    data = []
    data.append(
        {
         "chambers": nogLst
         })
    return data


def send_mail(bodyContent, line):
    to_email = []
    from_email = ""
    subject = f'L{line} NG TDU Torque Graph Report'
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = "Sputter Automation Bot<SHDS.Spt_maint@showadenko.com>"
    message['To'] = ""

    message.attach(MIMEText(bodyContent, "html"))
    msgBody = message.as_string()

    # server = SMTP('smtp.gmail.com', 587)
    server = SMTP("")
    # server.starttls()
    # server.login(from_email, '')
    server.sendmail(from_email, to_email, msgBody)
    server.quit()


def send_NGemail(line, ngChLst, tmaxlst, tminlst, CSRalst, unResponsive, dateTime):
    try:
        linky = ngLinks(line, ngChLst, dateTime)
        json_data = get_data(ngChLst, linky, tmaxlst, tminlst, CSRalst)
        template = env.get_template('child.html')
        output = template.render(data=json_data[0], line=line, ngChambers=unResponsive)
        send_mail(output, line)
        print("Mail sent successfully.")
    except Exception as e:
        print(f"email failed due to {e}")


def send_OKemail(line):
    try:
        sender = ""
        receivers = []
        message = MIMEMultipart()
        message["Subject"] = f"L{line} TDU torque graph collection is completed"
        message["From"] = "Sputter Automation Bot<SHDS.Spt_maint@showadenko.com>"
        message["To"] = ""
        content = """Dear Engineers,


Good job! All look pretty well. Keep up the excellent work.
Kindly visit the following directory in file browser to review.

R:\SPECIAL\MEASUREMENT\PROD\CHECKLIST\Sputter Equipment\TDU Torque

Thank you.
Best regards,
TDU Automation Bot
                """
        part1 = MIMEText(content, "plain")
        message.attach(part1)

        # showa settings
        smtpObj = smtplib.SMTP("")
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print("email sent")

    except Exception as e:
        raise(e)
