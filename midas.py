"""
Scrapping public information from government about its colleges in Brazil, RN.
The results will be at report files, in JSON format.

TODO: find all IFRN's professors basic details.
TODO: find all IFRN's professors remunerations.
"""

import json
import time
import csv

from threading import Thread
from queue import Queue
from io import TextIOWrapper

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

EMPLOYEES_BASICS_FILENAME = './reports/employees_basics.json'
EMPLOYEES_DETAILS_DS_FILENAME = './reports/ifrn_employees_details.csv'


# here we go for the functions

def report_employees_basics(employees_basics_filename=EMPLOYEES_BASICS_FILENAME):
    """
    Scrapes data from generic search about employees names and puts them on a given filename.
    Should be the initial function to be called before the other employees reports.
    """

    with open(employees_basics_filename, 'w') as employees_basics_file:

        employees_basics_file.write('{\n')
        employees_index = 0
        page_num = 1
        ended_querying_all_pages = False

        while not ended_querying_all_pages:
            print("Reading page {0}...".format(page_num))

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

    print("Reached the end after {0} pages and {1} employees found.".format(page_num-1, employees_index))




def report_employees_details(employees_basics_filename=EMPLOYEES_BASICS_FILENAME,
                             target_details_ds_filename=EMPLOYEES_DETAILS_DS_FILENAME):
    """
    Scrapes details data of each employee and puts them on files based on given filenames mask.
    The employees should be already stored in a local file based on a given filename param.
    """
    employees_basics = None
    with open(employees_basics_filename, 'r') as employees_basics_file:
        employees_basics = json.loads(employees_basics_file.read())

    #scrapping_threads_q = Queue()

    with open(target_details_ds_filename, 'w', newline='') as details_ds_file:
        csvwriter = csv.DictWriter(details_ds_file, fieldnames=[
            'index',
            'campus',
            'class',
            'situationBond',
            'organizationalUnit',
            'campus',
            'hasTrustPosition',
            'employeeSince',
            'urlRemunerationSufix'
        ])

        csvwriter.writeheader()

        """
        for employee_index in employees_basics:
            scrapping_threads_q.put(Thread(
                target=_scrap_employee_details,
                args=(employees_basics, employee_index, details_ds_file)
            ))

        active_scrapping_threads = []
        for i in range(MAX_HTTP_CONNECTIONS):
            active_scrapping_threads[i] = None

        while not scrapping_threads_q.empty():
            for i in range(MAX_HTTP_CONNECTIONS):

                if active_scrapping_threads[i] is None:
                    if not scrapping_threads_q.empty():
                        active_scrapping_threads[i] = scrapping_threads_q.get()

                if active_scrapping_threads[i] is not None:
                    if not active_scrapping_threads[i].is_alive():
                        active_scrapping_threads[i].start()

            time.sleep(1)

        if scrapping_threads_q.empty():
            print("Todas as requisições foram feitas.")
        """
        for i in range(3):

            employee_index = str(i)
            details = _scrap_employee_details(employees_basics, employee_index)

            print('Reading {}: {}...'.format(employee_index, employees_basics[employee_index]['name']))
            details['index'] = employee_index

            if 'CAMPUS' in details['organizationalUnit']:
                for unit in details['organizationalUnit'].split('/'):
                    if 'CAMPUS' in unit.upper():
                        details['campus'] = unit.strip()
            else:
                details['campus'] = details['organizationalUnit'].split('/')[0].strip()

            if 'campus' not in details:
                details['campus'] = ''

            csvwriter.writerow(details)




def _scrap_employee_details(employees_basics: dict, employee_key: str):
    employee_details = {}

    url_details_sufix = employees_basics[employee_key]['urlDetailsSufix']

    details_response = urlopen(_employee_details_url(url_details_sufix))
    details_soup = BeautifulSoup(details_response, 'html.parser')

    # get its link for $$$

    remuneration_url_sufix = details_soup.find('a', title='Remuneração individual do servidor').get('href')
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

    return employee_details if employee_details else None




def report_employees_remunerations():
    pass




def _employees_search_url(page_num: int):
    base_ifrn = URL_ROOT_EMPLOYEES + 'OrgaoExercicio-ListaServidores.asp?CodOS=15000&DescOS=MINISTERIO%20DA%20EDUCACAO&CodOrg=26435&DescOrg=INSTITUTO%20FEDERAL%20DO%20RIO%20GRANDE%20DO%20NORTE&Pagina='
    return base_ifrn + str(page_num)




def _employee_details_url(url_sufix: str):
    return URL_ROOT_EMPLOYEES + url_sufix


# routines

#report_employees_basics()
report_employees_details()
