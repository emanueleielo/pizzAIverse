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

import concurrent.futures




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
                You can ignore the requests about Licenses or Galactic gode limits (the question may contain other conditions that can be fulfilled).
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
    Checks the relevance of dishes extracted from documents using multithreading to process
    each dish concurrently.

    For each dish in state['dishes'], this function retrieves dish details, formats the dish
    information, and uses an LLM model to evaluate the dish's relevance with respect to
    state['question']. If a dish is deemed relevant, its dish ID is collected. In case no
    relevant dish is found, a default result is returned.

    Args:
        state (dict): Dictionary containing at least:
            - 'dishes' (list): List of dish names.
            - 'question' (str): The user query.

    Returns:
        dict: A dictionary with a key "dishes" containing a comma-separated string of
              relevant dish IDs.
    """
    # Initialize the LLM model with the specified configuration.
    model = get_model(model='gpt-4o-mini', temperature=0.7)

    def process_single_dish(dish: str) -> str:
        """
        Processes a single dish by retrieving its details, formatting its information,
        and evaluating its relevance via an LLM call.

        Args:
            dish (str): The name of the dish to process.

        Returns:
            str or None: The dish ID as a string if the dish is relevant and the ID is available;
                         otherwise, None.
        """
        try:
            # Retrieve dish details; skip the dish if retrieval fails.
            json_dish = get_dish_by_name(dish)
        except Exception:
            print('Error retrieving dish:', dish)
            return None

        if not json_dish:
            return None

        # Format dish information for LLM evaluation.
        dish_pretty_str = (
            "\n### Nome Piatto: {0}\n"
            "- **Ristorante:** {1}\n"
            "- **Descrizione:** {2}\n"
            "- **Chef:** {3}\n"
            "- **Pianeta:** {4}\n"
            "- **Ingredienti:** {5}\n"
            "- **Tecniche:** {6}\n"
        ).format(
            json_dish.get('nome', ''),
            json_dish.get('ristorante', ''),
            json_dish.get('descrizione', ''),
            json_dish.get('chef', ''),
            json_dish.get('pianeta', ''),
            ", ".join(json_dish['ingredienti']) if isinstance(json_dish.get('ingredienti'), list) else json_dish.get('ingredienti', ''),
            ", ".join(json_dish['tecniche']) if isinstance(json_dish.get('tecniche'), list) else json_dish.get('tecniche', '')
        )

        print('Dish (Pretty):', dish_pretty_str)

        # Build the prompt for LLM evaluation.
        prompt_text = (
            "Valuta la rilevanza di questo piatto rispetto alla richiesta dell'utente.\n"
            "Regole di valutazione:\n"
            "1. La richiesta può avere più condizioni in AND e/o OR; considera tutte le condizioni esplicitamente.\n"
            "2. Se la richiesta riguarda l'Ordine Galattico o la distanza tra pianeti o la licenza, ignora questa condizione,\n"
            "   poiché non è possibile verificarne la validità. \n"
            "3. Per ingredienti, tecniche, ristoranti, ecc., è richiesta un'aderenza quasi assoluta (circa 100%).\n"
            "   Se c'è un errore di battitura di una sola lettera, puoi considerarlo lo stesso nome;\n"
            "   se la differenza è maggiore (parole diverse, più lettere cambiate), interpretalo come entità differente.\n"
            "4. Se la richiesta dell'utente (pianeta, ingredienti, tecniche, chef, ristorante ec..) non risulta soddisfatta dai dati del piatto, il piatto non è rilevante.\n"
            "\n"
            f"Richiesta dell'utente: {state.get('question', '')}\n"
            f"Piatto:\n{dish_pretty_str}\n"
            "IMPORTANTISSIMO: Rispondi solo con True (rilevante) o False (non rilevante), non aggiungere nient'altro."
        )

        try:
            # Invoke the LLM to evaluate the dish's relevance.
            relevance = model.invoke(prompt_text).content
            # Convert the LLM response to a boolean value.
            relevance = relevance.lower() == 'true'
        except Exception:
            print('LLM invocation failed for dish:', dish)
            return None

        if relevance:
            print('Dish is relevant')
            dish_id = json_dish.get('id')
            if dish_id is not None:
                return str(dish_id)
        else:
            print('Dish is not relevant')
        return None

    relevant_dish_ids = []

    # Use ThreadPoolExecutor to concurrently process each dish.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all dish processing tasks to the executor.
        futures = {executor.submit(process_single_dish, dish): dish for dish in state.get('dishes', [])}
        # Retrieve and process the results as they become available.
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                relevant_dish_ids.append(result)

    # Remove duplicate dish IDs.
    relevant_dish_ids = list(set(relevant_dish_ids))

    print('Question:', state.get('question', ''))
    print('Relevant Dishes:', relevant_dish_ids)

    # If no relevant dish is found, return a default result.
    if not relevant_dish_ids:
        print('No relevant dishes found', state.get('question', ''))
        return {"dishes": "1,42"}

    # Return the relevant dish IDs as a comma-separated string.
    return {"dishes": ",".join(relevant_dish_ids)}


def process_questions(input_csv: str, output_csv: str):
    """
    Process questions from an input CSV file by invoking the graph for each question.
    The function attempts to invoke the graph up to 3 times in case of failure.
    If all attempts fail, a default result "1,42" is used.
    The output is written to a CSV file with each row including a sequential row identifier
    and the resulting dishes, with all fields always quoted.

    Args:
        input_csv (str): Path to the CSV file containing the questions.
        output_csv (str): Path to the CSV file where the output will be written.
    """
    output_rows = []  # List to store output rows
    max_retries = 3   # Maximum number of retries for each graph.invoke call

    # Open the input CSV file and create a reader object
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Iterate over each question row, with a sequential row identifier starting at 1
        for idx, row in enumerate(reader, start=1):
            question = row['domanda']  # Extract the question from the 'domanda' column
            print('Processing question:', question)

            # Initialize result with default value in case all attempts fail
            result = "1,42"
            # Try invoking the graph up to max_retries times
            for attempt in range(1, max_retries + 1):
                try:
                    # Invoke the graph using the current question; expects a dict with a 'dishes' key
                    dishes = graph.invoke({"question": question})
                    # Extract the dishes result (expected to be a comma-separated string)
                    result = dishes['dishes']
                    break  # Exit the retry loop if invocation is successful
                except Exception as e:
                    #Save in error.log the question that failed
                    with open('error.log', 'a') as f:
                        f.write(f"Attempt {attempt} failed for question: {question} with error: {e}\n")
                    print(f"Attempt {attempt} failed for question: {question} with error: {e}")
                    if attempt == max_retries:
                        # After max_retries, use the default result
                        print("Max retries reached; using default result '1,42'.")
                    else:
                        # Optional: Wait for a short period before retrying
                        time.sleep(1)

            # Append the processed row to the output list
            output_rows.append({
                "row_id": idx,
                "result": result
            })

    # Open the output CSV file and create a writer that always quotes fields
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['row_id', 'result']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()  # Write header row to CSV
        writer.writerows(output_rows)  # Write all processed rows

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

    process_questions("Hackapizza Dataset/domande.csv", "output.csv")
