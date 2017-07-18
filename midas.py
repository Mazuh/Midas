"""
Scrapping public information from government about its colleges in Brazil, RN.
The results will be at report files, in JSON format.

TODO: find all IFRN's professors basic details.
TODO: find all IFRN's professors remunerations.
"""

import json
import time

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

EMPLOYEES_CLASS_VALUES_LABELS = {
    'A': 'Adjunto A / Assistente A / Auxiliar',
    'B': 'Assistente',
    'C': 'Adjunto',
    'D': 'Associado',
    'E': 'Titular',
}

# some default values

MAX_CONNECTIONS = 5 # maximum number of requests that may be created at the same time

EMPLOYEES_BASICS_FILENAME = './reports/employees_basics.json'
EMPLOYEES_DETAILS_FILENAMES_MASK = './reports/{0}_employees_details.json' # 0: campus name


# here we go for the functions

def report_employees_basics(target_employees_basics_filename=EMPLOYEES_BASICS_FILENAME):
    """
    Scrapes data from generic search about employees names and puts them on a given filename.
    TODO: accept others than just IFRN
    """

    with open(target_employees_basics_filename, 'w') as employees_basics_file:

        employees_basics_file.write('{\n')
        employees_index = 0
        page_num = 1
        end = False

        while not end:
            print("Reading page {0}...".format(page_num))

            search_response = urlopen(_employees_search_url(page_num))
            search_soup = BeautifulSoup(search_response, 'html.parser')

            end = INVALID_QUERY_MSG in search_soup.find(id='conteudo').text

            if not end:

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




def report_employees_details(employees_basics_filename=EMPLOYEES_BASICS_FILENAME, target_details_filenames_mask=EMPLOYEES_DETAILS_FILENAMES_MASK):
    #employees_units = {} # key: unit name, value: list of employees dicts

    employees_basics = None
    with open(employees_basics_filename) as employees_basics_file:
        employees_basics = json.loads(employees_basics_file.read())

    details = _scrap_employee_details(employees_basics, '11')
    for detail_key, detail in details.items():
        print(detail_key + ': ' + str(detail))




def _scrap_employee_details(employees_basics: dict, employee_key: str):
    employee_details = {}

    url_details_sufix = employees_basics[employee_key]['urlDetailsSufix']
    name = employees_basics[employee_key]['name']

    details_response = urlopen(_employee_details_url(url_details_sufix))
    details_soup = BeautifulSoup(details_response, 'html.parser')

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
