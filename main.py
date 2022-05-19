# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import multiprocessing
from anticaptchaofficial.hcaptchaproxyon import *
import random
import os
import threading
from typing import List
from html import unescape
from ssl import create_default_context
from random_username.generate import generate_username
import json
import time
import requests


def get_proxies():

    new_session = randstr(6)
    proxy = {"http":"http://k2ys:niggakilla_session-"+new_session+"_lifetime-30m@91.239.130.17:12323",
             "https":"http://k2ys:niggakilla_session-"+new_session+"_lifetime-30m@91.239.130.17:12323"
        }
    return proxy


def randstr(lenn):
    lib = "abcdefghijklmnopqrstuvwxyz0123456789"
    text = ''
    for i in range(0, lenn):
        text += lib[random.randint(0, len(lib) - 1)]
    return text


def solve_hcaptcha(site_key, url, proxy, cookie, order_id):
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed

    solver = hCaptchaProxyon()
    solver.set_verbose(1)
    solver.set_key(CAP_API)
    solver.set_website_url(url)
    solver.set_website_key(site_key)
    solver.set_proxy_address(re.search(r'http://(.*):(.*)@(.*):(.*)', proxy['http']).group(3))
    solver.set_proxy_port(re.search(r'http://(.*):(.*)@(.*):(.*)', proxy['http']).group(4))
    solver.set_proxy_login(re.search(r'http://(.*):(.*)@(.*):(.*)', proxy['http']).group(1))
    solver.set_proxy_password(re.search(r'http://(.*):(.*)@(.*):(.*)', proxy['http']).group(2))
    solver.set_user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36")

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        return g_response
    else:
        captcha_failed +=1
        cancel_mail(order_id)
        exit()


def get_5sim_num():
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed

    proxy = get_proxies()

    headers = {
        'Authorization': 'Bearer ' + sim_token,
        'Accept': 'application/json',
    }
    try:
        response = requests.get('https://5sim.net/v1/user/profile', headers=headers, proxies=proxy)
        # print(response.text)
        # print(response)
        bal = re.search(r'balance":(.*),"rating"', response.text).group(1)
        # print(bal)

        if float(bal) < 5:
            print("5Sim Balance Insufficient")
            exit()
    except:
        print("5Sim Authentication failed")
        exit()

    country = requests.get(
        "https://ipapi.co/" + requests.get("https://api.ipify.org/", proxies=proxy).text + "/json/")
    country = re.search(r'"country_name": "(.*)",', country.text).group(1)

    operator = 'any'
    product = 'discord'

    response = requests.get('https://5sim.net/v1/user/buy/activation/' + country.lower() + '/' + operator + '/' + product, headers=headers, proxies=proxy)

    if not response.ok:
        print(response)
        print(response.text)
        phone_failed += 1
        exit()
    print(response)
    print(response.text)
    phone = re.search(r'phone":"(.*)","operator"', response.text).group(1)
    order_id = re.search(r'id":(.*),"phone"', response.text).group(1)

    return order_id, phone


def get_5sim_response(order_id):
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed

    proxy=get_proxies()

    headers = {
        'Authorization': 'Bearer ' + sim_token,
        'Accept': 'application/json',
    }

    response = requests.get('https://5sim.net/v1/user/finish/' + order_id, headers=headers, proxies=proxy)
    print(response)

    while "code" not in response.text:
        time.sleep(3)
        response = requests.get('https://5sim.net/v1/user/check/' + order_id, headers=headers, proxies=proxy)
        print(response)
        print(response.text)
        if "TIMEOUT" in response.text:
            phone_failed += 1
            exit()

    code = re.search(r'code":"(.*)"}]', response.text).group(1)
    return code


def get_fingerprint(proxy):

    r = requests.post("https://discord.com/api/v6/auth/fingerprint", data={}, proxies=proxy)
    fingerprint = re.search(r'{"fingerprint": "(.*)"}', r.text).group(1)
    return fingerprint


