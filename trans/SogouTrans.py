# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/17
import sys

sys.path.append('..')
sys.path.append('.')
import time
import json
import requests
import hashlib
import urllib.parse
from typing import List, Dict, Tuple, Union
from trans.config import configs


class SogouTrans(object):
    @staticmethod
    def md5(s: str):
        m = hashlib.md5()
        m.update(s.encode("utf8"))
        return m.hexdigest()

    @classmethod
    def translate(cls, data: Dict, fields: List) -> Dict:
        def _sogou_translation(_sentence: str):
            _salt = str(int(time.time()))
            _sign = cls.md5(configs.SogouPID + _sentence + _salt + configs.SogouKEY)
            _src = 'en'
            _dest = 'zh-CHS'
            _payload = "from=" + _src + "&to=" + _dest + "&pid=" + configs.SogouPID + "&q=" + urllib.parse.quote(
                _sentence) + "&sign=" + _sign + "&salt=" + _salt
            _headers = {
                'content-type': "application/x-www-form-urlencoded",
                'accept': "application/json"
            }
            _response = requests.request("POST", configs.SogouURL, data=_payload, headers=_headers)
            try:
                result = json.loads(_response.text)['translation']
            except KeyError as e:
                print(json.loads(_response.text))
                print(_sign)
                print(_sentence)
                raise e
            return result

        sentences = [data[c].strip() for c in fields]
        sentences = [_sogou_translation(s) for s in sentences]
        for c, s in zip(fields, sentences):
            data[c] = s
        return data


def try_trans():
    from copy import deepcopy
    a = "A brown dog is attacking another animal in front of the tall man in pants."
    b = "A brown dog is attacking another animal in front of the man in pants."
    c = "Myanmar's pro-democracy leader Aung San Suu Kyi will be kept under house arrest " \
        "following her release from a hospital where she underwent surgery, her personal physician said Friday."
    d = "charge falsely or with malicious intent; attack the good name and reputation of someone."
    x = {'a': a, 'b': b, 'c': c, 'd': d}
    tx = SogouTrans.translate(deepcopy(x), ['a', 'b', 'c', 'd'])
    for _ in ['a', 'b', 'c', 'd']:
        print(x[_])
        print(tx[_])
        print('---' * 10)


if __name__ == '__main__':
    try_trans()
