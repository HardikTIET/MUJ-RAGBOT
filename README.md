# RAG-Based Chatbot with Admin/Student Roles

This is a web application built with Streamlit that implements a Retrieval-Augmented Generation (RAG) chatbot. It features a secure, dual-role system for administrators and students, allowing for easy knowledge base management and interaction.

## ✨ Key Features

* **Role-Based Login System:** Secure access for two distinct user roles:
    * **Admin:** Manages the application's users and knowledge base.
    * **Student:** Interacts with the chatbot.
* **Admin Panel:**
    * Create and delete student user accounts.
    * Upload PDF documents to build a persistent knowledge base using a FAISS vector store.
    * View a list of all documents currently in the knowledge base.
    * A "Danger Zone" to securely and completely delete the knowledge base for a fresh start.
* **Student Chat Interface:**
    * An intuitive chat interface to ask questions based on the uploaded documents.
    * **Streaming Responses:** Answers from the AI appear word-by-word for a dynamic user experience.
    * **Feedback Mechanism:** Users can provide "👍" or "👎" feedback on the quality of each answer.
    * **Copy to Clipboard:** Easily copy the chatbot's answers.
    * **Example Questions:** Helps guide new users on how to interact with the bot.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend & Orchestration:** LangChain
* **LLM:** Google Gemini Pro
* **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
* **Vector Store:** FAISS (for local similarity search)
* **Database:** SQLite (for user credentials, PDF metadata, and feedback logging)

## 🚀 Local Setup and Installation

Follow these steps to run the application on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/HardikTIET/MUJ-RAGBOT.git](https://github.com/HardikTIET/MUJ-RAGBOT.git)
cd MUJ-RAGBOT
```

### 2. Install Dependencies

Ensure you have Python 3.8+ installed. Then, install the required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Set Up Google API Key

The application requires a Google API key to use the Gemini model.

1.  Create a folder named `.streamlit` in the root of the project directory.
2.  Inside the `.streamlit` folder, create a file named `secrets.toml`.
3.  Add your API key to this file in the following format:
    ```toml
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
    ```

## ▶️ How to Run the Application

1.  Open your terminal in the project's root directory.
2.  Run the following command:
    ```bash
    streamlit run app.py
    ```
3.  The application will open in your default web browser.

### Default Admin Login

You can log in as an administrator using the default credentials:

* **Username:** `admin`
* **Password:** `admin`
