
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)


def load_document(file_path):
    """
    Load PDF, DOCX, or TXT file
    and return LangChain Documents.
    """

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)

    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)

    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")

    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

    documents = loader.load()

    return documents



