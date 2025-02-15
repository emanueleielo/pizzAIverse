from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def create_faiss_index_from_markdown(
        markdown_folder_path: str,
        faiss_index_save_path: str):
    """
    Creates a FAISS vector store from all Markdown files in the given folder.
    The index is then saved locally at 'faiss_index_save_path'.

    :param markdown_folder_path: Directory containing your Markdown files (*.md).
    :param faiss_index_save_path: Directory path where the FAISS index will be saved.
    """

    # 1. Load all Markdown files from the specified directory.
    #    DirectoryLoader supports glob patterns to restrict file types
    #    e.g. `glob="**/*.md"` if you have nested folders.
    loader = DirectoryLoader(markdown_folder_path, glob="*.md")

    # Read all documents (each file becomes one Document in LangChain).
    documents = loader.load()
    print(f"Loaded {len(documents)} Markdown documents.")

    # 2. Split documents into smaller chunks:
    #    - This improves embedding quality for long documents
    #    - chunk_size and chunk_overlap may be adjusted as needed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150
    )
    docs = text_splitter.split_documents(documents)
    print(f"Split into {len(docs)} text chunks.")

    embeddings = HuggingFaceEmbeddings(model_name="Lajavaness/bilingual-embedding-small", model_kwargs={
           "trust_remote_code": True
        })

    # 4. Create a FAISS vector store from the documents + embeddings.
    #    This step calculates an embedding for each chunk and stores it in FAISS.
    vectorstore = FAISS.from_documents(docs, embeddings)
    print("FAISS index successfully created in memory.")

    # 5. Save the FAISS index locally so you can reload it later without re-embedding.
    #    This will create a folder (faiss_index_save_path) with the necessary files.
    vectorstore.save_local(faiss_index_save_path)
    print(f"FAISS index saved to '{faiss_index_save_path}'.")

def load_faiss_index(faiss_index_path: str) -> FAISS:
    try:
        """
        Loads an existing FAISS index from a local directory.
    
        :param faiss_index_path: The directory where the FAISS index was saved.
        :return: A LangChain FAISS vector store object.
        """
        embeddings = HuggingFaceEmbeddings(model_name="Lajavaness/bilingual-embedding-small", model_kwargs={
           "trust_remote_code": True
        })

        # Re-load the FAISS index from disk, using the same embeddings.
        faiss_vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        return faiss_vectorstore
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None



if __name__ == "__main__":
    MARKDOWN_FOLDER = "../database"  # Folder containing .md files
    FAISS_INDEX_PATH = "../faiss_index"  # Where the index files will be saved

    create_faiss_index_from_markdown(
        markdown_folder_path=MARKDOWN_FOLDER,
        faiss_index_save_path=FAISS_INDEX_PATH
    )
    faiss_store = load_faiss_index(FAISS_INDEX_PATH)
    if faiss_store is None:
        print("Error creating FAISS index.")
    else:
        print("FAISS index created successfully.")

