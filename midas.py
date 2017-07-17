"""
Scrapping public information from government about its colleges in Brazil, RN.
The results will be at report files, in JSON format.

TODO: find all IFRN's professors names by campus.
TODO: find all IFRN's professors basic details.
TODO: find all IFRN's professors remunerations.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup


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


def report_employees_init(): # currently only the first page
    """
    Scrapes data from generic search about employees names.
    """

    with open('./reports/all_employees.json', 'w') as all_employees_file:

        all_employees_file.write('{\n')
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

                    all_employees_file.write((
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

        all_employees_file.write('}\n')

    print("Reached the end after {0} pages and {1} employees found.".format(page_num-1, employees_index))

'''
def report_employees_basic_details():
    """
    Scrapes data from generic search about employees common details and organize them by campus.
    The result will be at report files.
    """

    search_response = urlopen(_employees_search_url(1))
    search_soup = BeautifulSoup(search_response, 'html.parser')

    employees_table = search_soup.find(id='listagem').find('table')
    employees_rows = employees_table.find_all('tr')
    del employees_rows[0]

    for employees_row in employees_rows:
        employee = {}

        cpf, name, _ = employees_row.find_all('td')

        employee['name'] = name.text.title()
        employee['cpf'] = cpf.text

        url_details_sufix = name.find('a').get('href')

        employee_response = urlopen(_employee_details_url(url_details_sufix))
        employee_soup = BeautifulSoup(employee_response, 'html.parser')
        details_tbody = employee_soup.find('table', summary='Detalhes do Servidor').find('tbody')
        
        for details_row in details_tbody:
            title, content = details_row.find('td')
            title = title.text
            for interest_key, interest_title in EMPLOYEES_INTERESTING_DETAILS_TITLES.items():
                if interest_title in title:
                    employee[interest_key] = content.text
        
        days_file = open(, 'a')
'''


def report_employees_remunerations():
    """
    It needs employees basic details.
    TODO
    """
    pass



def _employees_search_url(page_num: int):
    base_ifrn = URL_ROOT_EMPLOYEES + 'OrgaoExercicio-ListaServidores.asp?CodOS=15000&DescOS=MINISTERIO%20DA%20EDUCACAO&CodOrg=26435&DescOrg=INSTITUTO%20FEDERAL%20DO%20RIO%20GRANDE%20DO%20NORTE&Pagina='
    return base_ifrn + str(page_num)



def _employee_details_url(url_sufix: str):
    return URL_ROOT_EMPLOYEES + url_sufix



def _employee_remuneration_url(url_sufix: str):
    pass
    #return URL_ROOT_EMPLOYEES + 'http://www.portaldatransparencia.gov.br/servidores/Servidor-DetalhaRemuneracao.asp?Op=2&IdServidor=2140100&CodOrgao=26435&CodOS=15000&bInformacaoFinanceira=True'


report_employees_init()
