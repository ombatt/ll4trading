from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

'''
metodo che carica i documenti markdown e crea i chunk
'''


def load_and_split_markdown() -> [Document]:
    """
    Carica i documenti da una cartella e li divide in chunk.
    """
    # Usiamo DirectoryLoader per caricare tutti i file .md
    loader = DirectoryLoader("./docs/",
                             glob="**/*.md",
                             loader_cls=TextLoader,
                             loader_kwargs={'encoding': 'utf-8'})
    documents = loader.load()

    # Suddividiamo i documenti in chunk più piccoli
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    return split_docs


'''
metodo che crea il vector store
'''


def create_vector_store(split_docs) -> Chroma:
    """
    Trasforma i chunk in embeddings e li memorizza in un Vector Store.
    """
    # Inizializza il modello di embedding di Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Crea un Vector Store persistente con ChromaDB
    db = Chroma.from_documents(split_docs, embeddings, persist_directory="./chroma_db")
    return db


'''
crea la catena rag con il prompt dedicato per l'analisi finanziaria
'''


def create_rag_chain_with_custom_prompt(vector_store):
    """
    Crea la catena RAG utilizzando un prompt personalizzato.
    """

    # 3.1. Definisci il prompt personalizzato
    template = """
    Answer the question considering the following context:
    {context}

    the question is: {query}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 3.2. Inizializza il modello Gemini Flash
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

    # 3.3. Crea la catena
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    rag_chain = (
            {"context": retriever, "query": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain
