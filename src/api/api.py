from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel
import sqlite3
from .db_functions import cadastrar_usuario, login_usuario
from ..agents.agents_main import bot_main
import secrets
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Calendar API scopes para diferentes permissões
CALENDAR_SCOPES = {
    "readonly": ["https://www.googleapis.com/auth/calendar.readonly"],
    "read_update": ["https://www.googleapis.com/auth/calendar.events"],
    "full_access": ["https://www.googleapis.com/auth/calendar"]
}

app = FastAPI()

# Inicialização do Banco de Dados
def init_db():
    conn = sqlite3.connect("database/usuarios.sqlite")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

# Armazenamento temporário de tokens (em produção, usar um banco de dados)
tokens: Dict[str, Dict] = {}


# Definição dos modelos Pydantic
class UserCadastro(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str
    calendar_permissions: str = "full_access"  # Default permission


class Message(BaseModel):
    message: str
    username: str


# Função para verificar o token de autenticação
def get_current_user(token: str = Header(...)):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens[token]


def get_permission_capabilities(permission_level: str) -> Dict[str, bool]:
    """
    Retorna as capacidades baseadas no nível de permissão
    """
    capabilities = {
        "can_read": False,
        "can_create": False,
        "can_update": False,
        "can_delete": False
    }
    
    if permission_level == "readonly":
        capabilities["can_read"] = True
    elif permission_level == "read_update":
        capabilities["can_read"] = True
        capabilities["can_update"] = True
    elif permission_level == "read_create_update":
        capabilities["can_read"] = True
        capabilities["can_create"] = True
        capabilities["can_update"] = True
    elif permission_level == "full_access":
        capabilities["can_read"] = True
        capabilities["can_create"] = True
        capabilities["can_update"] = True
        capabilities["can_delete"] = True
    
    return capabilities


# Função para validar/criar credenciais do Google Calendar
def check_calendar_credentials(user_email: str, permission_level: str = "full_access"):
    """
    Verifica ou cria credenciais para o Google Calendar com base no nível de permissão.
    Retorna True se as credenciais estiverem válidas, False caso contrário.
    """
    creds = None
    scopes = CALENDAR_SCOPES.get(permission_level, CALENDAR_SCOPES["full_access"])
    
    # Caminho personalizado para o token do usuário com base na permissão
    token_path = f"auth/tokens/{user_email}_{permission_level}_token.json"
    os.makedirs("auth/tokens", exist_ok=True)
    
    # Verificar se as credenciais existem e são válidas
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    
    # Se não há credenciais ou elas não são válidas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Se o refresh falha, reautorizar
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("config/credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        
        # Salvar as credenciais para o próximo uso
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            
        return True
    
    return creds.valid


# Rota para cadastro de usuário
@app.post("/register")
def register(user: UserCadastro):
    user.username = user.username.lower()
    result = cadastrar_usuario(user.username, user.password, user.email)
    if "sucesso" in result.lower():
        return {"message": result}
    else:
        raise HTTPException(status_code=400, detail=result)


# Rota para login de usuário
@app.post("/login")
def login(user: UserLogin):
    user.username = user.username.lower()
    logged_user = login_usuario(user.username, user.password)
    if logged_user:
        # Obter o email do usuário
        conn = sqlite3.connect("database/usuarios.sqlite")
        c = conn.cursor()
        c.execute("SELECT email FROM usuarios WHERE username = ?", (user.username,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Usuário não encontrado na base de dados")
        
        user_email = result[0]
        
        # Verificar se o nível de permissão é válido
        if user.calendar_permissions not in CALENDAR_SCOPES:
            raise HTTPException(status_code=400, detail="Nível de permissão inválido")
        
        # Verificar/criar credenciais do Google Calendar com a permissão especificada
        credentials_valid = check_calendar_credentials(user_email, user.calendar_permissions)
        
        # Obter capacidades baseadas na permissão
        capabilities = get_permission_capabilities(user.calendar_permissions)
        
        # Gerar token de autenticação
        token = secrets.token_hex(16)
        tokens[token] = {
            "username": user.username, 
            "email": user_email,
            "calendar_permissions": user.calendar_permissions,
            "capabilities": capabilities
        }
        
        return {
            "message": f"Bem-vindo {user.username}", 
            "token": token, 
            "calendar_auth": credentials_valid,
            "calendar_permissions": user.calendar_permissions,
            "capabilities": capabilities
        }
    else:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")


# Rota para resetar autenticação do calendário
@app.post("/reset_calendar_auth")
def reset_calendar_auth(current_user: dict = Depends(get_current_user)):
    """
    Remove os tokens de autenticação do calendário para forçar nova autenticação
    """
    user_email = current_user["email"]
    
    # Remove todos os tokens de calendário do usuário
    import glob
    token_pattern = f"auth/tokens/{user_email}_*_token.json"
    for token_file in glob.glob(token_pattern):
        try:
            os.remove(token_file)
        except OSError:
            pass
    
    return {"message": "Autenticação do calendário resetada"}


# Rota para interação com o chatbot
@app.post("/chat")
def chat(message: Message, current_user: dict = Depends(get_current_user)):
    # Passar informações de permissão para o bot
    response = bot_main(
        message.message, 
        message.username,
        user_permissions=current_user.get("capabilities", {}),
        permission_level=current_user.get("calendar_permissions", "full_access")
    )
    return {"response": response}
