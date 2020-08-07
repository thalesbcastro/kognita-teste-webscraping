import json
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://stackoverflow.com/search?page={0}&tab=Relevance&q={1}"
URL = "http://stackoverflow.com/search?q=%s"


def search(word):
    url = URL % word
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def scraping(sp_content):
    main_block = sp_content.find_all("div", {"class": "question-summary search-result"})
    informations_ = [
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
    return informations_


def de_json(info):
    perguntas, respostas, comentarios = [], [], []
    for i in range(len(info)):
        # Retorno a última posição da lista separa por "by".
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
    sp = search("nginx")
    info_ = scraping(sp)
    de_json(info_)
