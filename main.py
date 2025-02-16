import csv
import io
from typing import Any, Annotated

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from preprocessing.faiss_db import load_faiss_index
from tools import search_dishes, get_dish_by_name
from utils import get_model




class AgentState(TypedDict):
    question: str
    documents: list[Document]
    relevant_docs: list[Document]
    entities: str
    dishes: Annotated[list[str], "Dishes extracted from the documents"]

def neo_agent(state: AgentState) -> dict[str, Any]:
    llm = get_model(model='gpt-4o')


    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant. Make sure to use the tool for information. 
                Your duty is to assist the user finding the dish they are searching for, you are provided with a tool that can help you in the process.
                Your output must be only the name of the dishes that match the user's query separated by a comma (if more than one) (eg. 'Dish1,Dish2,Dish3')
                When you use the tool be aware to use the right argument and understand the difference between any/all.
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools = [search_dishes]

    # Construct the Tools agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    #convert entities to string
    entities = str(state['entities'])

    question ="Entità presenti nella domanda:" + entities + '\n' +  state['question']

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    dishes_str = agent_executor.invoke({"input": question})['output']

    dishes_list = dishes_str.split(",")
    print('Dishes neo:', dishes_list)
    return {"dishes": dishes_list}


def extract_entities(state: AgentState) -> dict[str, Any]:
    """
    Extract restaurant information from a menu PDF file.
    """

    class Entities(BaseModel):
        """Classe che rappresenta una qualsiasi entità all'interno del testo
        L'entità puo essere di questo tipi:

        TIPI:
        Ordine: rappresenta un ordine intergalattico (eg. Ordine della Galassia di Andromeda)
        Ristorante: rappresenta un ristorante intergalattico (eg. L'Oasi delle Dune Stellari)
        Licenza: rappresenta una licenza culinaria (eg. Psionica di 3° Livello)
        Tecnica Culinaria: rappresenta una tecnica culinaria avanzatac (eg. Cottura Sottovuoto Frugale Energeticamente Negativa)
        Ingredienti: rappresenta un ingrediente utilizzato nei piatti intergalattici (eg. Sashimi di Magikarp)
        Piatti: rappresenta un piatto servito in un ristorante intergalattico (eg. Rapsodo Celestiale)
        Recensione: rappresenta una recensione di un critico gastronomico intergalattico su un ristorante
        Chef: rappresenta il nome dello chef principale del ristorante (eg.  Alessandra "Nova" Celestini)
        Pianeta: rappresenta il pianeta in cui si trova il ristorante (eg. Krypton)

        Ovviamente un entità NON puo essere un tipo di entità, ma solo un'istanza di un tipo di entità.
        Esempio di entità: Sashimi di Magikarp, Ordine della Galassia di Andromeda, Carne di Kraken, Rapsodo Celestiale, Cottura Sottovuoto Frugale Energeticamente Negativa ec...
        """
        entities: list[str] = Field(None, description="Lista di entità presenti nel testo")


    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Entities)
    entities: Entities = llm.invoke(
        "Estrai tutte le entità presenti nel testo \n ENTITA': " + state['question']
    )


    return {"entities": entities.entities}

def retrieve_docs(state: AgentState) -> dict[str, Any]:
    FAISS_INDEX_PATH = "faiss_index"

    faiss_store = load_faiss_index(FAISS_INDEX_PATH)
    docs = []
    #for each entitiy, execute query to retrieve documents
    for entity in state['entities']:
        docs += faiss_store.similarity_search(entity, 6, search_kwargs={"score_threshold": 0.85})
    return {"documents": docs}


def check_relevance_docs(state: AgentState) -> dict[str, Any]:
    """
    Check the relevance of the documents returned by the FAISS index.
    """

    class Relevance(BaseModel):
        """Classe che rappresenta la rilevanza di un documento rispetto alla domanda dell'utente."""
        relevance: bool = Field(None, description="Valore di rilevanza del documento rispetto alla domanda (True/False)")

    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Relevance)

    relevance_docs = []
    #for each document, check relevance
    for doc in state['documents']:
        relevance: Relevance = llm.invoke(
            "Il documento è rilevante rispetto alla domanda? \n Domanda: " + state['question'] + '\n' + doc.page_content
        )
        if relevance.relevance:
            relevance_docs.append(doc)

    return {"relevant_docs": relevance_docs}