def phone_verify(proxy, order_id, phone, token, cookie, email_id):
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed

    data = {"phone": phone, "change_phone_reason": "user_settings_update"}
    headers = {
        "Host": "discord.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "cookie": cookie,
        "Origin": "https://discord.com",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "x-debug-options": "bugReporterEnabled",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuODggU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMC4wLjQ4OTYuODgiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTI0NTIzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    }
    r = requests.Session().post("https://discord.com/api/v9/users/@me/phone", headers=headers, data=json.dumps(data), proxies=proxy)

    while "captcha_sitekey" in r.text:
        site_key = re.search(r'"captcha_sitekey": "(.*)",', r.text).group(1)
        captcha = solve_hcaptcha(site_key, "https://discord.com/api/v9/users/@me/phone", proxy, cookie, email_id)

        data = {"phone": phone, "captcha_key": captcha, "change_phone_reason": "user_action_required"}
        r = requests.Session().post("https://discord.com/api/v9/users/@me/phone", headers=headers, data=json.dumps(data), proxies=proxy)
    #     print(r)
    #
    # print(r)
    captcha_success += 1
    data = {"phone": phone, "code": get_5sim_response(order_id)}
    r = requests.post("https://discord.com/api/v9/phone-verifications/verify", headers=headers, data=json.dumps(data), proxies=proxy)
    # print(r)
    # print(r.text)
    phone_success += 1


def get_email():
    global Kopeechka_token
    r = requests.get("https://api.kopeechka.store/mailbox-get-email?api=2.0&spa=1&site=discord.com&sender=discord&regex=&mail_type=outlook.com&token="+Kopeechka_token).json()
    # print(r)
    return r['id'], r['mail']


def verify_email(p):
    global Kopeechka_token
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed
    x=0
    r = requests.get(
        "https://api.kopeechka.store/mailbox-get-message?full=1&spa=1&id=" + p + "&token="+Kopeechka_token).json()
    while r['value'] == "WAIT_LINK":
        x+=1
        time.sleep(3)
        r = requests.get(
            "https://api.kopeechka.store/mailbox-get-message?full=1&spa=1&id=" + p + "&token="+Kopeechka_token).json()
        if x>10:
            exit()
            email_failed+=1
    return r['value']


def cancel_mail(order_id):
    global Kopeechka_token
    r = requests.get("http://api.kopeechka.store/mailbox-cancel?id="+order_id+"&token="+Kopeechka_token)
    return


