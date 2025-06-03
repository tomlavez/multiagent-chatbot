import os
import dotenv
import datetime

# Prompts
from src.agents.prompts.calendar import prompt_calendar, prompt_calendar_auxiliar
from src.agents.prompts.revisor import prompt_revisor
from src.agents.prompts.helper import prompt_helper
from src.agents.prompts.identifier import prompt_identifier

# Agno
from agno.storage.sqlite import SqliteStorage
from agno.tools.tavily import TavilyTools
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.pgvector import PgVector

# Tools
from src.tools.calendar_tools import (
    get_calendar_events,
    create_calendar_event,
    current_time_tool,
    time_delta_tool,
    specific_time_tool,
    get_user_email,
    edit_calendar_event,
    delete_calendar_event,
)

dotenv.load_dotenv("config/.env")

calendar_tools = [
    get_calendar_events,
    create_calendar_event,
    current_time_tool,
    time_delta_tool,
    specific_time_tool,
    edit_calendar_event,
    delete_calendar_event,
]

auxiliar_calendar_tools = [
    get_user_email,
]
 
tools_search = [TavilyTools()]

pdf_knowledge_base = PDFKnowledgeBase(
    path="data/Base.pdf",
    vector_db=PgVector(
        table_name="sentence_transformer_embeddings",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        embedder=SentenceTransformerEmbedder(id="sentence-transformers/all-mpnet-base-v2", dimensions=768)
    ), 
    reader=PDFReader(chunk=True), 
)

helper_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions=prompt_helper,
    tools=tools_search,
    storage=SqliteStorage(table_name="agent_sessions", db_file="database/tmp/data.db"),
    add_history_to_messages=True,
    num_history_runs=5,
    show_tool_calls=True,
    markdown=True,
    knowledge=pdf_knowledge_base,
    search_knowledge=True,
)
 
helper_agent.knowledge.load(recreate=True) 

verifier_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions=prompt_revisor,
    tools=[],
    markdown=True,
)

request_identifier_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions=prompt_identifier,
    tools=[],
    markdown=True,
)

calendar_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions=prompt_calendar,
    tools=calendar_tools,
    storage=SqliteStorage(table_name="agent_sessions", db_file="database/tmp/data.db"),
    add_history_to_messages=True,
    num_history_runs=5,
    show_tool_calls=True,
    markdown=True,
)

auxiliar_calendar_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    instructions=prompt_calendar_auxiliar,
    tools=auxiliar_calendar_tools,
    storage=SqliteStorage(table_name="agent_sessions", db_file="database/tmp/data.db"),
    add_history_to_messages=True,
    num_history_runs=5,
    show_tool_calls=True,
    markdown=True,
)

# Função principal do chatbot
def bot_main(user_input: str, username: str, user_permissions: dict = None, permission_level: str = "full_access"):

    # Default permissions se não fornecidas
    if user_permissions is None:
        user_permissions = {
            "can_read": True,
            "can_create": True,
            "can_update": True,
            "can_delete": True
        }
    
    # Criar contexto de permissões para os agentes
    permission_context = f"\n\nPERMISSÕES DO USUÁRIO - NÍVEL: {permission_level.upper()}\n"
    permission_context += "Capacidades autorizadas:\n"
    
    if user_permissions.get("can_read", False):
        permission_context += "✅ VISUALIZAR eventos do calendário\n"
    else:
        permission_context += "❌ VISUALIZAR eventos do calendário\n"
    
    if user_permissions.get("can_create", False):
        permission_context += "✅ CRIAR novos eventos\n"
    else:
        permission_context += "❌ CRIAR novos eventos - OPERAÇÃO NÃO AUTORIZADA\n"
    
    if user_permissions.get("can_update", False):
        permission_context += "✅ EDITAR eventos existentes\n"
    else:
        permission_context += "❌ EDITAR eventos existentes - OPERAÇÃO NÃO AUTORIZADA\n"
    
    if user_permissions.get("can_delete", False):
        permission_context += "✅ DELETAR eventos\n"
    else:
        permission_context += "❌ DELETAR eventos - OPERAÇÃO NÃO AUTORIZADA\n"
    
    permission_context += "\nIMPORTANTE: Você DEVE verificar as permissões antes de tentar executar qualquer operação. Se o usuário solicitar uma operação não autorizada, explique educadamente que essa funcionalidade não está disponível com o nível de permissão atual e sugira como alterar as permissões.\n"

    # Identifica a requisição do usuário
    request = request_identifier_agent.run(user_input + "\nUsuário: " + username + permission_context).content

    # Se for uma requisição de ajuda, chama o agente de ajuda
    if request == "Help" or ("Help" in request and len(request) > 15):
        response = helper_agent.run(user_input + "\nUsuário: " + username).content

        # Verifica se a resposta gerada atende aos critérios
        verification_result = verifier_agent.run(response).content

        if "Valid response" in verification_result:
            return response
        elif "Revised text:" in verification_result:
            res = verification_result.split("Revised text: ", 1)
            splitRes = str(res[1].strip())
            return splitRes
        else:
            return verification_result

    # Se for uma requisição de calendário, chama o agente de calendário.
    elif request == "Calendar" or ("Calendar" in request and len(request) > 20):
        envolvidos = auxiliar_calendar_agent.run(user_input + "\nUsuário: " + username).content

        if envolvidos == "Não foi possível encontrar o email de um dos convidados.":
            return envolvidos
        
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        current_weekday = datetime.datetime.now().strftime("%A")
        
        # Adicionar contexto de permissões para o agente de calendário
        calendar_input = (
            user_input + 
            "\nUsuário: " + username + 
            "\nDia de hoje: " + current_datetime + 
            "\nDia da semana: " + current_weekday + 
            "\nConvidados: " + envolvidos +
            permission_context
        )
        
        response = calendar_agent.run(calendar_input).content

        return response

    # Se não for uma requisição de ajuda ou calendário, verifica se a resposta gerada é válida
    else:
        response = verifier_agent.run(request).content

        if "Valid response" in response:
            return request
        elif "Revised text" in response:
            res = response.split("Revised text: ", 1)
            splitRes = str(res[1].strip())
            return splitRes
        else:
            return "Não foi possível responder a esta requisição. Por favor, tente novamente."