def extract_dishes_from_docs(state: AgentState) -> dict[str, Any]:
    """
    Extract dishes from the relevant documents.
    """

    if not state['relevant_docs']:
        print('No relevant docs found')
        return {"dishes": state['dishes']}

    class Dishes(BaseModel):
        """Classe che rappresenta i piatti estratti dai documenti rilevanti."""
        dishes: list[str] = Field(None, description="Lista di piatti estratti dai documenti rilevanti")

    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Dishes)
    dishes: Dishes = llm.invoke(
        """Estrai i piatti dai documenti rilevanti, di base il nome del piatto è sempre sopra quello del ristorante (una riga sopra)
        I documenti saranno simili a questo formato:
        ### 3. Nome piatto
- **Ristorante:** Nome ristorante
- **Ordine:** Nome Ordine
- **Descrizione:** Descrizione del piatto
- **Chef:** Nome Chef
- **Pianeta:** Nome Pianeta
- **Ingredienti:**
...
- **Tecniche:**
...
        
        Domanda: """ + state['question'] + '\n' + '\n'.join([doc.page_content for doc in state['relevant_docs']])
    )

    dishes_ = state['dishes'] + dishes.dishes
    print('Dishes RAG:', dishes.dishes)
    return {"dishes": dishes_}


def check_dish_relevance(state: dict):
    """
    Checks the relevance of the dishes extracted from the documents.

    For each dish in state['dishes'], this function retrieves the dish details using
    get_dish_by_name and formats the dish information. If any error occurs during
    retrieval, the dish is skipped. The function then calls an LLM to evaluate the
    relevance of each dish with respect to state['question'].

    Returns:
        dict: A dictionary with a key "dishes" containing a comma-separated string of dish IDs.
    """

    # Define a model representing dish relevance as a boolean output.
    class Relevance(BaseModel):
        relevance: bool = Field(None, description="Indicates if the dish is relevant to the question (True/False)")

    # Initialize the LLM model with structured output.
    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Relevance)

    relevant_dishes = []

    # Evaluate relevance for each dish in state['dishes']
    for dish in state.get('dishes', []):
        try:
            # Retrieve dish details; if an error occurs, skip this dish.
            json_dish = get_dish_by_name(dish)
        except Exception:
            print('Error retrieving dish:', dish)
            continue

        # If the dish details are empty, skip it.
        if not json_dish:
            continue

        # Format dish information for LLM evaluation.
        dish_pretty_str = """
### Nome Piatto: {0}
- **Ristorante:** {1}
- **Descrizione:** {2}
- **Chef:** {3}
- **Pianeta:** {4}
- **Ingredienti:** {5}
- **Tecniche:** {6}
""".format(
            json_dish.get('nome', ''),
            json_dish.get('ristorante', ''),
            json_dish.get('descrizione', ''),
            json_dish.get('chef', ''),
            json_dish.get('pianeta', ''),
            ", ".join(json_dish['ingredienti']) if isinstance(json_dish.get('ingredienti'), list) else json_dish.get(
                'ingredienti', ''),
            ", ".join(json_dish['tecniche']) if isinstance(json_dish.get('tecniche'), list) else json_dish.get(
                'tecniche', '')
        )

        print('Dish (Pretty):', dish_pretty_str)
        # Invoke the LLM to evaluate dish relevance.
        try:
            relevance: Relevance = llm.invoke(
                "Il piatto è rilevante rispetto alla richiesta? Per essere rilevante la richiesta dell'utente deve essere soddisfatta, se la richiesta è relativa all'Ordine galattico o la distanza tra pianeti, ritienila sempre rilevante a prescindere in quanto non puoi verificarla. Inoltre considera che i nomi delle tecniche, ingredienti, ristoranti ec.. devono essere corrispondenti quasi al 100%, poichè all'interno dei documenti ci sono nomi molto simili ma che rappresentano cose differenti, se differiscono di 1 sola lettera che magari può essere un errore di battitura va bene, ma se contengono parole diverse rappresentano cose differenti. \nRichiesta: " + state.get('question',
                                                                                       '') + "\nPiatto:" + dish_pretty_str
            )
        except Exception:
            print('LLM invocation failed for dish:', dish)
            # If LLM invocation fails, skip this dish.
            continue


        # If the dish is considered relevant, add it to the list.
        if relevance.relevance:
            print('Dish is relevant')
            relevant_dishes.append(dish)
        else:
            print('Dish is not relevant')

    print('Question:', state.get('question', ''))
    print('Relevant Dishes:', relevant_dishes)
    # Retrieve dish IDs from the relevant dishes.
    dishes_ids = []
    for dish in relevant_dishes:
        try:
            json_dish = get_dish_by_name(dish)
            dish_id = json_dish.get('id')
            if dish_id is not None:
                dishes_ids.append(str(dish_id))
        except Exception:
            # If retrieval fails, simply skip this dish.
            continue

    #avoid duplicates
    dishes_ids = list(set(dishes_ids))

    # If no relevant dish is found, return a default result.
    if not dishes_ids:
        print('No relevant dishes found', state.get('question', ''))
        return {"dishes": "1,2,3"}

    # Return dish IDs as a comma-separated string.
    return {"dishes": ",".join(dishes_ids)}



