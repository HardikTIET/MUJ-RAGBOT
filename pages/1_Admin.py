import streamlit as st
from database import (add_user, add_pdf_record, is_pdf_processed, get_all_pdfs,
                      get_all_students, delete_user, clear_all_pdfs)
import os
import shutil
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="🔑", layout="wide")
st.title("🔑 Admin Panel")

# --- ADMIN AUTHENTICATION ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.warning("You do not have permission to view this page. Please log in as an admin.")
    st.stop()

# --- CONSTANTS ---
FAISS_INDEX_PATH = "faiss_index"
UPLOADED_FILES_DIR = "uploaded_files"
os.makedirs(UPLOADED_FILES_DIR, exist_ok=True)

# --- UI TABS ---
tab1, tab2 = st.tabs(["📚 Knowledge Base Management", "👤 User Management"])

# --- KNOWLEDGE BASE MANAGEMENT TAB ---
with tab1:
    st.header("Upload and Process Documents")

    @st.cache_resource
    def get_embeddings_model():
        return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    embeddings = get_embeddings_model()

    @st.cache_resource
    def load_vector_store():
        if os.path.exists(FAISS_INDEX_PATH):
            return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            dummy_texts = [Document(page_content="initialization", metadata={"source": "dummy"})]
            db = FAISS.from_documents(dummy_texts, embeddings)
            db.save_local(FAISS_INDEX_PATH)
            return db

    db = load_vector_store()

    uploaded_file = st.file_uploader("Upload a PDF to the Knowledge Base", type="pdf", key="pdf_uploader")

    if uploaded_file is not None:
        if not is_pdf_processed(uploaded_file.name):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    file_path = os.path.join(UPLOADED_FILES_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    pdf_reader = PdfReader(file_path)
                    text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

                    if text:
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                        chunks = text_splitter.split_text(text=text)

                        documents = [Document(page_content=chunk, metadata={"source": uploaded_file.name}) for chunk in chunks]
                        db.add_documents(documents)

                        db.save_local(FAISS_INDEX_PATH)
                        add_pdf_record(uploaded_file.name)
                        st.success(f"✅ Successfully added '{uploaded_file.name}'!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Could not extract text from {uploaded_file.name}.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.info(f"ℹ️ The document '{uploaded_file.name}' has already been processed.")

    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("Current Knowledge Base")
        processed_files = get_all_pdfs()
        if processed_files:
            filenames = [file[0] for file in processed_files]
            st.table(filenames)
        else:
            st.info("No documents have been uploaded yet.")
    with col2:
        st.header("⚠️ Danger Zone")
        if st.button("Delete Entire Knowledge Base"):
            st.session_state.confirm_delete = True

        if st.session_state.get('confirm_delete'):
            st.warning("Are you sure you want to delete the ENTIRE knowledge base? This action cannot be undone.")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("YES, I AM SURE", type="primary"):
                    if os.path.exists(FAISS_INDEX_PATH):
                        shutil.rmtree(FAISS_INDEX_PATH)
                    if os.path.exists(UPLOADED_FILES_DIR):
                        shutil.rmtree(UPLOADED_FILES_DIR)
                        os.makedirs(UPLOADED_FILES_DIR, exist_ok=True)
                    clear_all_pdfs()
                    st.session_state.confirm_delete = False
                    st.success("Knowledge base has been cleared.")
                    # Invalidate the cached resource to force a reload
                    st.cache_resource.clear()
                    st.rerun()
            with col_cancel:
                if st.button("CANCEL"):
                    st.session_state.confirm_delete = False
                    st.rerun()


# --- USER MANAGEMENT TAB ---
with tab2:
    st.header("Create New Student")
    with st.form("new_user_form", clear_on_submit=True):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.form_submit_button("Create User"):
            if new_username and new_password:
                if add_user(new_username, new_password, "student"):
                    st.success(f"✅ User '{new_username}' created.")
                else:
                    st.error("⚠️ Username already exists.")
            else:
                st.warning("⚠️ Please provide all details.")

    st.divider()

    st.header("Manage Existing Students")
    student_users = get_all_students()
    if student_users:
        for user in student_users:
            username = user[0]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(username)
            with col2:
                if st.button("Delete", key=f"delete_{username}", type="secondary"):
                    delete_user(username)
                    st.rerun()
    else:
        st.info("No student accounts found.")
