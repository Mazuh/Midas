#!/usr/bin/env python
"""
Scrapping public information from government about its colleges in Brazil, RN.
The results will be at report files, in JSON and CSV format.

TODO: find all IFRN's professors remunerations.
"""

import json
import time
import csv
import threading

from queue import Queue
from datetime import datetime

from urllib.request import urlopen
from bs4 import BeautifulSoup

# a lot of useful stuff for beautiful soup to get

URL_ROOT_EMPLOYEES = 'http://www.portaldatransparencia.gov.br/servidores/'

INVALID_QUERY_MSG = 'Parâmetros de pesquisa inválidos.'

EMPLOYEES_INTERESTING_DETAILS_TITLES = {
    'organizationalUnit' : 'UORG', # organizational unit
    'employeeSince' : 'Data de publicação', # employee since when?
    'class' : 'Classe', # http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12772.htm
    'situationBond' : 'Situação Vínculo', # exclusive or not? is it an active asset?
}

# some default values

MAX_HTTP_CONNECTIONS = 6 # maximum number of http threads at the same time

# masks to .format() and insert a date as YYMMDD
EMPLOYEES_BASICS_FILENAME = './reports/{}_ifrn_employees_basics_search.json'
EMPLOYEES_DETAILS_DS_FILENAME = './reports/{}_ifrn_employees_details.csv'


# here we go for the functions

def report_employees_basics(employees_basics_filename=EMPLOYEES_BASICS_FILENAME):
    """
    Scrapes data from generic search about employees names and puts them on a given filename.
    Should be the initial function to be called before the other employees reports.
    """

    with open(employees_basics_filename.format(_time_now_str()), 'w') as employees_basics_file:

        employees_basics_file.write('{\n')
        employees_index = 0
        page_num = 1
        ended_querying_all_pages = False

        while not ended_querying_all_pages:
            print('Reading page {0}...'.format(page_num))

            search_response = urlopen(_employees_search_url(page_num))
            search_soup = BeautifulSoup(search_response, 'html.parser')

            ended_querying_all_pages = INVALID_QUERY_MSG in search_soup.find(id='conteudo').text

            if not ended_querying_all_pages:

                employees_table = search_soup.find(id='listagem').find('table')
                employees_rows = employees_table.find_all('tr')
                del employees_rows[0]

                for employees_row in employees_rows:
                    employee = {}

                    cpf, name, _ = employees_row.find_all('td')

                    employee['name'] = name.text.title()
                    employee['cpf'] = cpf.text
                    employee['urlDetailsSufix'] = name.find('a').get('href')

                    employees_basics_file.write((
                        '  {0}"{1}": {{\n' +\
                        '    "name": "{2}",\n' +\
                        '    "cpf": "{3}",\n' +\
                        '    "urlDetailsSufix": "{4}"\n' +\
                        '  }}\n'
                    ).format(
                        ',' if employees_index else '',
                        employees_index,
                        employee['name'].strip(),
                        employee['cpf'].strip(),
                        employee['urlDetailsSufix'].strip()
                    ))

                    employees_index += 1

                page_num += 1

        employees_basics_file.write('}\n')

    print('Reached the end after {0} pages and {1} employees found.'
          .format(page_num-1, employees_index))




