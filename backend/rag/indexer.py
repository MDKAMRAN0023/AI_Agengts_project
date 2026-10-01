from backend.rag.loader import load_document
from backend.rag.splitter import split_documents
from backend.rag.embeddings import get_embedding_model
from backend.rag.vectorstore import create_vectorstore


def index_document(file_path):

    documents = load_document(file_path)

    chunks = split_documents(documents)

    embeddings = get_embedding_model()

    vectorstore = create_vectorstore(chunks, embeddings)

    return vectorstore