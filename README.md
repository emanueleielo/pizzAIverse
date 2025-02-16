# Hackapizza: Galactic Culinary Assistant

## Overview
This project was created for the Hackapizza hackathon. The challenge required building an AI assistant that helps intergalactic travelers navigate a rich multiverse of culinary delights. The system interprets natural language queries, handles complex dietary restrictions and preferences, and ensures that dish recommendations comply with galactic regulations.

## Project Description
The assistant is capable of:
- Parsing natural language queries to understand user preferences and restrictions.
- Processing diverse documents such as menus, galactic codes, and culinary manuals using generative AI.
- Building a knowledge graph and vector database to support dish search and retrieval.
- Querying a Neo4j graph database to extract relevant information about restaurants, chefs, dishes, and more.
- Employing a multi-agent architecture to extract entities, retrieve relevant documents, and validate dish recommendations.

## Architecture
The project is organized into several components:

1. **Preprocessing**  
   - **Data Extraction:** Extracts structured information from PDFs (Galactic Code, Culinary Manual, Restaurant Menus).
   - **Data Transformation:** Converts extracted JSON data into well-formatted Markdown using an LLM.
   - **Vector Store:** Creates a FAISS vector store from Markdown files to enable similarity search.
   - **Knowledge Graph:** Uploads distance data and constructs a Neo4j graph database with full-text indexes for efficient querying.

2. **Main Agent**  
   - Uses LangChain and a custom workflow to:
     - Extract entities from user queries.
     - Retrieve relevant documents from the FAISS vector store.
     - Extract dish information and evaluate dish relevance using fuzzy matching and multi-threading.
     - Return a list of dish identifiers that meet the specified criteria.

3. **Repository and Tools**  
   - A repository layer that interfaces with Neo4j to perform fuzzy searches on dish attributes.
   - Custom tools that support dish search by name and various attributes (ingredients, techniques, orders, etc.).

## Code Structure
The code is organized into the following directories and files:

- **preprocessing/**
  - `code.py`: Extracts structured information from the Galactic Code PDF.
  - `dish_restaurants.py`: Processes restaurant menus and maps dish IDs.
  - `distance.py`: Converts CSV distance data to JSON.
  - `faiss_db.py`: Creates and loads a FAISS vector store from Markdown files.
  - `kg_distances.py`: Uploads planetary distance data to the Neo4j database.
  - `kg_indexes.py` & `knowledge_graph.py`: Create full-text indexes for nodes in the Neo4j graph.
  - `manual.py`: Extracts and processes structured information from the Culinary Manual PDF.
  - `restaurants.py`: Processes restaurant menu PDFs, extracts restaurant information, and converts it to Markdown.

- **main.py**  
  Implements the multi-step agent workflow using LangGraph. It covers:
  - Entity extraction.
  - Document retrieval from the FAISS vector store.
  - Dish extraction and relevance evaluation.
  - Integration with custom tools for dish search and retrieval.

- **repository.py**  
  Contains the Neo4j models and repository for querying dish nodes via full-text indexes and fuzzy matching.

- **tools.py**  
  Implements custom tools for searching dishes by various criteria and for retrieving dish details by name.

- **utils.py**  
  Provides utility functions for reading and cleaning PDF text, interacting with the LLM, and converting JSON data to Markdown.

## Installation
1. **Clone the repository:**
```bash
git clone <repository_url>
```

2. **Create and activate a Python virtual environment.**

3. **Install dependencies:**

`pip install -r requirements.txt`


4. **Set up environment variables:**  
   Create a `.env` file with your OpenAI API key and any other required settings.

5. **Ensure Neo4j is running:**  
   Verify that the Neo4j instance is accessible using the connection details provided in the code.

## Usage
To run the preprocessing steps, execute the following commands:

```bash
 run -d \
    --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/Neo4jTest123 \
    -e NEO4JLABS_PLUGINS='["apoc"]' \
    -e NEO4J_dbms_security_procedures_unrestricted="apoc.*" \
    neo4j:latest
      

```bash
python preprocessing/manual.py
python preprocessing/restaurants.py
python preprocessing/code.py
python preprocessing/distance.py
python preprocessing/dish_restaurants.py
python preprocessing/knowledge_graph.py
python preprocessing/faiss_db.py
python preprocessing/kg_distances.py
python preprocessing/kg_indexes.py
```

Then, start the main agent workflow:

```bash
python main.py
```

## Customization
You can adjust the models and parameters in `utils.py` and modify the agent workflow in `main.py` to suit additional requirements. The code leverages the LangChain framework along with FAISS, Neo4j, and generative AI to deliver comprehensive and accurate dish recommendations.

## Conclusion
This project demonstrates an innovative approach to building an AI assistant that bridges intergalactic culinary cultures using advanced techniques in natural language processing, knowledge graphs, and vector search. It effectively addresses the hackathon challenge by providing complex query interpretation and precise dish recommendations in a multi-dimensional galactic setting.

Enjoy exploring the cosmos of flavors!
