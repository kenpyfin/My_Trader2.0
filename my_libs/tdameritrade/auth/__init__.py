import os
import os.path
import sys
import time
import urllib.parse as up
from shutil import which

import requests
path = "/home/ken/notebook/My_Trader2.0/file/"

def authentication(client_id, redirect_uri, tdauser=None, tdapass=None):
    from selenium import webdriver as se
    # import selenium
    client_id = client_id + '@AMER.OAUTHAP'
    url = 'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=' + up.quote(redirect_uri) + '&client_id=' + up.quote(client_id)



    options = se.FirefoxOptions()
    # options.add_argument("--headless")

    driver = se.Firefox(options=options)

    driver.get(url)

    # Set tdauser and tdapass from environemnt if TDAUSER and TDAPASS environment variables were defined
    tdauser = tdauser or os.environ.get('TDAUSER', '')
    tdapass = tdapass or os.environ.get('TDAPASS', '')

    # Fully automated oauth2 authentication (if tdauser and tdapass were intputed into the function, or found as
    # environment variables)
    if tdauser and tdapass:
        ubox = driver.find_element_by_id('username0')
        pbox = driver.find_element_by_id('password')
        ubox.send_keys(tdauser)
        pbox.send_keys(tdapass)
        driver.find_element_by_id('accept').click()

        driver.find_element_by_id('accept').click()
        while True:
            try:
                code = up.unquote(driver.current_url.split('code=')[1])
                if code != '':
                    break
                else:
                    time.sleep(2)
            except (TypeError, IndexError):
                pass
    else:
        input('after giving access, hit enter to continue')
        code = up.unquote(driver.current_url.split('code=')[1])

    driver.close()
    #
    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data={'grant_type': 'authorization_code',
                               'refresh_token': '',
                               'access_type': 'offline',
                               'code': code,
                               'client_id': client_id,
                               'redirect_uri': redirect_uri})
    if resp.status_code != 200:
        raise Exception('Could not authenticate!')
    return resp.json()


def access_token(refresh_token, client_id):
    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data={'grant_type': 'refresh_token',
                               'refresh_token': refresh_token,
                               'client_id': client_id})
    if resp.status_code != 200:
        raise Exception('Could not authenticate!')
    return resp.json()


def main():
    client_id = input('client id:')
    redirect_uri = input('redirect uri:')
    print(authentication(client_id, redirect_uri))
