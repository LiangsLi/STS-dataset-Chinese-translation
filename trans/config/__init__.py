# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/17
import yaml
from types import SimpleNamespace

with open('trans/config/liangs.yaml', encoding='utf-8')as f:
    configs = yaml.load(f, Loader=yaml.FullLoader)
configs = SimpleNamespace(**configs)

if __name__ == '__main__':
    pass
