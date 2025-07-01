import streamlit as st
from database import create_tables, get_user, check_hashes

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RAG-Bot | Login",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- MAIN APPLICATION ---
def main():
    """Main function to run the Streamlit app"""
    st.title("Welcome to the RAG Chatbot! 🤖")
    st.sidebar.title("Login Section")

    # Initialize session state variables if they don't exist
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = ''
        st.session_state['confirm_delete'] = False


    # If the user is not logged in, show the login form
    if not st.session_state['logged_in']:
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")

        if st.sidebar.button("Login"):
            create_tables()
            user_data = get_user(username)

            if user_data:
                if check_hashes(password, user_data[2]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user_data[1]
                    st.session_state['role'] = user_data[3]
                    st.sidebar.success(f"✅ Logged in as {st.session_state['username']}")
                    st.rerun()
                else:
                    st.sidebar.warning("⚠️ Incorrect password.")
            else:
                st.sidebar.warning("⚠️ Username not found.")

        st.info("Please log in to proceed.")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.header("For Admins 🔑")
            st.markdown("""
            - Manage student accounts (create/delete).
            - Upload PDF documents to build the knowledge base.
            - View and clear the entire knowledge base.
            """)
        with col2:
            st.header("For Students 🎓")
            st.markdown("""
            - Interact with the intelligent chatbot.
            - Ask questions based on the uploaded documents.
            - View source document snippets for answers.
            """)

    # If the user is logged in, show a welcome message and a logout button
    else:
        st.success(f"Welcome, **{st.session_state['username']}**!")
        st.sidebar.success(f"✅ Logged in as {st.session_state['username']} ({st.session_state['role']})")

        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                if key not in ['logged_in', 'username', 'role']:
                    del st.session_state[key]
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.session_state['role'] = ''
            st.rerun()

        st.markdown(f"""
        You are logged in as an **{st.session_state['role']}**.
        Please navigate to the appropriate page using the sidebar to the left.
        """)

if __name__ == '__main__':
    main()
