from neo4j import GraphDatabase


# Configura la connessione a Neo4j
URI = "bolt://localhost:7687"  # Modifica se necessario
USERNAME = "neo4j"
PASSWORD = "Neo4jTest123"  # Modifica se necessario

# Define allowed node types
allowed_nodes = [
    "Chef", "Order", "Restaurant", "Planet",
    "Dish", "Ingredient", "Technique", "License",
]
def create_fulltext_indexes(driver):
    with driver.session() as session:
        for label in allowed_nodes:
            index_name = f"{label.lower()}_fulltext"
            query = f'CREATE FULLTEXT INDEX {index_name} FOR (n:{label}) ON EACH [n.id]'
            try:
                session.run(query)
                print(f"Indice full-text creato per: {label}")
            except Exception as e:
                print(f"Errore nella creazione dell'indice per {label}: {e}")

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    try:
        create_fulltext_indexes(driver)
    finally:
        driver.close()
