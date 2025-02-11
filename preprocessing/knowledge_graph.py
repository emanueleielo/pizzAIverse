import os
import logging
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
    "Person", "Chef", "GastronomicOrder", "Restaurant", "Planet", "Galaxy","Substances",
    "Dish", "Ingredient", "Technique", "License", "Sanction",
]

# Define allowed relationships
allowed_relationships = [
    "IS_MEMBER_OF", "BELONGS_TO_ORGANIZATION", "LOCATED_IN", "WITHIN_RANGE",
    "SERVES_DISH", "USES_INGREDIENT", "EXCLUDES_INGREDIENT", "USES_TECHNIQUE",
    "EXCLUDES_TECHNIQUE", "IS_PREPARED_BY", "REQUIRES_LICENSE", "HAS_SANCTION",
    "VIOLATES", "HAS_INTOLERANCE", "IMPOSES_LIMIT", "HAS_LEVEL", "HAS_LICENSE",
    "CHEF_OF", "LIMITS_INGREDIENT", "LIMITS_QUANTITY", "REQUIRES_LICENSE_LEVEL",
    "CERTIFIED_BY", "WITHIN_DISTANCE_OF", "REGULATED_BY", "FOLLOWS_ORDER",
    "PROHIBITED_BY_ORDER", "USES_MULTIPLE_TECHNIQUES","PLANET_DISTANCE"
]


# Initialize OpenAI LLM model
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o-mini",
    api_key=api_key,
    max_tokens=16000
)

# Initialize the LLM Graph Transformer
lm_transformer_filtered = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
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

# Process all Markdown files in the directory
for filename in os.listdir(database_dir):
    if filename.endswith(".md"):
        file_path = os.path.join(database_dir, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_text = file.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
            continue

        # Split the document into smaller chunks
        text_chunks = text_splitter.split_text(raw_text)

        # Convert chunks into LangChain Document objects
        chunk_documents = [Document(page_content=chunk) for chunk in text_chunks]

        logging.info(f"Processing file '{filename}' - {len(chunk_documents)} chunks detected.")

        # Process each chunk
        for i, doc in enumerate(chunk_documents):
            try:
                graph_docs = lm_transformer_filtered.convert_to_graph_documents([doc])

                # Store extracted graph data into Neo4j
                graph.add_graph_documents(graph_docs, include_source=True)

                logging.info(f"File: {filename}, Chunk {i + 1}/{len(chunk_documents)} processed successfully.")
                for j, gdoc in enumerate(graph_docs):
                    logging.debug(f"GraphDocument {j + 1}: Nodes={gdoc.nodes}, Relationships={gdoc.relationships}")

            except Exception as e:
                logging.error(f"Failed to process chunk {i + 1}/{len(chunk_documents)} in {filename}: {e}")
                continue

logging.info("Processing completed successfully.")
