🤖 Smart AMS - Agente de Suporte L1 (GenAI)

O Smart AMS é um assistente virtual inteligente voltado para suporte Nível 1. Ele analisa sintomas relatos em chamados, consulta uma base de conhecimento em PDF (Instruções de Trabalho - ITs) através de busca híbrida (semântica + palavras-chave) e sugere soluções fundamentadas usando o modelo Google Gemini.

🛠️ Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

Python 3.10 ou superior

Git

🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e executar o aplicativo em sua máquina local:

1. Clonar o Repositório

git clone https://github.com/JacksonAlves-dev/Smart-Ams.git
cd Smart-Ams


2. Criar e Ativar um Ambiente Virtual (Recomendado)

# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate


3. Instalar as Dependências

Instale todos os pacotes necessários especificados no requirements.txt:

pip install -r requirements.txt


4. Configurar a Chave da API do Gemini

Você pode criar um arquivo .env na raiz do projeto com a sua chave da API do Google Gemini:

GOOGLE_API_KEY=sua_chave_aqui


Nota: Caso você não crie o arquivo .env, o próprio sistema solicitará a chave diretamente na interface gráfica na primeira vez em que for executado.

5. Executar a Aplicação

Inicie a interface gráfica desenvolvida em Streamlit com o comando:

streamlit run SmartAms.py


🤖 Download Automático do Modelo de IA

Este projeto utiliza o modelo de embeddings all-MiniLM-L6-v2 para realizar a busca semântica no banco vetorial.

Automático: Na primeira vez que você executar o aplicativo, o sistema detectará que os arquivos do modelo não estão presentes na pasta models/ e fará o download automático diretamente do Hugging Face.

Nas execuções seguintes, o modelo será carregado diretamente da pasta local, garantindo rapidez e funcionamento offline para essa etapa.

📁 Estrutura da Base de Conhecimento

Insira os arquivos em formato PDF com os procedimentos e ITs na pasta docs/ (pode ser feito diretamente pelo painel lateral da interface).

O sistema reindexará o banco de dados vetorial (chroma_db/) automaticamente para responder às dúvidas com base nos novos arquivos.
