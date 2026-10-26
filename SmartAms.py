import os

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==========================================
# CONFIGURAÇÃO INICIAL (CHAVE GEMINI)
# ==========================================
load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))

if not os.environ.get("GOOGLE_API_KEY"):
    st.set_page_config(page_title="Smart AMS - Configuração", page_icon="🔑")
    st.title("🤖 Smart AMS: Configuração Inicial")
    st.warning("⚠️ Chave **GOOGLE_API_KEY** não detectada.")
    api_key_input = st.text_input(
        "Insira sua chave do Google Gemini (API Key):",
        type="password",
        placeholder="AIzaSy...",
        help="Obtenha sua chave gratuitamente em https://aistudio.google.com/"
    )
    if st.button("Salvar e Iniciar"):
        if api_key_input.strip():
            env_file = os.path.join(base_dir, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"GOOGLE_API_KEY={api_key_input.strip()}\n")
            os.environ["GOOGLE_API_KEY"] = api_key_input.strip()
            st.success("✅ Chave salva com sucesso! Iniciando...")
            st.rerun()
        else:
            st.error("Por favor, digite uma chave válida.")
    st.stop()

DOCS_DIR = os.path.join(base_dir, "docs")
DB_DIR = os.path.join(base_dir, "chroma_db")

# Abaixo do qual a resposta do retriever é considerada pouco relevante e o
# app responde direto, sem gastar uma chamada de LLM.
LIMIAR_RELEVANCIA = 0.25

st.set_page_config(page_title="Smart AMS - L1 Agent", page_icon="🤖")
st.title("🤖 Smart AMS: Agente de Suporte L1 (GenAI)")


# ==========================================
# BACKEND (HuggingFace + ChromaDB) — cacheados
# ==========================================
# Certifique-se de que o import está no topo do ficheiro (caso não esteja):
# from sentence_transformers import SentenceTransformer

@st.cache_resource
def get_embeddings():
    """Garante o download local do modelo na primeira vez e devolve o objeto de embeddings."""
    local_model_path = os.path.join(base_dir, "models", "all-MiniLM-L6-v2")
    
    # Se o modelo ainda não existe na pasta local 'models/'
    if not os.path.exists(local_model_path):
        st.toast("📥 Baixando modelo de embeddings para a pasta local...", icon="⏳")
        print("[INFO] Modelo local não encontrado. Baixando da Hugging Face...", flush=True)
        
        # Descarrega do Hugging Face e guarda na pasta local
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        model.save(local_model_path)
        
        print(f"[INFO] Modelo salvo em: {local_model_path}", flush=True)
    
    # O LangChain passa a carregar o modelo diretamente do caminho local
    return HuggingFaceEmbeddings(model_name=local_model_path)


@st.cache_resource
def carregar_base_de_conhecimento():
    """Retorna (retriever_hibrido, vectorstore) ou (None, None) se não há PDFs.

    O vectorstore é retornado separadamente para permitir checar o score de
    relevância antes de decidir se vale a pena chamar o LLM.
    """
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        return None, None

    # 1. Carregar documentos PDF
    loader = PyPDFDirectoryLoader(DOCS_DIR)
    docs = loader.load()

    if not docs:
        return None, None

    # 2. Dividir o texto em blocos
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 3. Busca Semântica (ChromaDB)
    embeddings = get_embeddings()

    # Limpa qualquer coleção antiga antes de recriar — sem isso, cada vez
    # que essa função roda (ex: após "Atualizar Conhecimento"), os PDFs
    # eram adicionados de novo em cima dos que já existiam, duplicando
    # os chunks e distorcendo os resultados de busca.
    vectorstore_existente = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    try:
        vectorstore_existente.delete_collection()
    except Exception:
        pass  # coleção pode não existir ainda na primeira execução

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_DIR,
    )
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 4. Busca por Palavras-Chave (BM25)
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 3

    # 5. Busca Híbrida (Semântica 50% + Palavras-chave 50%)
    retriever_hibrido = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5]
    )
    return retriever_hibrido, vectorstore


retriever_hibrido, vectorstore = carregar_base_de_conhecimento()

# ==========================================
# BARRA LATERAL (Administração da base de documentos)
# ==========================================
with st.sidebar:
    st.header("⚙️ Administração")
    st.write("Adicione novos documentos à base da IA:")

    novo_arquivo = st.file_uploader("Faça upload de um PDF", type=["pdf"])

    if novo_arquivo is not None:
        caminho_salvar = os.path.join(DOCS_DIR, novo_arquivo.name)
        with open(caminho_salvar, "wb") as f:
            f.write(novo_arquivo.getbuffer())

        st.success(f"✅ Arquivo '{novo_arquivo.name}' recebido!")

        if st.button("🔄 Atualizar Conhecimento da IA"):
            st.cache_resource.clear()
            st.rerun()

    st.divider()

    if st.button("🧹 Limpar e Recriar Base Vetorial"):
        try:
            embeddings = get_embeddings()
            vs_temp = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
            vs_temp.delete_collection()

            st.cache_resource.clear()
            st.success("Base vetorial limpa com sucesso!")
            st.rerun()

        except Exception as e:
            st.warning(f"Aviso ao apagar arquivos: {e}")
            st.info(
                "A coleção foi resetada. Se os arquivos persistirem, recarregue a página."
            )

