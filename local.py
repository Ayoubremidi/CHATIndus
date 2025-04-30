import os
import streamlit as st
from premsql.generators import Text2SQLGeneratorHF
from premsql.executors import SQLiteExecutor
from premsql.agents.baseline.workers import BaseLineText2SQLWorker

######## Fixer l'image en haut de la page ########
with st.container():
    image_path = "labo.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"L'image {image_path} est introuvable.")

######## Authentification ########
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
        <h1>💬 ChatINDUS - LOCAL</h1>
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

######## Initialisation des générateurs ########
text2sql_generator = Text2SQLGeneratorHF(
    model_or_name_or_path="premai-io/prem-1B-SQL",
    experiment_name="text2sql_worker",
    type="test"
)

######## Sélection de la base de données ########
selected_db = st.sidebar.selectbox("Sélectionnez une base de données", st.session_state.allowed_databases)
db_connection_uri = f"sqlite:///{selected_db}"

######## Initialisation des Workers ########
text2sql_worker = BaseLineText2SQLWorker(
    db_connection_uri=db_connection_uri,
    generator=text2sql_generator,
    executor=SQLiteExecutor()
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "results" not in st.session_state:
    st.session_state.results = []

# Affichage des messages existants (Utilisateur et Chatbot)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Affichage des résultats précédents
for result in st.session_state.results:
    st.subheader("Résultats de la requête :")
    st.dataframe(result)

# Saisie de la requête utilisateur
user_query = st.chat_input("Pose une question sur ta base de données...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    try:
        text2sql_response = text2sql_worker.run(
            question=user_query,
            temperature=0.01
        )
        sql_query = text2sql_response.sql_string if text2sql_response else ""

        if not sql_query or not sql_query.lower().startswith(("select", "pragma", "with")):
            st.sidebar.error("⚠️ La requête SQL générée semble incorrecte.")
            st.stop()

        st.sidebar.write(f"📝 Requête SQL générée : {sql_query}")

        try:
            df_to_show = text2sql_response.show_output_dataframe()
            if df_to_show.empty:
                bot_response = "⚠️ Aucun résultat trouvé. Vérifiez que la base contient bien des données."
            else:
                st.subheader("Résultats de la requête :")
                st.dataframe(df_to_show)
                st.session_state.results.append(df_to_show)
                bot_response = "📊 Résultats mis à jour."
        except Exception as sql_error:
            bot_response = f"❌ Erreur SQL : {str(sql_error)}"

        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)

    except Exception as e:
        bot_response = f"⚠️ Une erreur est survenue : {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)

# Ajout du footer fixe
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
            © MADE BY : EL HADDAD / EL MADRASSI / REMIDI<br>
            © SUPERVISED BY : Mr.ESTEBAN RUIZ BAUTISTA
        </div>
    """, unsafe_allow_html=True)



# ✅ Ajout de l'image dans la sidebar
with st.sidebar:
    image_path = "chat.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"L'image {image_path} est introuvable.")

