# Configuração do Banco de Dados
import sqlite3
import json


# Funções de Cadastro e Login
def cadastrar_usuario(username, password, email):
    conn = sqlite3.connect("usuarios.sqlite")
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    if c.fetchone():
        return "Usuário já existe."
    c.execute(
        "INSERT INTO usuarios (username, password, email) VALUES (?, ?, ?)",
        (username, password, email),
    )
    conn.commit()
    conn.close()
    return "Usuário cadastrado com sucesso."


def login_usuario(username, password):
    conn = sqlite3.connect("usuarios.sqlite")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM usuarios WHERE username = ? AND password = ?",
        (username, password),
    )
    user = c.fetchone()
    conn.close()
    if user:
        return user
    return None


def get_message_history(username):
    conn = sqlite3.connect("usuarios.sqlite")
    c = conn.cursor()
    c.execute(
        "SELECT message_history FROM historico_mensagens WHERE username = ?",
        (username,),
    )
    history = c.fetchone()
    conn.close()
    if history:
        return json.loads(history[0])
    return []


def save_message_history(username, chat_history):
    conn = sqlite3.connect("usuarios.sqlite")
    c = conn.cursor()
    c.execute("SELECT * FROM historico_mensagens WHERE username = ?", (username,))
    if c.fetchone():
        c.execute(
            "UPDATE historico_mensagens SET message_history = ? WHERE username = ?",
            (json.dumps(chat_history), username),
        )
    else:
        c.execute(
            "INSERT INTO historico_mensagens (username, message_history) VALUES (?, ?)",
            (username, json.dumps(chat_history)),
        )
    conn.commit()
    conn.close()


def add_user_message(chat_history, message):
    chat_history.append({"role": "user", "messages": message})


def add_ai_message(chat_history, message):
    chat_history.append({"role": "ai", "content": message})
