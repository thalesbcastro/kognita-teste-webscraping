#### Requirements
Para rodar o programa, faz-se necessário instalar as dependências por meio do seguinte comando na raiz do projeto:

```markdown
pip install -r requirements.txt
```

O pacote **package01** contém a versão mais atual do programa (main_webscraping.py) e que será chamado pelo arquivo principal da aplicação 
_Flask_, o _main.py_. Nele (package01) é disponibilizada apenas a função **search** como pode ser verificado no arquivo ```__init__.py``` desse pacote. Já, o **diretório** 
package00 contém a versão mais antiga (webscraping.py) como será explicado posteriormente. Essa versão não está sendo usada pela API,
mas pode ser testada passando para a função **search** a palavra a ser pesquisada, bem como a quantidade de páginas a serem retornadas, executando o arquivo normalmente:

```markdown
python package00/webscraping.py
```

Os parâmetros devem ser escritos dentro do arquivo:

```python
# execução da função search na versão mais antiga, a webscraping.py, dentro de package00.
if __name__ == '__main__':
    # Nome a ser pesquisado mais a quantidade de páginas a ser retornada
    search("nginx", 2)
```

- Para a criação do arquivo, chamado, nesse projeto, de **dados.json**, optou-se por criá-lo através da url ```127.0.0.1:5000/api/create/nome_a_ser_pesquisado/quantidade_de_paginas```. Desse modo, para criar 
o arquivo, com a aplicação rodando localmente, deve-se substituir **nome_a_ser_pesquisado** pela palavra que se deseja pesquisar, bem como **quantidade_de_paginas** pelo número de páginas que
o usuário quer que seja retornado.  

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

No entanto, foi verificado que essa **URL** não funciona para todas as pesquisas. Um exemplo de uso adequado dela é com a 
palavra **nginx**, passando também a quantidade de páginas. Porém, passando a palavra **python**, outro comportamento pode 
ser observado: a url formada a partir da página inicial se transforma em ```https://stackoverflow.com/questions/tagged/nome_a_ser_pesquisado```, tornando,
desse modo, a versão anterior inválida. 

Para isso, foi criada uma outra versão (main_webscraping.py), muito semelhante a anterior, baseando-se na seguinte URL:
```python
BASE_URL = "https://stackoverflow.com/questions/tagged/{0}?tab=newest&page={1}&pagesize=50"
```
Onde o **{0}** será substituído pelo nome passado na função **search** e 0 **{1}** pela quantidade de páginas que se quer retornar.
Vale ressaltar que o tamanho de cada página, observando a url anterior, é limitado em 50 resultados, retornando, desse modo, 100 _posts_ para 2 páginas, por exemplo.

#### Algumas observações
- Para a primeira versão é mais fácil encontrar _posts_ com uma maior variedade (_asked_/_answered_);
- Para a segunda, passando a palavra **Python**, por exemplo, é difícil encontrar _posts_ _answered_;
- Um campo extra foi adicionado para os **Comentários** para que seja melhor visualizado quando for o comentário de uma
pergunta ou de uma resposta:

```python
def de_json(info):
    # [...]
        # [...]
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
    # [...]
```

- Uma coisa que não pôde ser verificada foi a questão de expandir comentários, pois não consegui encontrar nenhum _post_
com esse comportamento.

#### API Flask
A "API" é uma simples aplicação em _Flask_ composta por duas funções:
- A primeira função realiza a criação do arquivo _.json_, acessando a url ```127.0.0.1:5000/api/create/nome_a_ser_pesquisado/numero_paginas_retornadas```; 
```python
@app.route('/api/create/<name>/<int:num>', methods=['GET'])
def de_json(name, num):
    try:
        search(name, num)
        return "<h3>Arquivo dados.json foi criado com sucesso na raiz do projeto!</h3>"
    except Exception as e:
        return f"<h3><b>Descupe! Algo não deu muito certo: {e}</b></h3>"
```

- A segunda, por sua vez, trata de retornar um _jsonify_, acessando  ```http://127.0.0.1:5000/api/get/<autor>/<numero_paginas>```
- Resposta esperada, acessando o _endpoint_ anterior:
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

#### Resumindo:
- Acessar ```127.0.0.1/api/create/nome_a_ser_pesquisado/quantidade_de_paginas``` para criar arquivo .json;
- Acesar ```127.0.0.1/api/get/nome_autor``` para acessar os dados do autor.  