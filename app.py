import requests
import streamlit as st

API_URL = "http://localhost:8000"

# Streamlit App
st.title("Chatbot de Integração")

# Inicializando o estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "token" not in st.session_state:
    st.session_state.token = ""

menu = ["Login", "Cadastro"]
choice = st.sidebar.radio("Menu", options=menu)

if not st.session_state.logged_in:
    if choice == "Cadastro":
        st.subheader("Cadastro de Novo Usuário")
        new_user = st.text_input("Nome de Usuário")
        new_password = st.text_input("Senha", type="password")
        new_email = st.text_input("Email")
        if st.button("Cadastrar"):
            res = requests.post(
                f"{API_URL}/register",
                json={
                    "username": new_user,
                    "password": new_password,
                    "email": new_email,
                },
            )
            if res.status_code == 200:
                st.success(res.json()["message"])
            else:
                st.error(res.json()["detail"])

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/login", json={"username": username, "password": password}
            )
            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = res.json()["token"]
                st.success(res.json()["message"])
            else:
                st.warning(res.json()["detail"])
else:
    st.subheader(f"Chatbot - Usuário: {st.session_state.username}")

    flag = False

    message = st.text_input("Você:")
    if st.button("Enviar") and flag is False:
        flag = True

        # Obter resposta do chatbot
        headers = {"token ": st.session_state.token}
        res = requests.post(
            f"{API_URL}/chat",
            json={"message": message, "username": st.session_state.username},
            headers={"token": st.session_state.token},
        ).json()["response"]

        st.text_area("Chatbot:", value=res, height=200)
        flag = False

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.success("Você saiu com sucesso.")
