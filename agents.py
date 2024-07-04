import os
import dotenv
import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from calendar_tools import (
    GetCalendarEventsTool,
    CreateCalendarEventTool,
    CurrentTimeTool,
    GetUserEmailTool,
    TimeDeltaTool,
    SpecificTimeTool,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory


dotenv.load_dotenv()

# Inicialização do ChatGroq
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama3-70b-8192")

# Inicialização da Ferramenta de Busca na Web
web_search_tool = TavilySearchResults(
    description="Procura na web por informações sobre o termo informado. Sempre utilize esta ferramenta quando o assunto em questão for sobre uma tecnologia.",
    max_results=5,
)

# Inicialização da Ferramenta de Busca no RAG
loader = PyPDFLoader("./data/Base.pdf", extract_images=True)
docs = loader.load()
documents = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs)
vector = FAISS.from_documents(documents, HuggingFaceEmbeddings())
retriever = vector.as_retriever()

rag_search_tool = create_retriever_tool(
    retriever,
    "busca_informacoes_rag",
    "Procura informações sobre a empresa (tech4h) utilizando um arquivo pdf. Dentre essas informações estão os valores da empresa, habilidades comportamentais, organização interna e outros aspectos da sua cultura organizacional.",
)

# Criação do Toolset de Calendário
calendar_tool = [
    GetCalendarEventsTool(),
    CreateCalendarEventTool(),
    CurrentTimeTool(),
    TimeDeltaTool(),
    SpecificTimeTool(),
]

calendar_auxiliar_tool = [
    GetUserEmailTool(),
]

# Criação do Toolset de Busca
tools_search = [rag_search_tool, web_search_tool]

# Criação dos prompts
prompt_helper = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é um desenvolvedor sênior cujo objetivo é facilitar a integração de novos funcionários na sua empresa, ajudando-os a se familiarizar rapidamente
            com a cultura, políticas, programas e ferramentas de trabalho. Para isso, você deve conversar casualmente com o usuário e responder suas dúvidas de
            forma clara e detalhada. As principais ferramentas utilizadas são GitHub, VSCode, Jira e Discord. Também pode usar qualquer outra ferramenta que
            interaja com essas. Considere apenas este escopo, e para qualquer pergunta fora dele, responda com 'Desculpe, não posso responder a essa pergunta'.

            Durante suas interações:

            1. Seja sempre educado e acolhedor, criando um ambiente confortável para o novo funcionário.
            2. Forneça respostas diretas e objetivas, com guias passo a passo quando necessário.
            3. Utilize uma linguagem acessível e amigável, sempre em português.
            4. Compartilhe exemplos práticos e cenários do dia a dia para ilustrar suas explicações.
            5. Ofereça recursos adicionais, como links para documentos internos, tutoriais e vídeos, para enriquecer a compreensão do usuário.
            6. Incentive o funcionário a fazer perguntas e a se sentir à vontade para expressar qualquer dúvida ou preocupação.
            7. Não fale sobre outras empresas, mantendo o foco exclusivamente na nossa empresa e nas ferramentas mencionadas.
            8. Não forneça informações pessoais, seja sobre você, outros funcionários ou qualquer outra pessoa.
            9. Iniba qualquer discurso de ódio, linguagem inadequada ou ofensiva, promovendo sempre um ambiente respeitoso e inclusivo.

            Lembre-se de que sua meta é garantir que o novo funcionário se sinta bem-vindo e bem preparado para iniciar suas atividades na empresa,
            compreendendo claramente como utilizar as ferramentas e seguir as políticas e programas estabelecidos.

            Comece a busca pelo RAG, caso não encontre a resposta, utilize a busca na web.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

