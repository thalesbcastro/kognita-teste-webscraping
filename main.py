import json

from package01.main_webscraping import search
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/create/<name>/<int:num>', methods=['GET'])
def de_json(name, num):
    try:
        search(name, num)
        return "<h3>Arquivo dados.json foi criado com sucesso na raiz do projeto!</h3>"
    except Exception as e:
        return f"<h3><b>Descupe! Algo não deu muito certo {e}</b></h3>"


@app.route('/api/get/<autor>', methods=['GET'])
def info_autor(autor):
    try:
        with open("dados.json") as file:
            data = json.loads(file.read())
        perguntas = [c for c in data["perguntas"] if c['autor'] == autor]
        respostas = [c for c in data["respostas"] if c['autor'] == autor]
        comentarios = [c for c in data["comentarios"] if c['autor'] == autor]
        response = {
            "perguntas": perguntas,
            "respostas": respostas,
            "comentarios": comentarios
        }
        return jsonify(response)
    except FileNotFoundError:
        return jsonify(response="É preciso antes realizar a pesquisa para que o arquivo seja criado, usando a "
                                "URL 127.0.0.1:5000/api/create/<name>")


if __name__ == '__main__':
    app.run(debug=True)
