import json
from neo4j import GraphDatabase

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Neo4jTest123"  # Replace with your Neo4j password


class PlanetDistanceUploader:
    """
    This class handles the insertion of planetary distances into a Neo4j database.
    It reads a JSON file containing planet distances and creates both nodes and
    relationships in the graph database.
    """

    def __init__(self, uri, username, password):
        """
        Initialize the connection to the Neo4j database.
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """
        Close the connection to the Neo4j database.
        """
        self.driver.close()

    def create_planet_node(self, tx, planet_name):
        """
        Create a Planet node in the database if it does not already exist.

        :param tx: Neo4j transaction object
        :param planet_name: Name of the planet
        """
        query = """
        MERGE (p:Planet {id: $planet_name})
        RETURN p
        """
        tx.run(query, planet_name=planet_name)

    def create_distance_relationship(self, tx, planet1, planet2, distance):
        """
        Create a DISTANCE_TO relationship between two planets, storing the distance.

        :param tx: Neo4j transaction object
        :param planet1: Name of the first planet
        :param planet2: Name of the second planet
        :param distance: Distance value between the two planets
        """
        query = """
        MATCH (a:Planet {id: $planet1}), (b:Planet {id: $planet2})
        MERGE (a)-[:DISTANCE_TO {distance: $distance}]->(b)
        """
        tx.run(query, planet1=planet1, planet2=planet2, distance=distance)

    def upload_data(self, json_file):
        """
        Read the JSON file and upload the planetary distances to Neo4j.

        :param json_file: Path to the JSON file
        """
        with open(json_file, "r") as file:
            data = json.load(file)

        with self.driver.session() as session:
            for planet_data in data:
                planet_name = planet_data["planet"]
                distances = planet_data["distances"]

                # Create the primary planet node
                session.write_transaction(self.create_planet_node, planet_name)

                # Create distance relationships
                for target_planet, distance in distances.items():
                    if planet_name != target_planet:  # Avoid self-referencing relationships
                        session.write_transaction(self.create_planet_node, target_planet)
                        session.write_transaction(self.create_distance_relationship, planet_name, target_planet,
                                                  distance)


if __name__ == "__main__":
    # Initialize the uploader
    uploader = PlanetDistanceUploader(URI, USERNAME, PASSWORD)

    # Upload the data from the JSON file
    uploader.upload_data("../database/distance.json")  # Replace with the correct JSON file path

    # Close the connection
    uploader.close()

    print("✅ Planetary distances successfully uploaded to Neo4j!")
