import json
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://stackoverflow.com/search?page={0}&tab=Relevance&q={1}"
URL = "http://stackoverflow.com/search?q=%s"


def search(word, pages):
    list_soup = []
    for p in range(pages):
        url = BASE_URL.format(p + 1, word)
        response = requests.get(url)
        time.sleep(1.2)
        list_soup.append(BeautifulSoup(response.content, "html.parser"))
    return list_soup  # cada elemento da lista é um objeto bs4 com o parser da página


def scraping(sp_content_list):
    list_info = []
    for sp_content in sp_content_list:
        main_block = sp_content.find_all("div", {"class": "question-summary search-result"})
        el_info = [
            {  # Retorna asked/answered Mar 15 '13 by Mike Glaz
                "tipo": info.find("div", {"class": "started"}).get_text().strip(),
                # a data se encontra no título da tag span
                "data": info.find("div", {"class": "started"}).find('span')["title"],
                # Retorna a tag do usuário <a href="/users/1220190/mike-glaz">Mike Glaz</a>
                # Tratar depois, porque há casos em q é None
                # "usr": info.find("div", {"class": "started"}).find('a'),
                "titulo": info.find("div", {"class": "result-link"}).get_text().strip(),
                "texto": info.find("div", {"class": "excerpt"}).get_text().strip(),
                # Retorna uma lista de tags. Vazia se for uma answered
                "tags": info.find_all("a", {"class": "post-tag"})
            }
            for info in main_block
        ]
        list_info.append(el_info)  # cada elemento da lista representa as informações de cada página
    return list_info


def de_json(list_info):
    perguntas, respostas, comentarios = [], [], []
    for info in list_info:
        for i in range(len(info)):
            # Retorno a última posição da lista separada por "by".
            autor = info[i]["tipo"].rsplit("by", 1)[-1].strip()  # Ex: João da string "asked Feb 15 '11 by João"
            # Retorno a primeira posição a lista que corresponde ao tipo do post, se answered ou asked
            tipo = info[i]["tipo"].split()[0].strip()  # Ex: "asked" da string "asked Feb 15 '11 by João"
            if tipo == 'asked':
                tags = []
                for tg in info[i]["tags"]:
                    tags.append(tg.text)
                perguntas.append({
                            "titulo": info[i]["titulo"],
                            "texto": info[i]["texto"],
                            "autor": autor,
                            "data": info[i]["data"],
                            "tags": tags}
                    )
                comentarios.append({
                            "pergunta": info[i]["titulo"],
                            "texto": info[i]["texto"],
                            "autor": autor,
                            "data": info[i]["data"]}
                    )
            else:
                respostas.append({
                            "titulo": info[i]["titulo"],
                            "texto": info[i]["texto"],
                            "autor": autor,
                            "data": info[i]["data"]}
                    )
                comentarios.append({
                            "resposta": info[i]["titulo"],
                            "texto": info[i]["texto"],
                            "autor": autor,
                            "data": info[i]["data"]}
                    )
    dados = {
        "perguntas": perguntas,
        "respostas": respostas,
        "comentarios": comentarios
    }
    with open("dados.json", "w") as file:
        json.dump(dados, file, indent=4)


if __name__ == '__main__':
    sp = search("nginx", 2)  # lista com as duas pág content
    info_ = scraping(sp)  # lista com cada elemento representando as informações de cada página
    de_json(info_)