def register():

    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed

    proxy = get_proxies()

    cookie = f"__cfuid={randstr(43)}; __dcfduid={randstr(32)}; locale=en-US"

    fingerprint = get_fingerprint(proxy) # Get Fingerprint

    name = generate_username()[0] # Get Fake Username

    email_id, address = get_email()

    data={"fingerprint":fingerprint,
           "email": address,
           "username": name,
           "password":address+"KKK",
           "invite": None,
           "consent": True,
           "date_of_birth":"2001-05-05",
           "gift_code_sku_id": None,
           "captcha_key": None}

    headers={"Host":"discord.com",
             "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36",
             "Accept":"*/*",
             "Accept-Language":"en-US",
             "Accept-Encoding":"gzip, deflate, br",
             "Content-Type": "application/json",
             "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuODggU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMC4wLjQ4OTYuODgiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTI0NTIzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
             "X-Fingerprint": fingerprint,
             "X-Discord-Locale": "en-US",
             "X-Debug-Options": "bugReporterEnabled",
             "Origin": "https://discord.com",
             "Connection": "keep-alive",
             "Referer": "https://discord.com/register",
             "Cookie": cookie,
             "Sec-Fetch-Dest": "empty",
             "Sec-Fetch-Mode": "cors",
             "Sec-Fetch-Site": "same-origin",
             "TE": "trailers",
             "DNT": "1"
             }

    r = requests.Session().post("https://discord.com/api/v9/auth/register", headers=headers, data=json.dumps(data), proxies=proxy)
    x=0
    while "captcha_sitekey" in r.text:
        if x==3:
            captcha_failed += 4
            exit()
        # print(r.text)
        site_key = re.search(r'"captcha_sitekey": "(.*)",', r.text).group(1)
        captcha = solve_hcaptcha(site_key, "https://discord.com", proxy, cookie, email_id)
        # print("CAPTCHA BEING SOLVED! with"+captcha)

        data = {"fingerprint": fingerprint,
            "email": address,
            "username": name,
            "password": address+"KKK",
            "invite": None,
            "consent": True,
            "date_of_birth": "1980-05-01",
            "gift_code_sku_id": None,
            "captcha_key": captcha}


        r = requests.Session().post("https://discord.com/api/v9/auth/register", headers=headers, data=json.dumps(data), proxies=proxy)
        x = x + 1

    if not r.ok:
        aborting += 1
    # print(r)
    # print(r.text)
    captcha_success += 1
    token = re.search(r'token": "(.*)"', r.text).group(1)
    # print(token)

    # headers = {
    #     "Host": "discord.com",
    #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36",
    #     "accept": "*/*",
    #     "accept-encoding": "gzip, deflate, br",
    #     "accept-language": "en-US,en;q=0.9",
    #     "authorization": token,
    #     "content-type": "application/json",
    #     "cookie": cookie,
    #     "Origin": "https://discord.com",
    #     "sec-fetch-dest": "empty",
    #     "sec-fetch-mode": "cors",
    #     "sec-fetch-site": "same-origin",
    #     "Connection": "keep-alive",
    #     "Cache-Control": "no-cache",
    #     "x-debug-options": "bugReporterEnabled",
    #     "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuODggU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMC4wLjQ4OTYuODgiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTI0NTIzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    # }

    # r = requests.get("https://discord.com/api/v9/users/@me/library", headers=headers, proxies=proxy)
    # print(r)

    time.sleep(5)
    headers = {
                   "Host": "discord.com",
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36",
                   "Accept": "*/*",
                   "Accept-Language": "en-US",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Content-Type": "application/json",
                   "Authorization": token,
                   "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuODggU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMC4wLjQ4OTYuODgiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTI0NTIzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
                   "X-Debug-Options": "bugReporterEnabled",
                   "Origin": "https://discord.com",
                   "Connection": "keep-alive",
                   "Referer": "https://discord.com/channels/@me",
                   "Cookie": cookie,
                   "Sec-Fetch-Dest": "empty",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "same-origin",
                   "TE": "trailers",
                   "DNT": "1"
                   }
    r = requests.Session().get("https://discord.com/api/v9/users/@me/library", headers=headers, proxies=proxy)
    if not r.ok:
        # print(r.text)
        # print(r)
        aborting +=1
        cancel_mail(email_id)
        exit()

    file = open("tokens.txt", "a")
    file.write(token+":"+address+"\n")
    file.close()
    succesful_tokens += 1

    time.sleep(17)
    # print("Now we will be verifying our Email")
    token_link = requests.get(verify_email(email_id)).url
    # print(token_link)
    tkn = re.search(r"token=(.*)", token_link).group(1)
    # print(tkn)
    data = {"token": tkn,"captcha_key": None}
    # print(data)
    headers = {
                   "Host": "discord.com",
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4889.0 Safari/537.36",
                   "Accept": "*/*",
                   "Accept-Language": "en-US",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Content-Type": "application/json",
                   "Authorization": token,
                   "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuODggU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMC4wLjQ4OTYuODgiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTI0NTIzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
                   "X-Debug-Options": "bugReporterEnabled",
                   "Origin": "https://discord.com",
                   "Connection": "keep-alive",
                   "Referer": "https://discord.com",
                   "Cookie": cookie,
                   "Sec-Fetch-Dest": "empty",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "same-origin",
                   "TE": "trailers",
                   "DNT": "1"
                   }
    r = requests.Session().post("https://discord.com/api/v9/auth/verify", headers=headers, data=json.dumps(data), proxies=proxy)
    # print(r.text)
    while "captcha_sitekey" in r.text:
        site_key = re.search(r'"captcha_sitekey": "(.*)",', r.text).group(1)
        captcha = solve_hcaptcha(site_key, "https://discord.com", proxy, cookie, email_id)
        # print(r.text)
        data = {"token": tkn, "captcha_key": captcha}
        r = requests.Session().post("https://discord.com/api/v9/auth/verify", headers=headers, data=json.dumps(data), proxies=proxy)

    # print(r.text)
    captcha_success += 1

    # time.sleep(10)
    # order_id, num = get_5sim_num()
    # print(order_id+"yes :"+num)
    # phone_verify(proxy, order_id, num, token, cookie, email_id)
    #
    # file = open("tokens.txt", "a")
    # file.write(":"+num+"\n")
    # file.close()


