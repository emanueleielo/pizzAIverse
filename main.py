from rag_research_agent.src.retrieval_graph.graph import retrieval_graph

research = retrieval_graph.stream({"messages": ["Quali piatti sono preparati senza usare la Cottura a Vapore Termocinetica Multipla, ma utilizzano la Congelazione Iperdimensionalmente Stratificata e la Fermentazione Quantico Biometrica?"]})

print(research)