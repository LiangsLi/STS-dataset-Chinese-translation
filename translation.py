# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/17
from functools import partial
from typing import List, Type, Tuple, Dict
from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
from trans import GoogleTrans, YoudaoTrans, SogouTrans, Timer, init_logger

logger = init_logger(logger_name='translation', log_file='trans.log')


def load_table_file(file_path: str,
                    columns: List[Tuple[str, Type]],
                    sep: str = '\t',
                    skip_header: bool = False) -> List[Dict]:
    """
    加载表格文件
    Args:
        file_path:
        sep:
        columns:
        skip_header:

    Returns:
        加载后的数据
    """
    if file_path.endswith('csv') and sep == ',':
        return load_csv(file_path, columns)
    Row = namedtuple('Row', field_names=[c[0] for c in columns])
    data = []
    with open(file_path, 'r', encoding='utf-8')as f:
        for i, line in enumerate(f):
            if skip_header and i == 0:
                continue
            items = line.strip().split(sep)
            # if len(items) != len(columns):
            #     raise RuntimeError(f'file:{file_path},line:{i + 1} does not match the columns')
            typed_items = []
            for c, it in zip(columns, items):
                typed_items.append(c[1](it))
            data.append(Row(*typed_items)._asdict())
    return data


def load_csv(file_path, columns):
    def transfer(_d, _original_keys, _columns):
        _nd = {}
        for k, (c, t) in zip(_original_keys, _columns):
            _nd[c] = t(_d[k])
        return _nd

    pd_data = pd.read_csv(file_path)
    original_keys = pd_data.keys()
    data = []
    for _, l in pd_data.iterrows():
        data.append(transfer(dict(l), original_keys, columns))
    return data


def time_vs():
    import copy
    import pprint
    test_data = load_table_file('original_data/MSRpar.test.tsv',
                                columns=[('label', float), ('sentence_a', str), ('sentence_b', str)])[:20]
    with Pool() as pool:
        with Timer(f'Google-worker:{pool._processes}'):
            trans_data1 = pool.map(partial(GoogleTrans.translate, fields=['sentence_a', 'sentence_b']),
                                   copy.deepcopy(test_data))
        with Timer(f'Sogou-worker:{pool._processes}'):
            trans_data2 = pool.map(partial(SogouTrans.translate, fields=['sentence_a', 'sentence_b']),
                                   copy.deepcopy(test_data))
        with Timer(f'Youdao-worker:{pool._processes}'):
            trans_data3 = pool.map(partial(YoudaoTrans.translate, fields=['sentence_a', 'sentence_b']),
                                   copy.deepcopy(test_data))
    for t1, t2, t3 in zip(trans_data1, trans_data2, trans_data3):
        pprint.pprint(t1)
        pprint.pprint(t2)
        pprint.pprint(t3)
        print('---' * 10)


def trans_dir(files_dir, file_type, columns, sep, skip_header, output_dir):
    files_dir = Path(files_dir)
    output_dir = Path(output_dir)
    dir_name = files_dir.name
    output_dir = output_dir / f'{dir_name}_zh'
    if not output_dir.is_dir():
        output_dir.mkdir()
    with Pool(processes=10) as pool:
        for file in files_dir.glob(f'*.{file_type}'):
            file_name = file.name
            with Timer(f'{dir_name}/{file_name}-worker:{pool._processes}'):
                data = load_table_file(str(file), sep=sep,
                                       columns=columns,
                                       skip_header=skip_header)
                trans_data = pool.map(partial(SogouTrans.translate, fields=['sentence_a', 'sentence_b']), data)
                with open(str(output_dir / f'{file_name}.zh.tsv'), 'w', encoding='utf-8')as f:
                    f.write('\t'.join([c[0] for c in columns]) + '\n')
                    for d in trans_data:
                        f.write('\t'.join([str(c) for c in d.values()]) + '\n')
                logger.critical(f'{dir_name}/{file_name} ({len(trans_data)} pairs) translate done')


def main():
    dir_pattern = {
        # Quality	#1 ID	#2 ID	#1 String	#2 String
        './original_data/msr': {
            'columns': [('label', str), ('id1', str), ('id2', str),
                        ('sentence_a', str), ('sentence_b', str)],
            'type': 'tsv',
            'sep': '\t',
            'skip_header': True,
        },
        # pair_ID	sentence_A	sentence_B	relatedness_score	entailment_judgment
        './original_data/sick2014': {
            'columns': [('pair_id', str),
                        ('sentence_a', str), ('sentence_b', str),
                        ('label', float),
                        ('entailment', str)],
            'type': 'txt',
            'sep': '\t',
            'skip_header': True
        },
        './original_data/stsbenchmark': {
            'columns': [('data_type', str), ('data_from', str), ('data_eval', str),
                        ('id', str), ('label', float),
                        ('sentence_a', str), ('sentence_b', str)
                        ],
            'type': 'csv',
            'sep': '\t',
            'skip_header': False
        },
        # "id","qid1","qid2","question1","question2","is_duplicate"
        './original_data/Quora_question_pairs/parts': {
            'columns': [('id', str), ('qid1', str), ('qid2', str),
                        ('sentence_a', str), ('sentence_b', str),
                        ('label', str)],
            'type': 'csv',
            'sep': ',',
            'skip_header': True,
        },
    }
    for td, dv in dir_pattern.items():
        trans_dir(files_dir=td, file_type=dv['type'],
                  columns=dv['columns'], sep=dv['sep'], skip_header=dv['skip_header'],
                  output_dir='./trans_data')


if __name__ == '__main__':
    main()
