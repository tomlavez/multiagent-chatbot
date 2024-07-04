<h1 align = "center"> ChatBot techlab <h1>

## 📝 Sumário

- [Motivação](#-motivação)
- [Resumo](#-resumo)
- [Instalação](#️-instalação)
- [Execução](#️-execução)

## 🤩 Motivação

<p align = "justify">Este projeto teve como motivação um desafio feito pela <a href="https://www.tech4h.com.br/">Tech4.ai</a> com o objetivo de desenvolver um agente conversacional que facilite a integração de novos funcionários na empresa ajudando-os a se familiarizar rapidamente com a cultura, políticas, programas e ferramentas de trabalho da empresa.</p>

## 📝 Resumo

<p align = "justify">O projeto se consiste em uma aplicação de um chatbot, utilizando diferentes agentes com funções e ferramentas distintas. Além disso ele apresenta um sistema de agendamento de eventos no google agendas, porém só é possível agendar e consultar eventos existentes. Nota-se que só será possível consultar eventos que foram marcados pelo próprio chatbot, visto que ele estará associado a uma agenda própria. Para acessar o chat, será necessário criar um cadastro, fornecendo nome, senha e email. O acesso de todas as funcionalidades é feito através de verbos HTTP que acionarão a Api do projeto.</p>

## 🔧 Instalação

### Clonando o repositório

<p align = "justify">Vá até a pasta local desejada e execute o seguinte comando.</p>

```
git clone https://github.com/tomlavez/techlab-IAG-2024.git
```

### Instalado as dependências

<p align = "justify">Após clonar o repositório será necessário instalar as bibliotecas utilizadas no projeto. Para isso, basta utilizar o seguinte comando</p>

```
pip install -r requirements.txt
```

### Configurando .env

<p align = "justify">Para rodar esse projeto são necessárias três chaves de api, que devem ser alocadas no arquivo .env, como no exemplo abaixo</p>

```
GROQ_API_KEY=XXXXXXXXXXXXXXXXXXX
TAVILY_API_KEY=XXXXXXXXXXXXXXXXXXX
HUGGINGFACEHUB_API_TOKEN=XXXXXXXXXXXXXXXXXXX
```

### Google Cloud Console Account

<p align = "justify"> Utilizaremos a API do google para automatizar a criação de eventos no Google Agendas. Para fazer isso é necessário ter uma conta, onde todos os eventos marcados estarão, a qual pode ser criada <a href="https://console.cloud.google.com/welcome/new">aqui</a> e configurada seguindo este <a href="https://developers.google.com/calendar/api/quickstart/python?hl=pt-br">link</a>. Após isso será necessário baixar o json do OAuth 2.0 e adicionar ao projeto com nome de credentials.json.

### Api

<p align = "justify"> Como padrão do framework FastApi, a api está rodando em http://localhost:8000, definido no arquivo app.py na variável API_URL.

## ⚙️ Execução

<p align = "justify"> Para executar o projeto são necessários dois comandos, um para iniciar a api e outro para iniciar o frontend da aplicação, são eles: </p>

```
uvicorn api:app --reload

streamlit run .\app.py
```

<p align = "justify"> A depender do ambiente pode ser necessário adicionar "python -m" antes dos comandos </p>
