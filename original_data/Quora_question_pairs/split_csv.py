# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/19
import pandas as pd
from pathlib import Path


def csv_split(original_file, each_part_len):
    def split_fun(_ori_data, _part_len):
        _part_list = [_ori_data[i:i + _part_len] for i in range(0, len(_ori_data), _part_len)]
        return _part_list

    csv_data = pd.read_csv(original_file)
    split_csvs = split_fun(csv_data, each_part_len)
    file_dir, file_name = Path(original_file).parent, Path(original_file).name
    for i, cd in enumerate(split_csvs):
        cd.to_csv(str(file_dir / (file_name.strip('.csv') + f'.P{i + 1}.csv')), index=False)


if __name__ == '__main__':
    csv_split('./all/questions.csv', 10000)
