import streamlit as st

# Configuración de página y estilo oscuro
st.set_page_config(page_title="OSECAC IA", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
st.title("🤖 Buscador OSECAC")
st.write("Bienvenido al asistente inteligente para agencias.")

# Simulación de Chat estilo Streamly
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte con el nomenclador?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        st.markdown("Buscando en tus documentos... (Pronto conectaremos Gemini)")
