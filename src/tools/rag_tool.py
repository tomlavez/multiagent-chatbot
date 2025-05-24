from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Inicialização da Ferramenta de Busca no RAG
try:
    loader = PyPDFLoader("./data/Base.pdf", extract_images=True)
    docs = loader.load()
    documents = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100
    ).split_documents(docs)
    vector = FAISS.from_documents(documents, HuggingFaceEmbeddings())
    retriever = vector.as_retriever(search_kwargs={"k": 3})
    RAG_AVAILABLE = True
except Exception:
    RAG_AVAILABLE = False
    retriever = None

def search_knowledge_base(query: str) -> str:
    """
    Busca informações na base de conhecimento usando FAISS.
    
    Args:
        query (str): Consulta de busca
        
    Returns:
        str: Documentos relevantes encontrados
    """
    
    if not RAG_AVAILABLE or not retriever:
        return "Sistema de busca em base de conhecimento não disponível."
    
    try:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return "Nenhum documento relevante encontrado na base de conhecimento."
        
        results = []
        for i, doc in enumerate(docs):
            results.append(f"Resultado {i+1}:\n{doc.page_content}\n")
        
        return "\n".join(results)
    except Exception as e:
        return f"Erro ao buscar na base de conhecimento: {str(e)}"