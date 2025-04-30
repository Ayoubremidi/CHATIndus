import os
import streamlit as st
import pandas as pd
import sqlite3
from langchain_groq import ChatGroq
from langchain.sql_database import SQLDatabase
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

######## Fixer l'image en haut de la page ########
with st.container():
    image_path = "labo.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"L'image {image_path} est introuvable.")

# ✅ Authentification
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.allowed_databases = []

user_roles = {
    "esteban": {"password": "esteban", "databases": ["car_retails.sqlite", "human_resources.sqlite", "sales.sqlite"]},
    "admin": {"password": "password", "databases": ["car_retails.sqlite", "human_resources.sqlite", "sales.sqlite"]},
    "rh": {"password": "rhpass", "databases": ["human_resources.sqlite", "sales.sqlite"]},
    "finance": {"password": "finpass", "databases": ["sales.sqlite"]}
}

if not st.session_state.authenticated:
    st.title("🔒 Authentification")
    username = st.text_input("Nom d'utilisateur", "")
    password = st.text_input("Mot de passe", "", type="password")
    if st.button("Se connecter"):
        if username in user_roles and password == user_roles[username]["password"]:
            st.session_state.authenticated = True
            st.session_state.user_role = username
            st.session_state.allowed_databases = user_roles[username]["databases"]
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")
    st.stop()

st.sidebar.markdown("""
    <div style='text-align: center;'>
        <h1>💬 ChatINDUS - CLOUD</h1>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <a href='https://filext.com/fr/online-file-viewer.html' target='_blank'>
        <button style='width: 100%; padding: 10px; font-size: 16px; background-color: #007bff; color: white; border: none; cursor: pointer;'>
            🔗 Visulaliser la Base de données
        </button>
    </a>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style='text-align: center;'>
        <h1>🔧 Paramètres</h1>
    </div>
""", unsafe_allow_html=True)
st.sidebar.write("Pose une question en langage naturel et obtiens une requête SQL exécutée sur la base de données.")

# ✅ Set API Key
os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"

# ✅ Initialize Llama-70B (Groq LLM)
llm = ChatGroq(model="llama-3.3-70b-versatile")

# ✅ Sélection de la base de données autorisée
selected_db = st.sidebar.selectbox("Sélectionnez une base de données", st.session_state.allowed_databases)
DB_PATH = selected_db  # SQLite attend un chemin de fichier valide
conn = sqlite3.connect(DB_PATH)

# ✅ Load Database Schema
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
database_schema = db.get_table_info()

# ✅ Prompt for SQL Query Generation
sql_generation_prompt = PromptTemplate(
    input_variables=["question", "database_schema"],
    template="""
    Generate an SQLite valid SQL query based on the given question and database schema.
### Database Schema:
{database_schema}

### User Question:
{question}

### Task: Return only the query based on the user question (without sql in the beginning) and database schema nothing else.

### SQL Query:
"""
)

sql_generation_chain = LLMChain(llm=llm, prompt=sql_generation_prompt)

result_generation_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "sql_result"],
    template="""
### User Question:
{question}

### SQL Query Used:
{sql_query}

### SQL Query Result:
{sql_result}

**
Generate a natural language response based on the SQL result.
"""
)
result_generation_chain = LLMChain(llm=llm, prompt=result_generation_prompt)

# ✅ Chat History in Streamlit Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ Display Previous Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ User Input
user_query = st.chat_input("Pose une question sur ta base de données...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    try:
        sql_query = sql_generation_chain.invoke({
            "question": user_query,
            "database_schema": database_schema
        })["text"].strip()

        df = pd.read_sql_query(sql_query, conn)
        str_result = df.to_string(index=False)
        
        if not df.empty:
            st.session_state.messages.append({"role": "assistant", "content": "Query result:", "dataframe": df})
            st.write("### Query Result:")
            st.dataframe(df)
        else:
            st.write("No results found.")
        
        final_response = result_generation_chain.invoke({
            "question": user_query,
            "sql_query": sql_query,
            "sql_result": str_result
        })["text"]
        
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        with st.chat_message("assistant"):
            st.markdown(final_response)
    except Exception as e:
        st.sidebar.write(f"❌ Error: {str(e)}")

# ✅ Ajout du footer fixe
with st.container():
    st.markdown("""
        <style>
            .footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: white;
                text-align: center;
                padding: 10px;
                font-size: 12px;
                border-top: 1px solid #ddd;
                z-index: 100;
            }
        </style>
        <div class='footer'>
            ©️ MADE BY : EL HADDAD / EL MADRASSI / REMIDI<br>
            ©️ SUPERVISED BY : Mr. ESTEBAN RUIZ BAUTISTA
        </div>
    """, unsafe_allow_html=True)


# ✅ Ajout de l'image dans la sidebar
with st.sidebar:
    image_path = "chat.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"L'image {image_path} est introuvable.")

