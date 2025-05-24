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
if "calendar_auth" not in st.session_state:
    st.session_state.calendar_auth = False
if "calendar_permissions" not in st.session_state:
    st.session_state.calendar_permissions = ""
if "redirect_to_login" not in st.session_state:
    st.session_state.redirect_to_login = False

# Definindo as opções de permissões
PERMISSION_OPTIONS = {
    "readonly": {
        "label": "🔍 Apenas Leitura",
        "description": "Visualizar eventos do calendário",
        "capabilities": ["Visualizar eventos", "Buscar eventos por data/participantes"],
        "restrictions": ["Não pode criar eventos", "Não pode editar eventos", "Não pode deletar eventos"]
    },
    "read_update": {
        "label": "📝 Leitura e Edição",
        "description": "Visualizar e modificar eventos existentes",
        "capabilities": ["Visualizar eventos", "Buscar eventos", "Editar eventos existentes", "Atualizar detalhes de eventos"],
        "restrictions": ["Não pode criar novos eventos", "Não pode deletar eventos"]
    },
    "full_access": {
        "label": "🔧 Acesso Completo",
        "description": "Controle total do calendário",
        "capabilities": ["Visualizar eventos", "Buscar eventos", "Criar novos eventos", "Editar eventos existentes", "Deletar eventos", "Gerenciar calendários secundários"],
        "restrictions": []
    }
}

menu = ["Login", "Cadastro"]
choice = st.sidebar.radio("Menu", options=menu)

# Redirect to login after successful registration
if st.session_state.redirect_to_login:
    choice = "Login"
    st.session_state.redirect_to_login = False

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
                st.session_state.redirect_to_login = True
                st.rerun()
            else:
                st.error(res.json()["detail"])

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        
        # Seleção de permissões do calendário
        st.subheader("🗓️ Permissões do Google Calendar")
        st.write("Escolha o nível de acesso que você deseja para o calendário:")
        
        permission_choice = st.radio(
            "Selecione as permissões:",
            options=list(PERMISSION_OPTIONS.keys()),
            format_func=lambda x: PERMISSION_OPTIONS[x]["label"],
            help="Diferentes níveis de permissão determinam quais ações o chatbot pode realizar no seu calendário"
        )
        
        # Mostrar detalhes da permissão selecionada
        selected_permission = PERMISSION_OPTIONS[permission_choice]
        
        with st.expander("ℹ️ Detalhes da Permissão Selecionada", expanded=False):
            st.write(f"**{selected_permission['label']}**")
            st.write(selected_permission['description'])
            
            if selected_permission['capabilities']:
                st.write("**✅ Funcionalidades disponíveis:**")
                for capability in selected_permission['capabilities']:
                    st.write(f"• {capability}")
            
            if selected_permission['restrictions']:
                st.write("**❌ Restrições:**")
                for restriction in selected_permission['restrictions']:
                    st.write(f"• {restriction}")
        
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/login", 
                json={
                    "username": username, 
                    "password": password,
                    "calendar_permissions": permission_choice
                }
            )
            if res.status_code == 200:
                response_data = res.json()
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = response_data["token"]
                st.session_state.calendar_auth = response_data.get("calendar_auth", False)
                st.session_state.calendar_permissions = response_data["calendar_permissions"]
                
                # Display login success message
                st.success(response_data["message"])
                
                # Show permission status
                st.success(f"Permissão selecionada: {selected_permission['label']}")
                
                # If calendar authentication is needed/succeeded
                if st.session_state.calendar_auth:
                    st.success("Autenticação com Google Calendar realizada com sucesso!")
                else:
                    st.warning("Não foi possível autenticar com o Google Calendar. Algumas funcionalidades podem estar limitadas.")
            elif res.status_code == 400:
                st.warning(res.json()["detail"])
            else:
                st.warning(res.json()["detail"])
            
            st.rerun()
else:
    st.subheader(f"Chatbot - Usuário: {st.session_state.username}")

    # Show calendar authentication and permission status
    with st.sidebar:
        st.subheader("🗓️ Status do Calendar")
        if st.session_state.calendar_auth:
            st.success("Google Calendar: Conectado")
        else:
            st.warning("Google Calendar: Não conectado")
        
        # Show current permissions
        if st.session_state.calendar_permissions:
            perm_info = PERMISSION_OPTIONS[st.session_state.calendar_permissions]
            st.info(f"**Permissões:** {perm_info['label']}")
            
            # Option to change permissions
            if st.button("🔧 Alterar Permissões"):
                # Reset calendar auth to force re-authentication with new permissions
                st.session_state.calendar_auth = False
                headers = {"token": st.session_state.token}
                requests.post(f"{API_URL}/reset_calendar_auth", headers=headers)
                
                # Disconnect the user automatically
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.token = ""
                st.session_state.calendar_auth = False
                st.session_state.calendar_permissions = ""
                st.success("Usuário desconectado. Faça login novamente para alterar as permissões.")
                st.rerun()

    message = st.text_input("Você:")
    if st.button("Enviar") and message:
        # Obter resposta do chatbot
        headers = {"token": st.session_state.token}
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": message, "username": st.session_state.username},
                headers=headers,
            )
            
            if response.status_code == 200:
                res = response.json()["response"]
                st.text_area("Chatbot:", value=res, height=200)
            elif response.status_code == 401:
                st.warning(response.json()["detail"])
                st.session_state.redirect_to_login = True
                st.rerun()
            else:
                st.error("Erro ao comunicar com o servidor. Por favor, tente novamente.")
                
        except Exception as e:
            st.error(f"Erro durante a comunicação: {str(e)}")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.session_state.calendar_auth = False
        st.session_state.calendar_permissions = ""
        st.success("Você saiu com sucesso.")
        st.rerun()

