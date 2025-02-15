import os
import logging
import concurrent.futures
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Retrieve OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("Missing OpenAI API key. Please set OPENAI_API_KEY in your .env file.")
    exit(1)

# Neo4j connection details
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "Neo4jTest123"

# Initialize Neo4j graph connection
try:
    graph = Neo4jGraph()
    logging.info("Connected to Neo4j successfully.")
except Exception as e:
    logging.error(f"Failed to connect to Neo4j: {e}")
    exit(1)

# Define allowed node types
allowed_nodes = [
    "Chef", "Order", "Restaurant", "Planet",
    "Dish", "Ingredient", "Technique", "License",
]

# Define allowed relationships
allowed_relationships = [
    "DISH_CONTAINS_INGREDIENT",
    "DISH_USES_TECHNIQUE",
    "DISH_SERVED_AT_RESTAURANT",
    "DISH_REQUIRES_LICENSE",
    "DISH_AVAILABLE_ON_PLANET",
    "DISH_ASSOCIATED_WITH_ORDER",
    "DISH_CREATED_BY_CHEF"
    "DISH_BELONG_TO_ORDER",

    "INGREDIENT_ORIGINATES_FROM_PLANET",
    "INGREDIENT_HAS_PROPERTY_SUBSTANCES",

    "TECHNIQUE_REQUIRES_LICENSE",
    "TECHNIQUE_ASSOCIATED_WITH_ORDER",

    "LICENSE_GRANTED_TO_CHEF",
    "LICENSE_ISSUED_BY_ORDER",

    "CHEF_WORKS_AT_RESTAURANT",
    "CHEF_ASSOCIATED_WITH_ORDER",
    "CHEF_CREATED_DISH",


    "LOCATED_ON_PLANET",
]

# Initialize OpenAI LLM model
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o",
    api_key=api_key,
    max_tokens=16000
)

# Initialize the LLM Graph Transformer
lm_transformer_filtered = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
    additional_instructions="""
    # License guidelines:
    License format ID = License_Name_License_Level(0-1-2..)
.
    """
)

# Define the directory containing Markdown files
database_dir = "../database"
if not os.path.exists(database_dir):
    logging.error(f"Database directory '{database_dir}' not found.")
    exit(1)

# Configure text splitter to handle large files
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Max size of each chunk
    chunk_overlap=250,  # Overlap to maintain context across chunks
)

text_splitter_2 = RecursiveCharacterTextSplitter(
    chunk_size=5000,  # Max size of each chunk
    chunk_overlap=1000,  # Overlap to maintain context across chunks
)



def create_predefined_orders():
    """
    Creates three Order nodes in Neo4j with only the 'id' property:
    - Ordine della Galassia di Andromeda
    - Ordine dei Naturalisti
    - Ordine degli Armonisti

    Uses MERGE to avoid duplicates if they already exist.
    """
    query = """
    MERGE (:Order {id: 'Galassia di Andromeda'})
    MERGE (:Order {id: 'Naturalisti'})
    MERGE (:Order {id: 'Armonisti'})
    """
    graph.query(query)
    logging.info("Predefined Orders created successfully.")

# Create predefined Orders if they do not exist
create_predefined_orders()

# Function to process a single chunk
def process_chunk(doc, filename, chunk_id, total_chunks):
    """
    Processes a single text chunk by converting it into a graph document and
    storing the extracted data into Neo4j.

    :param doc: LangChain Document object
    :param filename: The filename being processed
    :param chunk_id: The index of the chunk
    :param total_chunks: The total number of chunks for this file
    """
    try:
        graph_docs = lm_transformer_filtered.convert_to_graph_documents([doc])

        # Store extracted graph data into Neo4j
        graph.add_graph_documents(graph_docs, include_source=True)

        logging.info(f"File: {filename}, Chunk {chunk_id + 1}/{total_chunks} processed successfully.")

    except Exception as e:
        logging.error(f"Failed to process chunk {chunk_id + 1}/{total_chunks} in {filename}: {e}")



# Ordina i file dando priorità a "code.md" e "manual.md"
all_files = sorted(os.listdir(database_dir), key=lambda f: (f not in ["code.md", "manual.md"], f))
for filename in all_files:
    if filename.endswith(".md"):
        file_path = os.path.join(database_dir, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_text = file.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
            continue

        if filename in ["code.md", "manual.md"]:
           text_chunks = text_splitter_2.split_text(raw_text)
        else:
            text_chunks = text_splitter.split_text(raw_text)

        # Convert chunks into LangChain Document objects
        chunk_documents = [Document(page_content=chunk) for chunk in text_chunks]

        logging.info(f"Processing file '{filename}' - {len(chunk_documents)} chunks detected.")

        # Use multithreading to process chunks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(process_chunk, doc, filename, i, len(chunk_documents))
                for i, doc in enumerate(chunk_documents)
            ]

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

logging.info("Processing completed successfully.")