# ==========================================
# CONFIGURAÇÃO DO MODELO GEMINI
# ==========================================
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,  # 0 = mais determinístico, reduz "criatividade"/alucinação
)

system_prompt = (
    "Você é um assistente virtual inteligente de suporte nível 1 da Softtek. "
    "Sua missão é ajudar analistas a resolver chamados interpretando os sintomas relatados e aplicando a Instrução de Trabalho (IT) adequada. "
    "Se o usuário descrever um sintoma (ex: 'erro de senha' ou 'não consigo logar'), faça a dedução lógica de qual procedimento resolve o problema (ex: resetar a senha) usando APENAS o contexto fornecido. "
    "Inicie a resposta explicando rapidamente a sua linha de raciocínio (ex: 'Como o usuário não consegue logar, o procedimento indicado é o reset de senha.') e depois liste o passo a passo em bullet points. "
    "Se as ITs fornecidas não resolverem o problema de forma alguma, diga que não encontrou o procedimento e sugira escalar o chamado. "
    "Sempre cite o nome do documento base no final da sua resposta."
    "\n\n"
    "Documentos de contexto:\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

if retriever_hibrido:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever_hibrido, question_answer_chain)
else:
    st.warning(f"⚠️ Nenhuma documentação encontrada. Coloque PDFs na pasta '{DOCS_DIR}'.")

# ==========================================
# INTERFACE DO CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def _stream_resposta(rag_chain, pergunta, chunks_coletados):
    """Gera só o texto da resposta (para st.write_stream) e guarda os chunks
    brutos em chunks_coletados para extrairmos o 'context' (fontes) depois."""
    for chunk in rag_chain.stream({"input": pergunta}):
        chunks_coletados.append(chunk)
        if "answer" in chunk:
            yield chunk["answer"]


if prompt_usuario := st.chat_input("Ex: Como atendo uma BRM?"):
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    if retriever_hibrido:
        with st.chat_message("assistant"):
            # --- Checagem de relevância ANTES de chamar o LLM ---
            # Evita gastar tempo (e correr risco de alucinação) quando a
            # pergunta não tem relação com nenhum documento da base.
            with st.status("🔎 Buscando documentos relevantes...", expanded=False) as status:
                print("[DEBUG] iniciando similarity_search_with_relevance_scores", flush=True)
                resultados = vectorstore.similarity_search_with_relevance_scores(
                    prompt_usuario, k=3
                )
                print(f"[DEBUG] retrieval concluído, {len(resultados)} resultados", flush=True)
                for doc, score in resultados:
                    nome = os.path.basename(doc.metadata.get("source", "?"))
                    print(f"[DEBUG] score={score:.4f}  fonte={nome}  trecho={doc.page_content[:60]!r}", flush=True)
                status.update(label="✅ Busca concluída", state="complete")

            melhor_score = resultados[0][1] if resultados else 0

            if not resultados or melhor_score < LIMIAR_RELEVANCIA:
                texto_resposta = (
                    "Não encontrei um procedimento (IT) que resolva esse "
                    "sintoma na base de conhecimento atual. Recomendo "
                    "escalar o chamado."
                )
                st.warning(texto_resposta)
                st.session_state.messages.append(
                    {"role": "assistant", "content": texto_resposta}
                )
            else:
                try:
                    print("[DEBUG] chamando o Gemini via rag_chain.stream()", flush=True)
                    with st.spinner("🤖 Consultando o Gemini..."):
                        chunks_coletados = []
                        texto_resposta = st.write_stream(
                            _stream_resposta(rag_chain, prompt_usuario, chunks_coletados)
                        )
                    print("[DEBUG] resposta do Gemini recebida", flush=True)

                    # Extrai o contexto (documentos-fonte) dos chunks do stream
                    contexto = []
                    for c in chunks_coletados:
                        if "context" in c:
                            contexto = c["context"]

                    if contexto:
                        fontes = set(doc.metadata["source"] for doc in contexto)
                        st.markdown("📄 **Documentos de referência encontrados:**")

                        for caminho_arquivo in fontes:
                            nome_arquivo = os.path.basename(caminho_arquivo)
                            try:
                                with open(caminho_arquivo, "rb") as pdf_file:
                                    pdf_bytes = pdf_file.read()

                                st.download_button(
                                    label=f"📥 Baixar {nome_arquivo}",
                                    data=pdf_bytes,
                                    file_name=nome_arquivo,
                                    mime="application/pdf",
                                )
                            except FileNotFoundError:
                                st.error(
                                    f"⚠️ O arquivo {nome_arquivo} não foi encontrado na pasta."
                                )

                    st.session_state.messages.append(
                        {"role": "assistant", "content": texto_resposta}
                    )

                except Exception as e:
                    erro_msg = str(e)
                    if "429" in erro_msg or "RESOURCE_EXHAUSTED" in erro_msg:
                        st.warning(
                            "⏳ **Estou recebendo muitas mensagens!** Atingimos o "
                            "limite de segurança do plano gratuito. Por favor, "
                            "aguarde 1 minuto e tente enviar a pergunta novamente."
                        )
                    else:
                        st.error(f"⚠️ Ocorreu um erro inesperado: {erro_msg}")