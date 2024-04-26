@@ -7,6 +7,8 @@
import json
import time
import sys
import re
from urllib import parse
from collections import OrderedDict
import xml.etree.ElementTree as ET

@@ -18,6 +20,24 @@
_agent = requests.Session()
PY3 = sys.version_info[0] == 3

def read_token():
    with open("token.txt", "r") as f:
        TOKEN = f.read()
    return TOKEN

def update_token(agent):
    """update passportkey
    from https://gist.github.com/AcrylicShrimp/4c94db38b7d2c4dd2e832a7d53654e42
    """

    html = agent.get(url='https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=맞춤법검사기') 

    match = re.search('passportKey=([a-zA-Z0-9]+)', html.text)
    if match is not None:
        TOKEN = parse.unquote(match.group(1))
        with open("token.txt", "w") as f:
            f.write(TOKEN)
    return TOKEN

def _remove_tags(text):
    text = u'<content>{}</content>'.format(text).replace('<br>','')
@@ -28,6 +48,27 @@ def _remove_tags(text):

    return result

def get_response(TOKEN, text):

    payload = {
        'passportKey' : TOKEN,
        'q': text,
        'color_blindness': 0
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'referer': 'https://search.naver.com/',
    }

    r = _agent.get(base_url, params=payload, headers=headers)
    data = json.loads(r.text)

    if ('error' in data['message']) :
        r = get_response(update_token(_agent), text)

    return r


def check(text):
    """
@@ -43,21 +84,13 @@ def check(text):
    # 최대 500자까지 가능.
    if len(text) > 500:
        return Checked(result=False)

    payload = {
        'color_blindness': '0',
        'q': text
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'referer': 'https://search.naver.com/',
    }


    TOKEN = read_token()

    start_time = time.time()
    r = _agent.get(base_url, params=payload, headers=headers)
    r = get_response(TOKEN, text)
    passed_time = time.time() - start_time

    
    data = json.loads(r.text)
    html = data['message']['result']['html']
    result = {
@@ -111,4 +144,4 @@ def check(text):

    result = Checked(**result)

    return result
    return result