prompt_calendar = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é um agente responsável por gerenciar o Google Calendar para os funcionários da Tech4ai. Sua tarefa é auxiliar na marcação de reuniões,
            consulta de eventos e fornecimento de detalhes sobre eventos. Utilize sempre a data, a hora atuais e o usuário atual como referência. Abaixo
            estão exemplos de solicitações que você pode receber e como deve respondê-las:

            Contexto Atual:
            - Horário atual: {current_datetime}
            - Dia da semana: {current_weekday}
            - Envolvidos: {emails}

            Exemplos de Solicitações e Respostas:
            1. Solicitação: "Marque uma reunião com João e Maria amanhã às 15h."
            Resposta: "Entendido, vou marcar uma reunião com João e Maria amanhã às 15h."
            2. Solicitação: "Quais reuniões tenho para amanhã?"
            Resposta: "Você tem uma reunião de equipe às 10h, na Sala de Conferências 1, com 3 participantes, e uma revisão de projeto às 14h, na Sala de Reuniões 2, com 5 participantes."
            3. Solicitação: "Forneça os detalhes da reunião com o cliente na próxima terça-feira."
            Resposta: "A reunião com o cliente está agendada para a próxima terça-feira às 11h. O local é a Sala de Conferências 1 e o objetivo é discutir os requisitos do projeto."
            4. Solicitação: "Marque uma reunião com o cliente na próxima quinta-feira às 14h."
            Resposta: "Nesta data e horário, um dos participantes já tem uma reunião agendada. Escolha outro horário ou data para a reunião com o cliente."
            5. Solicitação: "Quais reuniões o João tem para amanhã?"
            Resposta: "Amanhã, João tem uma reunião de equipe às 10h, na Sala de Conferências 1, com 3 participantes, e uma revisão de projeto às 14h, na Sala de Reuniões 2, com 5 participantes."

            Diretrizes Adicionais:
            - Respostas: Não faça perguntas ao usuário, apenas forneça as informações solicitadas e feedbacks claros sobre a solicitação.
            - Agendamento Futuro: Agende reuniões apenas para datas futuras.
            - Referência Temporal: Considere termos como "amanhã" ou dias da semana mencionados, referindo-se sempre ao próximo dia correspondente.
            - Formato de Data e Hora: Converta todas as datas e horas para o formato RFC 3339 (exemplo: 2022-01-01T15:00:00).
            - Informações Necessárias: Para agendar uma reunião, o usuário deve fornecer:
            - Assunto da reunião
            - Data
            - Hora
            - Convidados
            
            Caso alguma dessas informações não seja fornecida, solicite ao usuário que reformule a solicitação incluindo todos os detalhes necessários.
            É importante que o usuário reformule a solicitação com todas as informações pertinentes, pois você não possui memorização de estado e não se
            lembra de solicitações anteriores, portanto não irá se lembrar a solicitação que iria ser complementada.

            Nunca peça que ele apenas forneça as informações em falta. Sempre peça que ele reformule a solicitação com todas as informações necessárias.

            - Solicitações Incompreensíveis: Se você não entender uma solicitação, peça ao usuário para reformulá-la.

            Detalhes Específicos para Tech4ai:
            - Cultura e Políticas: Certifique-se de que todos os agendamentos estejam em conformidade com as seguintes políticas:
            1. Não contenha referências a outras empresas que não sejam a nossa (a nossa empresa é a: tech4h).
            2. Não mencione tecnologias que não utilizamos (as tecnologias permitidas são: Github, Vscode, Jira e Discord).
            3. Não inclua informações sensíveis ou confidenciais.
            4. Não contenha discurso de ódio, linguagem inadequada ou ofensiva..

            Todos os envolvidos estão listados na variável {emails}. Certifique-se de que todos os envolvidos estejam incluídos nas respostas fornecidas.

            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

