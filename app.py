import streamlit as st
from google import genai

# Configuração visual da página
st.set_page_config(
    page_title="Assistente de Ingresso Acadêmico",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Dúvidas de Ingresso Universitário FAP")
st.caption("Assistente virtual inteligente alimentado pelas diretrizes e editais oficiais.")

# 1. Configurar o Cliente da API com a nova biblioteca (obtida dos Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Chave da API do Gemini não configurada. Adicione a chave nos 'Secrets' do painel do Streamlit Cloud.")
    st.stop()

# 2. Carregar a Base de Conhecimento (Arquivo TXT local)
@st.cache_data
def carregar_edital():
    try:
        with open("edital_ingresso.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Aviso: O arquivo 'edital_ingresso.txt' não foi encontrado na pasta do projeto."

conhecimento_edital = carregar_edital()

# 3. Inicializar o histórico de mensagens do chat no session_state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou JanAI, sua assistente virtual da faculdade. Como posso te ajudar com dúvidas sobre a FAP?"}
    ]

# 4. Renderizar o histórico de mensagens com avatares personalizados
for message in st.session_state.messages:
    # Escolhe o emoji/ícone com base no papel (assistant ou user)
    icone = "🎓" if message["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(message["role"], avatar=icone):
        st.markdown(message["content"])

# 5. Capturar nova entrada do usuário
if prompt := st.chat_input("Digite sua dúvida aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Avatar do usuário ao enviar
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant", avatar="🎓"): # Avatar do assistente
            with st.spinner("Analisando o edital oficial..."):
                prompt_completo = f"{system_instruction}\n\nPERGUNTA DO CANDIDATO: {prompt}"
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt_completo,
                )
                resposta_texto = response.text
                st.markdown(resposta_texto)
                
        st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
        
    except Exception as e:
        ...