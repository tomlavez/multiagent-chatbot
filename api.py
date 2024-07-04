from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel
import sqlite3
from db_functions import cadastrar_usuario, login_usuario
from agents import bot_main
import secrets

app = FastAPI()


# Inicialização do Banco de Dados
def init_db():
    conn = sqlite3.connect("usuarios.sqlite")
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

# Dicionário para armazenar tokens de autenticação
tokens: Dict[str, str] = {}


# Definição dos modelos Pydantic
class UserCadastro(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class Message(BaseModel):
    message: str
    username: str


# Função para verificar o token de autenticação
def get_current_user(token: str = Header(...)):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens[token]


# Rota para cadastro de usuário
@app.post("/register")
def register(user: UserCadastro):
    result = cadastrar_usuario(user.username, user.password, user.email)
    if "sucesso" in result.lower():
        return {"message": result}
    else:
        raise HTTPException(status_code=400, detail=result)


# Rota para login de usuário
@app.post("/login")
def login(user: UserLogin):
    logged_user = login_usuario(user.username, user.password)
    if logged_user:
        token = secrets.token_hex(16)
        tokens[token] = user.username
        return {"message": f"Bem-vindo {user.username}", "token": token}
    else:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")


# Rota para interação com o chatbot
@app.post("/chat")
def chat(message: Message, token: str = Depends(get_current_user)):
    response = bot_main(message.message, message.username)
    return {"response": response}