def multithreading():
    global phone_failed, phone_success, captcha_failed, captcha_success, aborting, succesful_tokens, email_success, email_failed
    threads = [
        threading.Thread(target=register)
        for _ in range(50)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()


def GUI():
    while True:
        print(
            "███▄▄▄▄      ▄████████ ▀████    ▐████▀     ███        ▄██████▄     ▄████████ ███▄▄▄▄\n███▀▀▀██▄   ███    ███   ███▌   ████▀  ▀█████████▄   ███    ███   ███    ███ ███▀▀▀██▄\n███   ███   ███    █▀     ███  ▐███       ▀███▀▀██   ███    █▀    ███    █▀  ███   ███\n███   ███  ▄███▄▄▄        ▀███▄███▀        ███   ▀  ▄███         ▄███▄▄▄     ███   ███\n███   ███ ▀▀███▀▀▀        ████▀██▄         ███     ▀▀███ ████▄  ▀▀███▀▀▀     ███   ███\n███   ███   ███    █▄    ▐███  ▀███        ███       ███    ███   ███    █▄  ███   ███\n███   ███   ███    ███  ▄███     ███▄      ███       ███    ███   ███    ███ ███   ███\n ▀█   █▀    ██████████ ████       ███▄    ▄████▀     ████████▀    ██████████  ▀█   █▀\n")
        print(("Tokens: " + str(succesful_tokens) + "\tSuccesful Captchas: " + str(captcha_success) + "\nAborts:" + str(
            aborting) + "\tPhone Verifications: " + str(phone_success) + "\n\n\n\n").expandtabs(63))
        print(("Failed Phone: " + str(phone_failed) + "\tFailed Captchas: " + str(captcha_failed) + "\nEmail Failed: " + str(
            email_failed)).expandtabs(63))
        print("\nBy your dad")
        time.sleep(0.02)
        os.system('cls')


phone_failed = phone_success = captcha_failed = captcha_success = aborting = succesful_tokens = email_failed = 0
global sim_token
#sim_token = input("\nEnter your 5Sim API Key: ")
global CAP_API
#CAP_API = input("\nEnter your CapMonster API Key: ")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
global Kopeechka_token

sim_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjkwNDE0MjQsImlhdCI6MTYzNzUwNTQyNCwicmF5IjoiY2IzMmRlNjA1ZDljNzMxNjM3MmVlYjdjMzYxOWM2MjciLCJzdWIiOjgxODAwNH0.oWy6JRCWDXxmUa-HL8Jz8phBc1zyELtfSqHD9g9qDXAHDqr_h6oSoUYHwQOfQccu7EK9gId863BVw1KF1UL_fySLSriMYI5S2uZo2yt18CEZqntAXzcDcqrVGpH2xOzeFwXDs-iGnaIi4dvX3-6T0pStP99Ce5QOCTxVVGk3W5UlWjRF553vKeDE8Ws8R8hoGIS6mJIHwSn_vF-1eiXIwteogOGcSbg0vVbj7GNG8_Bw2jq_9yNdGE2Ko9k9zHzqvTzAVy-xOQbq6Djn4aXXDoGJpcL9qKEE1hwMqjJ0rYmjYkWa5yw_Hfal3zb2BqYpylcvbEnblLkk3pva3tPprg"
CAP_API = "Anti-Captcha key here"
Kopeechka_token = "kopeechka key"

# if __name__ == "__main__":
#     workers = [
#         multiprocessing.Process(
#             target=multithreading())
#         for _ in range(1)]
#     for worker in workers: worker.start()

t = threading.Thread(target=multithreading)
a = threading.Thread(target=GUI)
t.start()
a.start()
t.join()
a.join()


