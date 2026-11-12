import streamlit as st
from google import genai

# Configuração visual da página
st.set_page_config(
    page_title="Assistente de Ingresso Acadêmico",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Tira-Dúvidas de Ingresso Universitário")
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
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da faculdade. Como posso te ajudar com dúvidas sobre o vestibular, isenção ou matrícula?"}
    ]

# 4. Renderizar o histórico de mensagens de forma segura
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Capturar nova entrada do usuário
if prompt := st.chat_input("Digite sua dúvida aqui..."):
    # Adicionar mensagem do usuário ao estado
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prompt Engineering com RAG estrito
    system_instruction = f"""
    Você é um assistente virtual de atendimento oficial da faculdade para dúvidas de ingresso de novos alunos.
    Responda à dúvida do candidato EXCLUSIVAMENTE com base no CONTEXTO DO EDITAL fornecido abaixo.
    Se a resposta exata não estiver no contexto, seja educado, informe que a informação não consta no edital atual e oriente o usuário a entrar em contato com a secretaria acadêmica.
    Nunca invente prazos, valores, documentos ou regras. Sempre cite a seção ou o trecho do documento em que a resposta se baseia.

    ---
    CONTEXTO OFICIAL (EDITAL):
    {conhecimento_edital}
    ---
    """

    try:
        with st.chat_message("assistant"):
            with st.spinner("Analisando o edital oficial..."):
                prompt_completo = f"{system_instruction}\n\nPERGUNTA DO CANDIDATO: {prompt}"
                
                # Chamada utilizando o novo cliente Google GenAI
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt_completo,
                )
                resposta_texto = response.text
                st.markdown(resposta_texto)
                
        # Salvar resposta do assistente no histórico
        st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
        
    except Exception as e:
        error_msg = f"Ocorreu um erro ao processar: {e}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})