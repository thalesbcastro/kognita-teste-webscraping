#### Requirements
Para rodar o programa, faz-se necessário instalar as dependências por meio do seguinte comando na raiz do projeto:

```markdown
pip install -r requirements.txt
```

O pacote **package01** contém a versão mais atual do programa (main_webscraping.py) e que será chamado pelo arquivo principal da aplicação 
_Flask_. Nele é disponibilizado apenas a função **search** como pode ser verificado no arquivo ```__init__.py``` desse pacote. Já, o **diretório** 
package00 contém a versão mais antiga (webscraping.py) como será explicado posteriormente. Essa versão não está sendo usada pela API,
mas pode ser testada passando para a função **search** a palavra a ser pesquisada, bem como a quantidade de páginas a serem retornadas, executando o arquivo normalmente:

```markdown
python package00/webscraping.py
```

Os parâmetros devem ser escritos dentro do arquivo:

```python
if __name__ == '__main__':
    # Nome a ser pesquisado mais a quantidade de páginas a ser retornada
    search("nginx", 2)
```

- Para a criação do arquivo, chamado, nesse projeto, de **dados.json**, optou-se por criá-lo através da url ```127.0.0.1:5000/api/create/nome_a_ser_pesquisado```. Desse modo, para criar 
o arquivo, com a aplicação rodando localmente, deve-se substituir **nome_a_ser_pesquisado** pela palavra que se deseja pesquisar.  

- Para consultar os dados, foi criada uma aplicação _Flask_ simples que retorna um _jsonify_, caso o usuário a ser pesquisado contenha informações no arquivo criado anteriormente. há uma **Obs** no final desse arquivo 
para um campo extra criado em comentários.

- Para visualizar os dados de algum autor, deve-se acessar o seguinte _endpoint_:
```markdown
http://127.0.0.1:5000/api/get/<autor>
```  
Onde **<autor>** deve ser substituído pelo nome do autor que se quer ver as informações.

#### Coleta dos Dados 
Para a coleta dos dados, há duas versões. A primeira versão, escrita em **webscraping.py**, foi realizada usando a seguinte URL: ```https://stackoverflow.com/search?q={nome_a_ser_pesquisado}```. 
Inicialmente, verificou-se que, ao realizar a pesquisa, o link inicial colocava a _querystring_ ```search?q={nome_a_ser_pesquisado}```, e que, ao paginar, substitua por ```search?page={nome_a_ser_pesquisado}&tab=Relevance&q={numero_da_pagina}```.
Dessa forma, pôde-se criar uma função que receberia o **nome** e a **quantidade de páginas** a serem raspadas:

```python
BASE_URL = "https://stackoverflow.com/search?page={0}&tab=Relevance&q={1}"


def search(word, pages):
    list_soup = []
    for p in range(pages):
        url = BASE_URL.format(p + 1, word)
        response = requests.get(url)
        time.sleep(1.2)
        # cada elemento da lista é um objeto bs4 com o parser da página
        list_soup.append(BeautifulSoup(response.content, "html.parser"))
    scraping(list_soup)
```  

No entanto, foi verificado que essa **URL** não funciona para todas as pesquisas. Um exemplo de uso adequado dela é com 
palavra **nginx**, passando também a quantidade de páginas. Porém, passando a palavra **python**, outro comportamento pode 
ser observado: a url formada a partir da página inicial se transforma em ```https://stackoverflow.com/questions/tagged/nome_a_ser_pesquisad0```, tornando,
desse modo, a versão anterior inválida. 

Para isso, foi criada uma outra versão (main_webscraping.py) para esse comportamento, não passando o número de páginas e limitando sua quantidade 
em 30, pois, por padrão, é retornado 50 resultados, sendo que cada página tem apenas 15, como pode ser observado no trecho de código a seguir:
```python
el_info = [
        {  
            "tipo": info.find("div", {"class": "user-action-time"}).get_text().strip(),
            "data": info.find("div", {"class": "started"}).find('span')["title"],
            "autor": info.find("div", {"class": "user-details"}).find("a").get_text().strip(),
            "titulo": info.find("a", {"class": "question-hyperlink"}).get_text().strip(),
            "texto": info.find("div", {"class": "excerpt"}).get_text().strip(),
            "tags": info.find_all("a", {"class": "post-tag"})
        }
        for info in questions_summary[:30]  # Retornar apenas as 2 primeiras páginas
    ]
```
Nesse trecho, pode-se observar que os elementos são retornados apenas para as 30 primeiras questões (```questions_summary[:30]```).   

#### Algumas observações
- Para a primeira versão é mais fácil encontrar _posts_ com uma maior variedade (_asked_/_answered_);
- Para a segunda, passando a palavra **Python**, por exemplo, é difícil encontrar _posts_ _answered_;
- Um campo extra foi adicionado para os **Comentários** para que seja melhor visualizado quando for o comentário de uma
pergunta ou de uma resposta:

```python
def de_json(info):
    perguntas, respostas, comentarios = [], [], []
    for i in range(len(info)):
        tipo = info[i]["tipo"].split()[0].strip()  # Ex: 'asked 58 mins ago'
        if tipo == 'asked':
            # [...]
            comentarios.append({
                        # Quando for uma pergunta, o título da pergunta é adicionado a comentário
                        "pergunta": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"]}
                )
        else:
            # [...]
            comentarios.append({
                        # Quando for uma resposta, o título da pergunta é adicionado a comentário
                        "resposta": info[i]["titulo"],
                        "texto": info[i]["texto"],
                        "autor": info[i]["autor"],
                        "data": info[i]["data"]}
                )
        # [...]
```

- Uma coisa que não pode ser verificada foi a questão de expandir comentários, pois não consegui encontrar nenhum _post_
com esse comportamento.

#### API Flask
A "API" é uma simples aplicação em _Flask_ composta por duas funções:
- A primeira função realiza a criação do arquivo _.json_, acessando a url ```127.0.0.1:5000/api/create/nome_a_ser_pesquisado```; 
```python
@app.route('/api/create/<name>', methods=['GET'])
def de_json(name):
    try:
        search(name)
        return "<h3>Arquivo dados.json foi criado com sucesso na raiz do projeto!</h3>"
    except Exception as e:
        return f"<h3><b>Descupe! Algo não de muito certo {e}</b></h3>"
```

- A segunda, por sua vez, trata de retornar um _jsonify_, acessando  ```http://127.0.0.1:5000/api/get/<autor>```
- Resposta esperada, avessando o _endpoint_ anterior:
```json
{
   "perguntas" : [],
   "respostas" : [],
   "comentarios" : []
}
``` 
- Função responsável por retornar as informações do autor, caso ele as tenha:
```python
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
``` 