def report_employees_details(employees_basics_filename=EMPLOYEES_BASICS_FILENAME,
                             target_details_ds_filename=EMPLOYEES_DETAILS_DS_FILENAME):
    """
    Scrapes details data of each employee and puts them on a csv file.
    The employees basics list should be already stored in a
    local file based on a given filename param.
    """
    # ready...
    employees_basics = None
    with open(employees_basics_filename.format(_time_now_str()), 'r') as employees_basics_file:
        employees_basics = json.loads(employees_basics_file.read())

    with open(target_details_ds_filename.format(_time_now_str()), 'w', newline='') as details_ds_file:
        ds_writer = csv.DictWriter(details_ds_file, fieldnames=[
            'index',
            'name',
            'cpf',
            'campus',
            'class',
            'situationBond',
            'organizationalUnit',
            'campus',
            'hasTrustPosition',
            'employeeSince',
            'urlRemunerationSufix'
        ])

        ds_writer.writeheader()

        # aim...
        scrapers_q = Queue()

        for employee_index in employees_basics:
            scrapers_q.put(threading.Thread(
                target=_scrap_employee_details,
                args=(employees_basics, employee_index, ds_writer)
            ))

        # fire!
        while not scrapers_q.empty():
            if threading.active_count() == 1:
                for _ in range(MAX_HTTP_CONNECTIONS):
                    if not scrapers_q.empty():
                        scrapers_q.get().start()
            else:
                time.sleep(1)

        while threading.active_count() != 1:
            print('Waiting for remaining requests...')
            time.sleep(1)

        print('Done. Dataset as CSV successfully assembled.')




def _scrap_employee_details(employees_basics: dict, employee_key: str, ds_writer: csv.DictWriter):
    employee_details = {}

    url_details_sufix = employees_basics[employee_key]['urlDetailsSufix']
    details_response = urlopen(_employee_details_url(url_details_sufix))
    details_soup = BeautifulSoup(details_response, 'html.parser')

    # get its link for $$$

    remuneration_url_sufix = (details_soup
                              .find('a', title='Remuneração individual do servidor')
                              .get('href'))
    if remuneration_url_sufix[:12] == '/servidores/':
        remuneration_url_sufix = remuneration_url_sufix[12:]

    employee_details['urlRemunerationSufix'] = remuneration_url_sufix

    # scrapes more details for its profile

    details_tables = details_soup.find_all('table', summary='Detalhes do Servidor')

    if len(details_tables) == 2:
        employee_details['hasTrustPosition'] = True
        details_table = details_tables[1]
    else:
        employee_details['hasTrustPosition'] = False
        details_table = details_tables[0]

    details_tbody = details_table.find('tbody')

    for details_row in details_tbody.find_all('tr'):
        details_data = details_row.find_all('td')

        if len(details_data) == 2:
            title, content = details_data
            title = title.text

            for interesting_key, interesting_title in EMPLOYEES_INTERESTING_DETAILS_TITLES.items():
                if interesting_title in title:
                    if interesting_key in employee_details:
                        employee_details[interesting_key] += ' / ' + content.text.strip()
                    else:
                        employee_details[interesting_key] = content.text.strip()

    # trying to write data on dataset

    print('Reading {}: {}...'.format(employee_key, employees_basics[employee_key]['name']))
    employee_details['index'] = employee_key
    employee_details['name'] = employees_basics[employee_key]['name']
    employee_details['cpf'] = employees_basics[employee_key]['cpf']

    if 'CAMPUS' in employee_details['organizationalUnit']:
        for unit in employee_details['organizationalUnit'].split('/'):
            if 'CAMPUS' in unit.upper():
                employee_details['campus'] = unit.strip()
    else:
        employee_details['campus'] = employee_details['organizationalUnit'].split('/')[0].strip()

    if 'campus' not in employee_details:
        employee_details['campus'] = ''

    ds_writer.writerow(employee_details)




def report_employees_remunerations():
    pass




def _employees_search_url(page_num: int):
    base_ifrn = URL_ROOT_EMPLOYEES + 'OrgaoExercicio-ListaServidores.asp?CodOS=15000&DescOS=MINISTERIO%20DA%20EDUCACAO&CodOrg=26435&DescOrg=INSTITUTO%20FEDERAL%20DO%20RIO%20GRANDE%20DO%20NORTE&Pagina='
    return base_ifrn + str(page_num)




def _employee_details_url(url_sufix: str):
    return URL_ROOT_EMPLOYEES + url_sufix




def _time_now_str():
    today = datetime.today()
    year = str(today.year)[2:]
    month = str(today.month) if today.month > 9 else '0'+str(today.month)
    day = str(today.day) if today.day > 9 else '0'+str(today.day)
    return year + month + day



# routines
report_employees_basics()
report_employees_details()
print('hello there')
