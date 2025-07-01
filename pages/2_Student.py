import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit.components.v1 import html
from database import add_feedback # Import the new feedback function

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Chat", page_icon="🎓", layout="wide")
st.title("🎓 Student Chat Interface")

# --- JAVASCRIPT FOR COPY TO CLIPBOARD ---
# This is a workaround for clipboard functionality in Streamlit
def get_copy_to_clipboard_html(text_to_copy):
    """Generates an HTML button that copies text to the clipboard."""
    # The text is encoded into the onclick attribute
    # Note: This has limitations on very long texts and special characters.
    text_for_js = text_to_copy.replace("\n", "\\n").replace("`", "\\`").replace("'", "\\'").replace('"', '\\"')
    return f"""
        <button onclick="
            const el = document.createElement('textarea');
            el.value = '{text_for_js}';
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            this.innerText = 'Copied!';
            setTimeout(() => {{ this.innerText = 'Copy'; }}, 1000);
        ">Copy</button>
    """

# --- STUDENT AUTHENTICATION ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'student':
    st.warning("Please log in as a student to view this page.")
    st.stop()

st.sidebar.success(f"Welcome, **{st.session_state.get('username', 'Student')}**!")

# --- CLEAR CHAT BUTTON ---
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with the course materials today?", "id": 0}]
    st.rerun()

# --- CONSTANTS & MODEL LOADING ---
FAISS_INDEX_PATH = "faiss_index"

@st.cache_resource
def load_dependencies():
    """Loads dependencies, returns db"""
    if not os.path.exists(FAISS_INDEX_PATH):
        st.error("Knowledge base not found. Please ask an admin to create it.")
        return None
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

db = load_dependencies()

@st.cache_resource
def load_llm():
    """Loads the LLM."""
    try:
        # --- MODIFICATION: Enable streaming ---
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=st.secrets["GOOGLE_API_KEY"],
                                      temperature=0.3, streaming=True)
    except Exception as e:
        st.error(f"Failed to load the language model: {e}")
        return None

llm = load_llm()

# --- RAG CHAIN SETUP ---
def create_rag_chain(db, llm):
    if db is None or llm is None: return None
    prompt_template = """
    You are a helpful study assistant. Use the context to answer the user's question.
    CONTEXT: {context}
    QUESTION: {question}
    ANSWER:
    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=db.as_retriever(search_kwargs={'k': 3}),
                                       return_source_documents=False, chain_type_kwargs={"prompt": PROMPT})

qa_chain = create_rag_chain(db, llm)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with the course materials today?", "id": 0}]

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i > 0:
            # Use columns for a cleaner layout of buttons
            col1, col2, col3 = st.columns([1, 1, 12])
            with col1:
                if st.button("👍", key=f"thumbs_up_{message['id']}", help="This answer was helpful"):
                    add_feedback(st.session_state['username'], st.session_state.messages[i-1]['content'], message['content'], 1)
                    st.toast("Thanks for your feedback!", icon="✅")
            with col2:
                if st.button("👎", key=f"thumbs_down_{message['id']}", help="This answer was not helpful"):
                    add_feedback(st.session_state['username'], st.session_state.messages[i-1]['content'], message['content'], -1)
                    st.toast("Thanks, we'll use this to improve.", icon="💡")
            with col3:
                 html(get_copy_to_clipboard_html(message['content']), height=38)


# --- EXAMPLE QUESTIONS ---
if len(st.session_state.messages) <= 1:
    st.info("Ask a question or try one of these examples:")
    example_questions = ["What is the main topic of the document?", "Summarize the key points.", "Who is the author?"]
    cols = st.columns(len(example_questions))
    for idx, question in enumerate(example_questions):
        if cols[idx].button(question):
            st.session_state.messages.append({"role": "user", "content": question, "id": len(st.session_state.messages)})
            st.rerun()


# --- HANDLE USER INPUT ---
if prompt := st.chat_input("Ask a question..."):
    if qa_chain is None:
        st.error("Chatbot not configured. Please contact an admin.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt, "id": len(st.session_state.messages)})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full_response = ""
            message_placeholder = st.empty()
            with st.spinner("🧠 Thinking..."):
                for chunk in qa_chain.stream({"query": prompt}):
                    full_response += chunk.get("result", "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response, "id": len(st.session_state.messages)})
