# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/17
from typing import List, Tuple, Dict, Union
from googletrans import Translator


class GoogleTrans(object):
    translator = Translator()

    @classmethod
    def translate(cls, data: Dict, fields: List[str]) -> Dict:
        def _google_translate(_sentence: Union[str, List[str]]) -> List[str]:
            if isinstance(_sentence, str):
                _sentence = [_sentence]
            _trans = cls.translator.translate(_sentence, dest='zh-cn')
            return [t.text for t in _trans]

        sentences = [data[c] for c in fields]
        sentences = _google_translate(sentences)
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
    tx = GoogleTrans.translate(deepcopy(x), ['a', 'b', 'c', 'd'])
    for _ in ['a', 'b', 'c', 'd']:
        print(x[_])
        print(tx[_])
        print('---' * 10)


if __name__ == '__main__':
    try_trans()
