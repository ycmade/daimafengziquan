# 在这里输入青龙面板用户名密码，如果不填写，就自动从auth.json中读取
username = ""
password = ""

import requests
import time
import json
import re
from urllib.parse import urlencode

requests.packages.urllib3.disable_warnings()

token = ""
if username == "" or password == "":
    f = open("/ql/config/auth.json")
    auth = f.read()
    auth = json.loads(auth)
    username = auth["username"]
    password = auth["password"]
    token = auth["token"]
    f.close()


def gettimestamp():
    return str(int(time.time() * 1000))


def login(username, password):
    url = "http://127.0.0.1:5700/api/login?t=%s" % gettimestamp()
    data = {"username": username, "password": password}
    r = s.post(url, data)
    s.headers.update({"authorization": "Bearer " + json.loads(r.text)["data"]["token"]})


def getitem(searchValue):
    url = "http://127.0.0.1:5700/api/envs?searchValue=%s&t=%s" % (searchValue, gettimestamp())
    r = s.get(url)
    item = json.loads(r.text)["data"]
    return item


def getckitem(searchValue, value):
    url = "http://127.0.0.1:5700/api/envs?searchValue=%s&t=%s" % (searchValue, gettimestamp())
    r = s.get(url)
    for i in json.loads(r.text)["data"]:
        if value in i["value"]:
            return i
    return []


def wstopt(cookies):
    headers = {
        'user-agent': 'JD4iPhone/167802 (iPhone; iOS 14.7.1; Scale/3.00)',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies,
    }
    url = 'https://api.m.jd.com/client.action?functionId=genToken&clientVersion=10.1.2&build=167802&client=apple' \
          '&d_brand=&d_model=&osVersion=&screen=&partner=&oaid=&openudid=a27b83d3d1dba1cc&eid=&sdkVersion=30&lang' \
          '=zh_CN&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&networkType=wifi&wifiBssid=&uts' \
          '=&uemps=0-2&harmonyOs=0&st=1630413012009&sign=ca712dabc123eadd584ce93f63e00207&sv=121'
    body = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml' \
           '%252fappjmp_blank.html%22%7D&'
    response = requests.post(url, data=body, headers=headers, verify=False)
    data = json.loads(response.text)
    if data.get('code') != '0':
        return None
    tokenKey = data.get('tokenKey')
    url = data.get('url')
    session = requests.session()
    params = {
        'tokenKey': tokenKey,
        'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'
    }
    url += '?' + urlencode(params)
    session.get(url, allow_redirects=True)
    result = ""
    for k, v in session.cookies.items():
        if k == 'pt_key' or k == 'pt_pin':
            result += k + "=" + v + "; "
    return result


def checkcookie(cookies):
    try:
        url = 'https://api.m.jd.com/client.action?functionId=newUserInfo&clientVersion=10.1.2&client=apple&openudid' \
              '=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&st' \
              '=1626848394828&sign=447ffd52c08f0c8cca47ebce71579283&sv=101&body=%7B%22flag%22%3A%22nickname%22%2C' \
              '%22fromSource%22%3A1%2C%22sourceLevel%22%3A1%7D&'
        headers = {
            'user-agent': 'JD4iPhone/167802 (iPhone; iOS 14.7.1; Scale/3.00)'
        }
        response = requests.post(url=url, headers=headers, cookies=cookies, verify=False)
        data = response.json()
        if data['code'] != '0':
            return False
        else:
            return True
    except:
        return False


def update(text, qlid):
    url = "http://127.0.0.1:5700/api/envs?t=%s" % gettimestamp()
    s.headers.update({"Content-Type": "application/json;charset=UTF-8"})
    data = {
        "name": "JD_COOKIE",
        "value": text,
        "_id": qlid
    }
    r = s.put(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def insert(text):
    url = "http://127.0.0.1:5700/api/envs?t=%s" % gettimestamp()
    s.headers.update({"Content-Type": "application/json;charset=UTF-8"})
    data = []
    data_json = {
        "value": text,
        "name": "JD_COOKIE"
    }
    data.append(data_json)
    r = s.post(url, json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


if __name__ == '__main__':
    s = requests.session()
    if token == "":
        login(username, password)
    else:
        s.headers.update({"authorization": "Bearer " + token})
    count = 0
    wskeys = getitem("JD_WSCK")
    for i in wskeys:
        count += 1
        wspin = re.findall(r"pin=(.*?);", i["value"])[0]
        if i["status"] == 0:
            item = getckitem("JD_COOKIE", "pt_pin=" + wspin)
            if item != []:
                if checkcookie(item["value"]):
                    if update(wstopt(i["value"]), item["_id"]):
                        print("第%s个wskey更新成功, pin:%s" % (count, wspin))
                    else:
                        print("第%s个wskey更新失败, pin:%s" % (count, wspin))
                else:
                    print("第%s个wskey无需更新, pin:%s" % (count, wspin))
            else:
                if insert(wstopt(i["value"])):
                    print("第%s个wskey添加成功, pin:%s" % (count, wspin))
                else:
                    print("第%s个wskey添加失败, pin:%s" % (count, wspin))
        else:
            print("第%s个wskey已禁用, pin:%s" % (count, wspin))
