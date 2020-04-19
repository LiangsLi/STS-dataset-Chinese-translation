# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/17
import sys
import uuid
import requests
import hashlib
import json
import time
from typing import List, Dict, Tuple, Union
from trans.config import configs


class YoudaoTrans(object):
    @staticmethod
    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    @staticmethod
    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    @staticmethod
    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(configs.YoudaoURL, data=data, headers=headers)

    @classmethod
    def translate(cls, data: Dict, fields: List) -> Dict:
        def _youdao_translation(_sentence):
            _data = {'from': 'en', 'to': 'zh-CHS', 'signType': 'v3'}
            _curtime = str(int(time.time()))
            _data['curtime'] = _curtime
            _salt = str(uuid.uuid1())
            _signStr = configs.YoudaoKEY + cls.truncate(_sentence) + _salt + _curtime + configs.YoudaoSECRET
            _sign = cls.encrypt(_signStr)
            _data['appKey'] = configs.YoudaoKEY
            _data['q'] = _sentence
            _data['salt'] = _salt
            _data['sign'] = _sign
            _response = cls.do_request(_data)
            return json.loads(_response.content)['translation']

        sentences = [data[c] for c in fields]
        sentences = [_youdao_translation(s) for s in sentences]
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
    tx = YoudaoTrans.translate(deepcopy(x), ['a', 'b', 'c', 'd'])
    for _ in ['a', 'b', 'c', 'd']:
        print(x[_])
        print(tx[_])
        print('---' * 10)


if __name__ == '__main__':
    try_trans()