# Loop through each question in the input CSV and process the query using graph.invoke
def process_questions(input_csv: str, output_csv: str):
    """
    Reads questions from input_csv, invokes the graph to get dishes for each question,
    and writes the results to output_csv in the format:
        row_id,result
    where row_id is a sequential identifier (starting at 1) and result is dishes.dishes.

    Args:
        input_csv (str): Path to the CSV file containing the questions.
        output_csv (str): Path to the CSV file to write the output.
    """
    output_rows = []  # List to hold output rows

    # Open the input CSV file containing the questions
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Iterate over each row (question) with a row counter starting at 1
        for idx, row in enumerate(reader, start=1):
            question = row['domanda']  # Extract the question from the 'domanda' column

            print('Processing question:', question)

            # Invoke the graph with the current question
            dishes = graph.invoke({"question": question})
            # Extract the dishes result (assumed to be a comma-separated string)
            result = dishes['dishes']

            # Append the output row as a dictionary
            output_rows.append({
                "row_id": idx,
                "result": result
            })

    # Write the output rows to the output CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['row_id', 'result']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()  # Write CSV header
        writer.writerows(output_rows)  # Write all rows


# Example usage:
if __name__ == "__main__":

    from langgraph.graph import END, StateGraph, START

    # Define a new graph
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("retrieve_docs", retrieve_docs)
    workflow.add_node("check_relevance_docs", check_relevance_docs)
    workflow.add_node("extract_dishes_from_docs", extract_dishes_from_docs)
    workflow.add_node("check_dish_relevance", check_dish_relevance)
    workflow.add_node("neo_agent", neo_agent)

    workflow.add_edge(START, "extract_entities")
    workflow.add_edge("extract_entities", "neo_agent")
    workflow.add_edge("neo_agent", "retrieve_docs")
    workflow.add_edge("retrieve_docs", "check_relevance_docs")
    workflow.add_edge("check_relevance_docs", "extract_dishes_from_docs")
    workflow.add_edge("extract_dishes_from_docs", "check_dish_relevance")
    workflow.add_edge("check_dish_relevance", END)

    graph = workflow.compile()
    from IPython.display import Image, display

    try:
        # Retrieve the graph image as bytes
        graph_bytes = graph.get_graph(xray=True).draw_mermaid_png()

        # Option 1: Save the bytes directly to a file named 'agent.png'
        with open("agent.png", "wb") as f:
            f.write(graph_bytes)

        # Option 2: Convert the bytes to a PIL Image and save it
        image_obj = Image.open(io.BytesIO(graph_bytes))
        image_obj.save("agent_converted.png")

        # Optionally, display the image in a Jupyter Notebook
        display(Image(image_obj))
    except Exception as e:
        # Print the error message if something goes wrong
        print("Error saving the graph image:", e)

    #process_questions("Hackapizza Dataset/domande.csv", "output.csv")
    graph.invoke({"question": "Quali piatti preparati con la tecnica Grigliatura a Energia Stellare DiV?"})