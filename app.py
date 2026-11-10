import streamlit as st
import google.generativeai as genai

# Configuração visual da página
st.set_page_config(
    page_title="Assistente de Ingresso Acadêmico",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Tira-Dúvidas de Ingresso Universitário")
st.caption("Assistente virtual inteligente alimentado pelas diretrizes e editais oficiais.")

# 1. Configurar Chave da API com segurança (obtida dos Secrets do Streamlit Cloud)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
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

# 3. Inicializar o histórico de mensagens do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico de conversas na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. Entrada do usuário (input do chat)
if prompt := st.chat_input("Digite sua dúvida (ex: Como funciona a isenção de taxa?):"):
    # Adicionar mensagem do usuário ao histórico e exibi-la
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Prompt Engineering com RAG estrito (Instruções de comportamento)
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
        # Configurar e chamar o modelo gemini-1.5-flash
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando o edital oficial..."):
                response = model.generate_content(prompt)
                resposta_texto = response.text
                st.write(resposta_texto)
                
        # Salvar resposta do assistente no histórico
        st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
        
    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"Ocorreu um erro ao processar sua solicitação: {e}")