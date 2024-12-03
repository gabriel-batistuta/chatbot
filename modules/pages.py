from bs4 import BeautifulSoup
from requests import get
import json
import pdfplumber
import io
import re
import pymupdf

class Tree:
    def __init__(self, url, links_div):
        self.url = url
        self.initial_links_div = links_div
        self.children = []

def pdf_text_to_utf_8(raw_text):
    # Decodificar caracteres Unicode, se necessário (caso seja em bytes)
    try:
        # Caso o texto esteja em bytes
        if isinstance(raw_text, bytes):
            raw_text = raw_text.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"Erro ao decodificar: {e}")

    # Remover caracteres de controle (como '\u0000') usando regex
    clean_text = re.sub(r'\\u0000', '', raw_text)  # Remove caracteres '\u0000'

    # Alternativamente, substituir caracteres indesejados por um espaço
    clean_text = re.sub(r'[^\x20-\x7E\n]', ' ', clean_text)

    # Exibir o texto limpo
    print("Texto Decodificado e Limpado:")
    print(clean_text)

def html_table_to_dict(table):
    """
    Converte uma tabela HTML em um dicionário.
    """
    rows = table.find_all('tr')
    headers = [header.text for header in rows[0].find_all('th')]
    data = [dict(zip(headers, [cell.text for cell in row.find_all('td')])) for row in rows[1:]]
    return data

def get_text_from_page(page, link):
    if link.strip().endswith('.pdf'):
        pdf_stream = pymupdf.open(stream=get(link).content, filetype="pdf")  # Abrir PDF em memória
        text = []
        
        for page_number in range(len(pdf_stream)):
            page = pdf_stream[page_number]
            page_text = page.get_text().encode("utf8")  # Extrai o texto da página

            # Decodificar bytes, caso necessário
            if isinstance(page_text, bytes):
                page_text = page_text.decode('utf-8', errors='ignore')

            # Limpar caracteres não imprimíveis ou indesejados
            # page_text = re.sub(r'[^\x20-\x7E\n]', '', page_text)

            text.append(f"Página {page_number + 1}:\n{page_text.strip()}")
        
        pdf_stream.close()
        print('\n'.join(text))
        return '\n'.join(text)
    page.find('')
    return page.text.strip()

def get_soup(url:str):
    """
    Realiza uma requisição HTTP para a URL e retorna o objeto BeautifulSoup com a página HTML.
    """
    response = get(url)
    return BeautifulSoup(response.text, 'html.parser')

def extract_links(soup:BeautifulSoup, div:dict):
    """
    Extrai os links de um determinado elemento HTML (ex.: links internos) e retorna uma lista.
    """
    '''
    'tag':'div',
        'attr': {
            'data-id':'cb5e2c3'
        }
    '''
    key, value = tuple(div['attr'].items())[0]
    # print(div['attr'].keys())
    # key, value = tuple(div['attr'])
    # print('key: ',key, '\nvalue: ', value)
    # print('tag: ', div['tag'])
    page = soup.find(div['tag'], attrs={key:value})
    links = []
    for link in page.find_all('a', href=True):
        links.append(link['href'])
    return links

if __name__ == '__main__':
    uern_tree = Tree('https://portal.uern.br/portaldatransparencia/gratificacoes/', {
        'tag':'div',
        'attr': {
            'data-id':'cb5e2c3'
        }
    })
    soup = get_soup(
            uern_tree.url
        )
    div = uern_tree.initial_links_div
    # Extrai os links dos nós internos da árvore
    links = extract_links(soup, div)

    pages = [

    ]

    for link in links:
        print(link)
        page = get_soup(link)
        page_title = page.title.string if page.title else "Sem título"  # Converte para string
        print(page_title)
        page_content = {
            "name": "search",
            "parameters": {
                "link": link,  # Inclui o link da página
                "title": page_title,  # Título da página
                "text": get_text_from_page(page, link)  # Texto associado à página
            }
        }
        pages.append(page_content)
        # print(page_content)

    # Salva os dados em um arquivo JSON
    with open('file.json', 'w', encoding='utf-8') as f:
        json.dump({'pages':pages}, f, indent=4, ensure_ascii=False)