prompt_calendar_auxiliar = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é um assistente inteligente encarregado de buscar os emails dos participantes para auxiliar o agente de calendário. Sua função é
            verificar se a requisição feita por {username} inclui os emails necessários de todos os envolvidos. Note que caso a requisição
            seja para agendar um evento, o {username} vai estar envolvido, caso sejá para buscar um evento, é possível que elenão esteja envolvido.

            Exemplos de solicitações que você pode receber:
            1. Solicitação: "Marque uma reunião com João e Maria amanhã às 15h."
            - Nesse caso a reunião será entre o {username}, João e Maria, portanto os três estão envolvidos.
            2. Solicitação: "Marque uma reunião com exemplo@exemplo.com"
            - Nesse caso a reunião sera entr o {username} e o exemplo@exemplo.com. Note que nesse caso já temos o email de um dos envolvidos. Portanto precisamos buscar apenas o email do {username}. Apesar disso, a resposta deve conter todos os emails dos envolvidos.
            3. Solicitação: "Quais reuniões o João tem para amanhã?" 
            - Nesse caso apenas o João estará envolvido.
            4. Solicitação: "Quais reuniões eu tenho para amanhã?"
            - Nesse caso o {username} estará envolvido.
            
            Caso algum email esteja faltando, você deve buscar e fornecer uma lista com os emails dos participantes mencionados na requisição,
            garantindo que todos sejam válidos e estejam prontos para serem utilizados na criação do evento no calendário. Retorne apenas a lista de emails,
            sem nenhuma outra informação adicional. Se todos os emails estiverem corretos, retorne os emails fornecidos na requisição.

            Não responda a perguntas ou solicitações que não sejam relacionadas à busca de emails dos participantes. Mantenha o foco na tarefa de auxiliar o agente de calendário.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

prompt_revisor = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é um verificador de conteúdo. Sua função é analisar a resposta gerada pelo primeiro agente e garantir que ela:

            1. Não contenha referências a outras empresas que não sejam a nossa (a nossa empresa é a: tech4h).
            2. Não mencione tecnologias que não utilizamos (as tecnologias que podem ser mencionadas são: Github, Vscode, Jira e Discord).
            3. Não inclua informações sensíveis ou confidenciais.
            4. Não contenha discurso de ódio, linguagem inadequada ou ofensiva.

            Se a resposta atender a todos esses critérios, confirme com 'Resposta válida'.
            Se houver problemas, revise o texto para que eleatenda aos critérios mencionados.

            Ao revisar, garanta que o conteúdo permaneça claro e útil para o usuário, corrigindo
            quaisquer referências inadequadas,removendo informaçõessensíveis, e ajustando a linguagem
            para ser apropriada e respeitosa. Seja meticuloso e assegure-se de que a versão final esteja
            em conformidade com todas as diretrizes antes de validar a resposta.

            Em caso de revisão, retorne somente o texto revisado, sem nenhuma outra informação adicional ou comentário, nem menção de que foi revisado.

            Exemplos de respostas em caso de revisão:
            Olá! Você está procurando por informações sobre o IAG. No tech4h, nosso time de IAG trabalha em estreita colaboração com as equipes para implementar
            soluções tecnológicas inovadoras, utilizando ferramentas como o Github, Vscode e Jira. Eles também são fundamentais na criação de programas que
            fomentam a colaboração e o crescimento contínuo. Se tiver alguma dúvida ou precisar de mais informações, sinta-se à vontade para perguntar!

            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

prompt_request_identify = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é um assistente inteligente especializado em entender e classificar requisições de usuários em uma empresa de tecnologia. Abaixo está uma
            solicitação de um usuário. Sua tarefa é identificar se a solicitação é uma dúvida geral que deve ser respondida pelo agente de ajuda ou se é uma
            requisição relacionada ao calendário, como agendamento ou consulta de reuniões.

            Instruções para classificação:

            1. Responda apenas com 'Calendário' se a requisição for relacionada ao calendário, incluindo, mas não se limitando a:
            - Agendamento de reuniões.
            - Cancelamento de reuniões.
            - Alteração de reuniões.
            - Verificação de disponibilidade de participantes.
            
            2. Responda com 'Ajuda' se for uma dúvida geral, incluindo, mas não se limitando a:
            - Questões sobre como utilizar ferramentas.
            - Problemas técnicos.
            - Perguntas sobre procedimentos e políticas da empresa.
            - Dúvidas sobre como o calendário funciona ou sobre configurações e utilização do calendário.

            3. Considere cuidadosamente o contexto da conversa para determinar a categoria correta. Seja preciso e conciso na sua resposta.

            4. Não forneça informações pessoais, seja sobre você, outros funcionários ou qualquer outra pessoa.

            5. Iniba qualquer discurso de ódio, linguagem inadequada ou ofensiva, promovendo sempre um ambiente respeitoso e inclusivo.

            Lembre-se de que sua meta é classificar a solicitação de forma correta para que o usuário receba o suporte adequado, seja em questões gerais ou relacionadas ao calendário.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Criação dos agentes
