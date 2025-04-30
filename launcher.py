import os
import streamlit as st

######## Fixer l'image en haut de la page ########
with st.container():
    image_path = "labo.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"L'image {image_path} est introuvable.")

# Interface de sélection du mode d'exécution
st.title("🖥️ Sélection du mode d'exécution")
type_execution = st.radio("Choisissez le mode d'exécution", ["Local", "Cloud"])

if st.button("Lancer l'application"):
    if type_execution == "Local":
        st.write("🔹 Lancement de la version locale...")
        os.system("streamlit run local.py")  # Exécute le fichier local.py
    elif type_execution == "Cloud":
        st.write("🔹 Lancement de la version cloud...")
        os.system("streamlit run cloud.py")  # Exécute le fichier cloud.py
    else:
        st.error("❌ Choix invalide. Relancez et sélectionnez Local ou Cloud.")

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
