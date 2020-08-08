import json
import os
import time

import requests
from bs4 import BeautifulSoup

# BASE_URL = "https://stackoverflow.com/search?page={0}&tab=Relevance&q={1}"
BASE_URL = "https://stackoverflow.com/questions/tagged/{0}"
URL = "http://stackoverflow.com/search?q=%s"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def search(word):
    url = BASE_URL.format(word)
    response = requests.get(url)
    time.sleep(1.2)
    soup = BeautifulSoup(response.content, "html.parser")
    scraping(soup)


def scraping(sp_content):
    questions = sp_content.find("div", {"id": "questions"})
    questions_summary = sp_content.find_all("div", {"class": "question-summary"})
    el_info = [
        {  # Retorna asked/answered Mar 15 '13 by Mike Glaz
            "tipo": info.find("div", {"class": "user-action-time"}).get_text().strip(),
            # a data se encontra no título da tag span
            "data": info.find("div", {"class": "started"}).find('span')["title"],
            # Retorna a tag do usuário <a href="/users/1220190/mike-glaz">Mike Glaz</a>
            # Tratar depois, porque há casos em q é None
            "autor": info.find("div", {"class": "user-details"}).find("a").get_text().strip(),
            "titulo": info.find("a", {"class": "question-hyperlink"}).get_text().strip(),
            "texto": info.find("div", {"class": "excerpt"}).get_text().strip(),
            # Retorna uma lista de tags. Vazia se for uma answered
            "tags": info.find_all("a", {"class": "post-tag"})
        }
        for info in questions_summary[:30]  # Retornar apenas as 2 primeiras páginas
    ]
    de_json(el_info)


def de_json(info):
    perguntas, respostas, comentarios = [], [], []
    for i in range(len(info)):
        # Retorno a última posição da lista separada por "by".
        # autor = info[i]["tipo"].rsplit("by", 1)[-1].strip()  # Ex: João da string "asked Feb 15 '11 by João"
        # Retorno a primeira posição a lista que corresponde ao tipo do post, se answered ou asked
        tipo = info[i]["tipo"].split()[0].strip()  # Ex: 'asked 58 mins ago'
        if tipo == 'asked':
            tags = []
            for tg in info[i]["tags"]:
                tags.append(tg.text)
            perguntas.append({
                        "titulo": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"],
                        "tags": tags}
                )
            comentarios.append({
                        "pergunta": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"]}
                )
        else:
            respostas.append({
                        "titulo": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"]}
                )
            comentarios.append({
                        "resposta": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"]}
                )
    dados = {
        "perguntas": perguntas,
        "respostas": respostas,
        "comentarios": comentarios
    }
    name_file = os.path.join(BASE_DIR, "dados.json")
    with open(name_file, "w") as file:
        json.dump(dados, file, indent=4)
