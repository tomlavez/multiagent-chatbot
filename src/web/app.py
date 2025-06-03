import requests
import streamlit as st

API_URL = "http://localhost:8000"

# Streamlit App
st.title("Integration Chatbot")

# Initializing session state
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

# Defining permission options
PERMISSION_OPTIONS = {
    "readonly": {
        "label": "🔍 Read Only",
        "description": "View calendar events",
        "capabilities": ["View events", "Search events by date/participants"],
        "restrictions": ["Cannot create events", "Cannot edit events", "Cannot delete events"]
    },
    "read_update": {
        "label": "📝 Read and Edit",
        "description": "View and modify existing events",
        "capabilities": ["View events", "Search events", "Edit existing events", "Update event details"],
        "restrictions": ["Cannot create new events", "Cannot delete events"]
    },
    "full_access": {
        "label": "🔧 Full Access",
        "description": "Complete calendar control",
        "capabilities": ["View events", "Search events", "Create new events", "Edit existing events", "Delete events", "Manage secondary calendars"],
        "restrictions": []
    }
}

menu = ["Login", "Register"]
choice = st.sidebar.radio("Menu", options=menu)

# Redirect to login after successful registration
if st.session_state.redirect_to_login:
    choice = "Login"
    st.session_state.redirect_to_login = False

if not st.session_state.logged_in:
    if choice == "Register":
        st.subheader("New User Registration")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_email = st.text_input("Email")
        if st.button("Register"):
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
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Calendar permissions selection
        st.subheader("🗓️ Google Calendar Permissions")
        st.write("Choose the level of access you want for the calendar:")
        
        permission_choice = st.radio(
            "Select permissions:",
            options=list(PERMISSION_OPTIONS.keys()),
            format_func=lambda x: PERMISSION_OPTIONS[x]["label"],
            help="Different permission levels determine which actions the chatbot can perform on your calendar"
        )
        
        # Show details of selected permission
        selected_permission = PERMISSION_OPTIONS[permission_choice]
        
        with st.expander("ℹ️ Selected Permission Details", expanded=False):
            st.write(f"**{selected_permission['label']}**")
            st.write(selected_permission['description'])
            
            if selected_permission['capabilities']:
                st.write("**✅ Available features:**")
                for capability in selected_permission['capabilities']:
                    st.write(f"• {capability}")
            
            if selected_permission['restrictions']:
                st.write("**❌ Restrictions:**")
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
                st.success(f"Selected permission: {selected_permission['label']}")
                
                # If calendar authentication is needed/succeeded
                if st.session_state.calendar_auth:
                    st.success("Google Calendar authentication completed successfully!")
                else:
                    st.warning("Could not authenticate with Google Calendar. Some features may be limited.")
            elif res.status_code == 400:
                st.warning(res.json()["detail"])
            else:
                st.warning(res.json()["detail"])
            
            st.rerun()
else:
    st.subheader(f"Chatbot - User: {st.session_state.username}")

    # Show calendar authentication and permission status
    with st.sidebar:
        st.subheader("🗓️ Calendar Status")
        if st.session_state.calendar_auth:
            st.success("Google Calendar: Connected")
        else:
            st.warning("Google Calendar: Not connected")
        
        # Show current permissions
        if st.session_state.calendar_permissions:
            perm_info = PERMISSION_OPTIONS[st.session_state.calendar_permissions]
            st.info(f"**Permissions:** {perm_info['label']}")
            
            # Option to change permissions
            if st.button("🔧 Change Permissions"):
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
                st.success("User logged out. Please log in again to change permissions.")
                st.rerun()

    message = st.text_input("You:")
    if st.button("Send") and message:
        # Get chatbot response
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
                st.error("Error communicating with server. Please try again.")
                
        except Exception as e:
            st.error(f"Error during communication: {str(e)}")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.session_state.calendar_auth = False
        st.session_state.calendar_permissions = ""
        st.success("You have successfully logged out.")
        st.rerun()

