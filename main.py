import configparser
import os
import re

import requests

from bs4 import BeautifulSoup

cp = configparser.ConfigParser()
cp.read('config.ini')

POSITION = cp.get('default', 'position')
SALARY = cp.get('default', 'salary')
OWS = cp.get('default', 'only_with_salary').lower() not in ['', '0', 'false', 'no', 'not', 'n', '-']
OWS = ['false', 'true'][OWS]
TMP_LINK = cp.get('default', 'tmp_link')
VAC_VOL_REG = cp.get('default', 'vacancy_volume_regex')
VAC_LINK_REG = cp.get('default', 'vacancy_link_regex')
PAGES_NUM_REG = cp.get('default', 'pages_num_regex')
DESCRIPTION_CLASS = cp.get('default', 'vac_desc_div_class')
MAX_VACS = int(cp.get('default', 'max_vacancies'))
MAX_SKILLS = int(cp.get('default', 'max_skills'))
RESULTS_DIR = cp.get('path', 'results')
STOP_WORDS_PATH = cp.get('path', 'stop_words')

browser = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
          'Chrome/39.0.2171.95 ' \
          'Safari/537.36'
headers = {'User-Agent': browser}


def stop_words():
    res = []
    with open(STOP_WORDS_PATH, 'r', encoding='utf-8') as file:
        for line in file.readlines():
           res.append(line.strip())
    return res


def request_get(url):
    resp = requests.get(url=url, headers=headers)
    return resp


def pages_volume():
    link = TMP_LINK.format(position=POSITION.replace(' ', '+'), page_num=0, salary=SALARY, ows=OWS)
    resp = request_get(link)
    content = resp.content.decode('utf-8')
    pages = re.findall(PAGES_NUM_REG, content)
    max_page = max(list(map(int, pages)))
    return max_page


def all_links(max_page_num):
    res = []
    for i in range(max_page_num):
        link = TMP_LINK.format(position=POSITION, page_num=i, salary=SALARY, ows=OWS)
        res.append(link)
    return res


def link_vacancies_links(link):
    resp = request_get(link)
    content = resp.content.decode('utf-8')
    t_pos = POSITION.replace(' ', '%20')
    pattern = VAC_LINK_REG.format(position=t_pos)
    links = re.findall(pattern, content)
    return links


def vac_description(link):
    resp = request_get(link)
    content = resp.content.decode('utf-8')
    bs = BeautifulSoup(content, features='html.parser')
    res = bs.find('div', {'class': DESCRIPTION_CLASS})
    return res.text if hasattr(res, 'text') else ''


def desc_words(_str):
    _str = _str\
        .replace('.', ' ')\
        .replace(',', ' ')\
        .replace(';', ' ')\
        .replace('/', ' ')\
        .replace(')', ' ')\
        .replace('(', ' ')\
        .replace('\\', ' ')\
        .replace('"', ' ')
    words = _str.split()
    words = list(filter(words_filter, words))
    res = dict()
    for w in words:
        wl = w.lower()
        if wl not in res:
            res[wl] = 1
        else:
            res[wl] += 1
    return res


def words_filter(word):
    # res = word and word[0].isalpha() and word[0] == word[0].upper() and word.lower() not in FALSE_WORDS and word[0] < 'А'
    res = word and word[0].isalpha() and word.lower() not in stop_words() and word[0] < 'А'
    return res


def all_pages_links():
    max_p = pages_volume()
    all_l = all_links(max_p)
    return all_l


def all_vac_links(p_links):
    vacancies_links = []
    for l in p_links:
        lvl = link_vacancies_links(l)
        vacancies_links.extend(lvl)
        if len(vacancies_links) >= MAX_VACS:
            break
    return vacancies_links[:MAX_VACS]


def skills_dict(v_links):
    res_dict = dict()
    for ind, link in enumerate(v_links):
        desc = vac_description(link)
        dict_words = desc_words(desc)

        for k, v in dict_words.items():
            if k not in res_dict:
                res_dict[k] = v
            else:
                res_dict[k] += v
        end = '' if (ind + 1) % 10 else '\n'
        print('.'.format(ind + 1, len(v_links)), end=end)
    return res_dict


def sorted_skill_list(s_dict):
    res = [[k.upper(), v] for k, v in s_dict.items()]
    res = reversed(sorted(res, key=lambda x: x[1]))
    return list(res)


def save_results(_list):
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)

    result_path = '{}/{}_ows{}_s{}.tsv'.format(RESULTS_DIR, POSITION.replace(' ', '_'), OWS, SALARY)
    result_string = '\n'.join(['{}\t{}'.format(x[0], x[1]) for x in _list])
    with open(result_path, 'w', encoding='utf-8') as file:
        file.write(result_string)


def main():
    pages_links = all_pages_links()
    print('Gotten {} pages with vacancies'.format(len(pages_links)))

    vac_links = all_vac_links(pages_links)
    print('Gotten {} vacancies links'.format(len(vac_links)))

    res_dict = skills_dict(vac_links)
    res_list = sorted_skill_list(res_dict)

    save_results(res_list)

    print()
    print('pos: {}, ows: {}, salary: {}'.format(POSITION, OWS, SALARY))
    print('-------')
    list(map(lambda x: print(x[0], x[1]), res_list[:MAX_SKILLS]))


if __name__ == '__main__':
    main()