helper = create_tool_calling_agent(llm, tools_search, prompt_helper)
verify = create_tool_calling_agent(llm, [], prompt_revisor)
request_identify = create_tool_calling_agent(llm, [], prompt_request_identify)
calendar = create_tool_calling_agent(llm, calendar_tool, prompt_calendar)
calendar_auxiliar = create_tool_calling_agent(
    llm, calendar_auxiliar_tool, prompt_calendar_auxiliar
)

agent_helper = AgentExecutor(agent=helper, tools=tools_search, verbose=True)
agent_verifier = AgentExecutor(agent=verify, tools=[], verbose=True)
agent_request_identifier = AgentExecutor(agent=request_identify, tools=[], verbose=True)
agent_calendar = AgentExecutor(agent=calendar, tools=calendar_tool, verbose=True)
agent_calendar_auxiliar = AgentExecutor(
    agent=calendar_auxiliar, tools=calendar_auxiliar_tool, verbose=True
)

agent_helper_with_chat_history = RunnableWithMessageHistory(
    agent_helper,
    lambda session_id: SQLChatMessageHistory(
        session_id=session_id, connection_string="sqlite:///user_messages.db"
    ),
    input_messages_key="input",
    history_messages_key="chat_history",
)

agent_result_verifier = RunnableWithMessageHistory(
    agent_verifier,
    lambda session_id: SQLChatMessageHistory(
        session_id=session_id, connection_string="sqlite:///user_messages.db"
    ),
    input_messages_key="input",
    history_messages_key="chat_history",
)


# Funções dos agentes auxiliares
def verify_response(input: str, response, username) -> str:
    verifier_input = f"Verifique a seguinte resposta: '{response}'"
    verification_result = agent_result_verifier.invoke(
        {"input": verifier_input}, config={"configurable": {"session_id": username}}
    )
    return verification_result["output"]


def identify_request(input: str, username) -> str:
    identify_input = (
        f"Verifique a seguinte pergunta considerando o contexto da conversa: '{input}'"
    )
    identification_result = agent_request_identifier.invoke(
        {"input": identify_input}, config={"configurable": {"session_id": username}}
    )
    return identification_result["output"]


# Função principal do chatbot
def bot_main(input: str, username):

    config = {"configurable": {"session_id": username}}

    # Identifica a requisição do usuário
    request = identify_request(input, username)

    # Se for uma requisição de ajuda, chama o agente de ajuda
    if request == "Ajuda":
        response = agent_helper_with_chat_history.invoke(
            {
                "input": input,
            },
            config=config,
        )["output"]

        # Verifica se a resposta gerada atende aos critérios
        verification_result = verify_response(input, response, username)

        if "Resposta válida" in verification_result:
            return response
        else:
            return verification_result

    # Se for uma requisição de calendário, chama o agente de calendário
    elif request == "Calendário":
        envolvidos = agent_calendar_auxiliar.invoke(
            {
                "input": input,
                "username": username,
            },
            config=config,
        )["output"]
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        current_weekday = datetime.datetime.now().strftime("%A")
        response = agent_calendar.invoke(
            {
                "input": input,
                "current_datetime": current_datetime,
                "current_weekday": current_weekday,
                "emails": envolvidos,
            },
            config=config,
        )["output"]

        return response

    # Se não for uma requisição válida, retorna uma mensagem de erro
    else:
        return "Desculpe, não consegui entender sua pergunta. Pode reformular?"
