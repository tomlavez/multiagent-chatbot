<h1 align = "center"> ChatBot techlab <h1>

## 📝 Sumário

- [Motivação](#-motivação)
- [Instalação](#️-instalação)

## 🤩 Motivação

<p align = "justify">Este projeto teve como motivação um desafio feito pela <a href="https://www.tech4h.com.br/">Tech4.ai</a> com o objetivo de desenvolver um agente conversacional que facilite a integração de novos funcionários na empresa ajudando-os a se familiarizar rapidamente com a cultura, políticas, programas e ferramentas de trabalho da empresa.</p>

## ⚙️ Instalação

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

<p align = "justify"> Utilizaremos a API do google para automatizar a criação de eventos no Google Agendas. Para fazer isso é necessário ter uma conta, a qual pode ser criada <a href="https://console.cloud.google.com/welcome/new">aqui</a> e configurada seguindo este <a href="https://developers.google.com/calendar/api/quickstart/python?hl=pt-br">link</a>. Após isso será necessário baixar o json do OAuth 2.0 e adicionar ao projeto com nome de credentials.json.
