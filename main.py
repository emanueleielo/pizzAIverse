from typing import Any, Annotated

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from preprocessing.faiss_db import load_faiss_index
from tools import search_dishes, get_dish_by_name
from utils import get_model

FAISS_INDEX_PATH = "../faiss_index"



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
                Your output must be only the name of the dishes that match the user's query separated by a comma (if more than one) (eg. 'Dish1,Dish2,Dish3').""",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools = [search_dishes]

    # Construct the Tools agent
    agent = create_tool_calling_agent(llm, tools, prompt)


    question ="Entità presenti nella domanda:" + state['entities'] + '\n' +  state['question']

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

        Ordine: rappresenta un ordine intergalattico
        Ristorante: rappresenta un ristorante intergalattico
        Licenza: rappresenta una licenza culinaria
        Tecnica Culinaria: rappresenta una tecnica culinaria avanzata
        Ingredienti: rappresenta un ingrediente utilizzato nei piatti intergalattici
        Piatti: rappresenta un piatto servito in un ristorante intergalattico
        Recensione: rappresenta una recensione di un critico gastronomico intergalattico su un ristorante
        Chef: rappresenta il nome dello chef principale del ristorante
        Pianeta: rappresenta il pianeta in cui si trova il ristorante
        """
        entities: list[str] = Field(None, description="Lista di entità presenti nel testo")


    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Entities)
    entities: Entities = llm.invoke(
        "Estrai tutte le entità presenti nel testo \n ENTITA': " + state['question']
    )

    #to string
    entities_str = ",".join(entities.entities)
    return {"entities": entities_str}

def retrieve_docs(state: AgentState) -> dict[str, Any]:
    faiss_store = load_faiss_index(FAISS_INDEX_PATH)
    docs = []
    #for each entitiy, execute query to retrieve documents
    for entity in state['entities']:
        docs += faiss_store.similarity_search_with_relevance_scores(entity, 2, search_kwargs={"score_threshold": .90})
    return {"docs": docs}


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

    class Dishes(BaseModel):
        """Classe che rappresenta i piatti estratti dai documenti rilevanti."""
        dishes: list[str] = Field(None, description="Lista di piatti estratti dai documenti rilevanti")

    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Dishes)
    dishes: Dishes = llm.invoke(
        """Estrai i piatti dai documenti rilevanti
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

    print('Dishes RAG:', dishes.dishes)
    return {"dishes": dishes.dishes}


def check_dish_relevance(state: AgentState):
    """
    Check the relevance of the dishes extracted from the documents.
    """

    class Relevance(BaseModel):
        """Classe che rappresenta la rilevanza di un piatto rispetto alla domanda dell'utente."""
        relevance: bool = Field(None, description="Valore di rilevanza del piatto rispetto alla domanda (True/False)")

    model = get_model(model='gpt-4o-mini')
    llm = model.with_structured_output(Relevance)

    relevant_dishes = []
    #for each dish, check relevance
    for dish in state['dishes']:
        json_dish = get_dish_by_name(dish)
        dish_pretty_str = """
        ### Nome Piatto: {0}
        - **Ristorante:** {1}
        - **Ordine:** {2}
        - **Descrizione:** {3}
        - **Chef:** {4}
        - **Pianeta:** {5}
        - **Ingredienti:** {6}
        - **Tecniche:** {7}
        """.format(json_dish['name'], json_dish['restaurant'], json_dish['order'], json_dish['description'], json_dish['chef'], json_dish['planet'], json_dish['ingredients'], json_dish['techniques'])
        relevance: Relevance = llm.invoke(
            "Il piatto è rilevante rispetto alla domanda? \n Domanda: " + state['question'] + '\n PIatto:' + dish_pretty_str
        )
        if relevance.relevance:
            relevant_dishes.append(dish)

    # use get_dish_by_name to retrieve the dish id
    dishes_ids = []
    for dish in relevant_dishes:
        json_dish = get_dish_by_name(dish)
        dishes_ids.append(json_dish['id'])
    #change format in id1,id2,id3
    return {"dishes": ",".join(dishes_ids)}


from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

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