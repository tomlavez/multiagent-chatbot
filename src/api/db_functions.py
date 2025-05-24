# Configuração do Banco de Dados
import sqlite3
import json


# Funções de Cadastro e Login
def cadastrar_usuario(username, password, email):
    conn = sqlite3.connect("database/usuarios.sqlite")
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username = ? OR email = ?", (username, email))
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
    conn = sqlite3.connect("database/usuarios.sqlite")
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



