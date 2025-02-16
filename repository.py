from neomodel import db, RelationshipTo, StringProperty, StructuredNode, RelationshipFrom,config



config.DATABASE_URL = 'bolt://neo4j:Neo4jTest123@localhost:7687'

class Document(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")
    text = StringProperty()

    # Outgoing relationships from Document to other nodes
    mentions_license = RelationshipTo('License', 'MENTIONS')
    mentions_technique = RelationshipTo('Technique', 'MENTIONS')
    mentions_order = RelationshipTo('Order', 'MENTIONS')
    mentions_chef = RelationshipTo('Chef', 'MENTIONS')
    mentions_ingredient = RelationshipTo('Ingredient', 'MENTIONS')
    mentions_planet = RelationshipTo('Planet', 'MENTIONS')
    mentions_dish = RelationshipTo('Dish', 'MENTIONS')
    mentions_restaurant = RelationshipTo('Restaurant', 'MENTIONS')


# ================================
# License Node
# ================================
class License(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    # Incoming from Document
    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # Outgoing relationships
    # The "LICENSE_GRANTED_TO_CHEF" relationship links a License to a Chef
    license_granted_to_chef = RelationshipTo('Chef', 'LICENSE_GRANTED_TO_CHEF')

    # The "LICENSE_ISSUED_BY_ORDER" relationship links a License to an Order
    license_issued_by_order = RelationshipTo('Order', 'LICENSE_ISSUED_BY_ORDER')

    # Incoming relationships from other nodes
    # The "TECHNIQUE_REQUIRES_LICENSE" relationship links from Technique to License
    technique_requires_license = RelationshipFrom('Technique', 'TECHNIQUE_REQUIRES_LICENSE')
    # The "DISH_REQUIRES_LICENSE" relationship links from Dish to License
    dish_requires_license = RelationshipFrom('Dish', 'DISH_REQUIRES_LICENSE')


# ================================
# Technique Node
# ================================
class Technique(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # Outgoing relationships
    # The "TECHNIQUE_REQUIRES_LICENSE" relationship links Technique to License
    technique_requires_license = RelationshipTo('License', 'TECHNIQUE_REQUIRES_LICENSE')
    # The "TECHNIQUE_ASSOCIATED_WITH_ORDER" relationship links Technique to Order
    technique_associated_with_order = RelationshipTo('Order', 'TECHNIQUE_ASSOCIATED_WITH_ORDER')

    # Incoming relationships from other nodes
    # If a Dish uses a Technique, we can use the existing relationship name "DISH_USES_TECHNIQUE"
    dish_uses_technique = RelationshipFrom('Dish', 'DISH_USES_TECHNIQUE')
    # A Chef might be associated with an Order via "CHEF_ASSOCIATED_WITH_ORDER"
    # but if we keep the link from Chef to Technique, we'd define it differently.


# ================================
# Order Node
# ================================
class Order(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # The "CHEF_ASSOCIATED_WITH_ORDER" relationship links Chef to Order
    chef_associated_with_order = RelationshipFrom('Chef', 'CHEF_ASSOCIATED_WITH_ORDER')

    # The "DISH_ASSOCIATED_WITH_ORDER" or "DISH_BELONG_TO_ORDER" can link Dish to Order
    dish_associated_with_order = RelationshipFrom('Dish', 'DISH_ASSOCIATED_WITH_ORDER')
    dish_belong_to_order = RelationshipFrom('Dish', 'DISH_BELONG_TO_ORDER')

    # The "TECHNIQUE_ASSOCIATED_WITH_ORDER" relationship can also link Technique to Order
    technique_associated_with_order_in = RelationshipFrom('Technique', 'TECHNIQUE_ASSOCIATED_WITH_ORDER')

    # A License can be issued by an Order, but that link is stored in License


# ================================
# Chef Node
# ================================
class Chef(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # A Chef can have a License
    license_granted_to_chef_in = RelationshipFrom('License', 'LICENSE_GRANTED_TO_CHEF')

    # A Chef creates a Dish
    chef_created_dish = RelationshipTo('Dish', 'CHEF_CREATED_DISH')

    # A Chef works at a Restaurant
    chef_works_at_restaurant = RelationshipTo('Restaurant', 'CHEF_WORKS_AT_RESTAURANT')

    # A Chef can be associated with an Order
    chef_associated_with_order = RelationshipTo('Order', 'CHEF_ASSOCIATED_WITH_ORDER')


# ================================
# Planet Node
# ================================
class Planet(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # The "LOCATED_ON_PLANET" relationship for Restaurant
    restaurant_on_planet = RelationshipFrom('Restaurant', 'LOCATED_ON_PLANET')

    # The "DISH_AVAILABLE_ON_PLANET" relationship from Dish to Planet
    dish_available_on_planet_in = RelationshipFrom('Dish', 'DISH_AVAILABLE_ON_PLANET')

    # The "INGREDIENT_ORIGINATES_FROM_PLANET" relationship from Ingredient to Planet
    ingredient_originates_from_planet_in = RelationshipFrom('Ingredient', 'INGREDIENT_ORIGINATES_FROM_PLANET')


# ================================
# Dish Node
# ================================
class Dish(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # The "DISH_CONTAINS_INGREDIENT" relationship from Dish to Ingredient
    dish_contains_ingredient = RelationshipTo('Ingredient', 'DISH_CONTAINS_INGREDIENT')

    # The "DISH_USES_TECHNIQUE" relationship from Dish to Technique
    dish_uses_technique = RelationshipTo('Technique', 'DISH_USES_TECHNIQUE')

    # The "DISH_SERVED_AT_RESTAURANT" relationship from Dish to Restaurant
    dish_served_at_restaurant = RelationshipTo('Restaurant', 'DISH_SERVED_AT_RESTAURANT')

    # The "DISH_REQUIRES_LICENSE" relationship from Dish to License
    dish_requires_license = RelationshipTo('License', 'DISH_REQUIRES_LICENSE')

    # The "DISH_AVAILABLE_ON_PLANET" relationship from Dish to Planet
    dish_available_on_planet = RelationshipTo('Planet', 'DISH_AVAILABLE_ON_PLANET')

    # A Dish can be created by a Chef using the relationship "DISH_CREATED_BY_CHEF"
    dish_created_by_chef = RelationshipTo('Chef', 'DISH_CREATED_BY_CHEF')

    # A Dish may be associated or belong to an Order
    dish_associated_with_order = RelationshipTo('Order', 'DISH_ASSOCIATED_WITH_ORDER')
    dish_belong_to_order = RelationshipTo('Order', 'DISH_BELONG_TO_ORDER')


# ================================
# Ingredient Node
# ================================
class Ingredient(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # The "DISH_CONTAINS_INGREDIENT" relationship from Dish to Ingredient (this is inverse direction)
    dish_contains_ingredient_in = RelationshipFrom('Dish', 'DISH_CONTAINS_INGREDIENT')

    # The "INGREDIENT_ORIGINATES_FROM_PLANET" relationship from Ingredient to Planet
    ingredient_originates_from_planet = RelationshipTo('Planet', 'INGREDIENT_ORIGINATES_FROM_PLANET')

    # Potential new relationship to reflect "INGREDIENT_HAS_PROPERTY_SUBSTANCES"
    # We can define it if we had a Substance node, but let's just put a placeholder.
    # ingredient_has_property_substances = RelationshipTo('Substance', 'INGREDIENT_HAS_PROPERTY_SUBSTANCES')


# ================================
# Restaurant Node
# ================================
class Restaurant(StructuredNode):
    uid = StringProperty(unique=True, required=True, db_property="id")

    mentioned_in = RelationshipFrom('Document', 'MENTIONS')

    # The "LOCATED_ON_PLANET" relationship from Restaurant to Planet
    located_on_planet = RelationshipTo('Planet', 'LOCATED_ON_PLANET')

    # A Chef works at a Restaurant
    chef_works_at_restaurant_in = RelationshipFrom('Chef', 'CHEF_WORKS_AT_RESTAURANT')

    # A Dish can be served at a Restaurant
    dish_served_at_restaurant_in = RelationshipFrom('Dish', 'DISH_SERVED_AT_RESTAURANT')




class DishRepository:
    """
    Simplified repository for retrieving Dish nodes via fulltext indexes
    with fuzzy matching enabled for ingredient and technique lookups.
    """

    # -------------------------
    # HELPER QUERIES (RETURN SETS OF Dish.id)
    # -------------------------

    @staticmethod
    def _any_of_ingredients(ingredient_uids: list) -> set:
        """
        Retrieves dish IDs that have at least one of the provided ingredients (OR logic).
        Each ingredient string is split into tokens, and each token is appended with a '~'
        to enable Lucene fuzzy matching.

        Args:
            ingredient_uids (list): A list of ingredient strings to be searched with fuzzy logic.

        Returns:
            set: A set of dish IDs matching at least one of the fuzzy ingredient searches.
        """
        if not ingredient_uids:
            return set()

        fuzzy_queries = []
        for uid in ingredient_uids:
            tokens = uid.split()
            fuzzy_tokens = [f"{t}~1" for t in tokens]
            fuzzy_query = " ".join(fuzzy_tokens)
            fuzzy_queries.append(fuzzy_query)

        query = """
        UNWIND $fuzzy_queries AS fq
        CALL db.index.fulltext.queryNodes("ingredient_fulltext", fq) YIELD node AS ingredient, score
        WITH ingredient, score
        WHERE score > 1.5
        MATCH (d:Dish)-[:DISH_CONTAINS_INGREDIENT]->(ingredient)
        RETURN DISTINCT d.id
        """
        results, _ = db.cypher_query(query, {"fuzzy_queries": fuzzy_queries})
        return {row[0] for row in results}

    @staticmethod
    def _all_of_ingredients(ingredient_uids: list) -> set:
        """
        Retrieves dish IDs that contain ALL of the provided ingredients (AND logic),
        with fuzzy matching and a score threshold for each ingredient token.

        Args:
            ingredient_uids (list): A list of ingredient strings (e.g. ["Sashimi di Magicarp", "Cioccorane"]).

        Returns:
            set: A set of dish IDs that contain all the specified fuzzy-matched ingredients.
        """
        if not ingredient_uids:
            return set()

        fuzzy_queries = []
        for uid in ingredient_uids:
            tokens = uid.split()
            fuzzy_tokens = [f"{t}~2" for t in tokens]
            fuzzy_query = " ".join(fuzzy_tokens)
            fuzzy_queries.append(fuzzy_query)

        query = """
        UNWIND $fuzzy_queries AS fq
        CALL db.index.fulltext.queryNodes("ingredient_fulltext", fq) YIELD node AS ing, score
        WHERE score > 3  // Adjust threshold to your desired strictness
        WITH fq, COLLECT(ing) AS matchedIngs
        // 'matchedIngs' is the set of Ingredient nodes matched by the fuzzy query 'fq' with score > 0.9

        WITH COLLECT(matchedIngs) AS listOfSets
        // 'listOfSets' is now a list, each element is the set of nodes matched by a single fuzzy query

        MATCH (d:Dish)
        // Condition: For each set in listOfSets, the dish must contain at least one Ingredient from that set
        WHERE ALL(ingSet IN listOfSets 
                  WHERE ANY(i IN ingSet 
                            WHERE (d)-[:DISH_CONTAINS_INGREDIENT]->(i)))
        RETURN d.id
        """

        results, _ = db.cypher_query(query, {"fuzzy_queries": fuzzy_queries})
        return {row[0] for row in results}

    @staticmethod
    def _all_of_techniques(technique_uids: list) -> set:
        """
        Retrieves dish IDs that use ALL of the provided techniques (AND logic)
        by executing a fuzzy matching query for each technique separately and
        then computing the intersection of the resulting dish IDs.

        Args:
            technique_uids (list): A list of technique strings to be matched collectively (AND).

        Returns:
            set: A set of dish IDs that use all of the specified fuzzy-matched techniques.
        """
        if not technique_uids:
            return set()

        all_ids = None  # This will hold the intersection of dish IDs for each technique

        for uid in technique_uids:
            # Split the technique string into tokens and build a fuzzy query for each token
            tokens = uid.split()
            fuzzy_tokens = [f"{t}~1" for t in tokens]
            fuzzy_query = " ".join(fuzzy_tokens)

            query = """
            CALL db.index.fulltext.queryNodes("technique_fulltext", $fuzzy_query) YIELD node AS technique, score
            WHERE score > 2
            MATCH (d:Dish)-[:DISH_USES_TECHNIQUE]->(technique)
            RETURN DISTINCT d.id AS id
            """
            results, _ = db.cypher_query(query, {"fuzzy_query": fuzzy_query})
            current_ids = {row[0] for row in results}

            # If it's the first technique, initialize all_ids; otherwise, intersect
            if all_ids is None:
                all_ids = current_ids
            else:
                all_ids = all_ids.intersection(current_ids)

        return all_ids if all_ids is not None else set()

    @staticmethod
    def _by_chef_license(license_uid: str, min_grade: int = 0) -> set:
        """
        Retrieves dish IDs created by chefs who have a specific license (exact match) with at least min_grade.
        This method does not apply fuzzy matching since license UIDs tend to be precise (e.g., short codes).

        Args:
            license_uid (str): The UID of the license to match exactly.
            min_grade (int): The minimum grade required for the license.

        Returns:
            set: A set of dish IDs created by chefs meeting the license criteria.
        """
        if not license_uid:
            return set()

        license_query = license_uid
        query = """
        CALL db.index.fulltext.queryNodes("license_fulltext", $license_query) YIELD node AS license
        MATCH (d:Dish)<-[:DISH_CREATED_BY_CHEF]-(c:Chef)<-[:LICENSE_GRANTED_TO_CHEF]-(license)
        WHERE license.grade >= $min_grade
        RETURN DISTINCT d.id
        """
        params = {"license_query": license_query, "min_grade": min_grade}
        results, _ = db.cypher_query(query, params)
        return {row[0] for row in results}

    @staticmethod
    def _by_order(order_uid: str) -> set:
        """
        Retrieves dish IDs that belong or are associated to a specific order (exact match).

        Args:
            order_uid (str): The UID of the order to match exactly.

        Returns:
            set: A set of dish IDs belonging/associated to the specified order.
        """
        if not order_uid:
            return set()

        order_query = order_uid
        query = """
        CALL db.index.fulltext.queryNodes("order_fulltext", $order_query) YIELD node AS ord
        MATCH (d:Dish)-[:DISH_BELONG_TO_ORDER|DISH_ASSOCIATED_WITH_ORDER]->(ord)
        RETURN DISTINCT d.id
        """
        results, _ = db.cypher_query(query, {"order_query": order_query})
        return {row[0] for row in results}

    @staticmethod
    def _by_restaurant(restaurant_uid: str) -> set:
        """
        Retrieves dish IDs served at a specific restaurant (exact match).

        Args:
            restaurant_uid (str): The UID of the restaurant to match exactly.

        Returns:
            set: A set of dish IDs served at the specified restaurant.
        """
        if not restaurant_uid:
            return set()

        restaurant_query = restaurant_uid
        query = """
        CALL db.index.fulltext.queryNodes("restaurant_fulltext", $restaurant_query) YIELD node AS rest
        MATCH (d:Dish)-[:DISH_SERVED_AT_RESTAURANT]->(rest)
        RETURN d.id
        """
        results, _ = db.cypher_query(query, {"restaurant_query": restaurant_query})
        return {row[0] for row in results}

    @staticmethod
    def _by_restaurant_distance(planet_uid: str, max_distance: int) -> set:
        """
        Retrieves dish IDs served in restaurants located within 'max_distance' from a specified planet.

        Args:
            planet_uid (str): The UID of the reference planet.
            max_distance (int): The maximum distance to match restaurants.

        Returns:
            set: A set of dish IDs served by restaurants within the given distance from the planet.
        """
        if not planet_uid or max_distance is None:
            return set()

        query = """
        MATCH (p:Planet {id: $planet_uid})-[:DISTANCE_TO]-(otherPlanet:Planet)
        WHERE EXISTS { 
            MATCH (p)-[d:DISTANCE_TO]->(otherPlanet) WHERE d.distance <= $max_distance
        }
        MATCH (r:Restaurant)-[:LOCATED_ON_PLANET]->(otherPlanet)
        MATCH (d:Dish)-[:DISH_SERVED_AT_RESTAURANT]->(r)
        RETURN DISTINCT d.id
        """

        params = {"planet_uid": planet_uid, "max_distance": max_distance}
        results, _ = db.cypher_query(query, params)
        return {row[0] for row in results}

    @staticmethod
    def _all_dishes() -> set:
        """
        Retrieves the IDs of all available Dish nodes (no fulltext query applied).

        Returns:
            set: A set of IDs for all Dish nodes in the database.
        """
        query = """MATCH (d:Dish) RETURN d.id"""
        results, _ = db.cypher_query(query, {})
        return {row[0] for row in results}

    # -------------------------
    # MAIN ENTRY POINT
    # -------------------------

    @staticmethod
    def get_dish_by_name(name: str) -> list:
        """
        Get a Dish node by its name.
        Args:
            name (str): The name of the Dish node.

        Returns:
            list: A list of Dish nodes with the specified name.
        """
        query = """
        MATCH (d:Dish {id: $name})
        RETURN d
        """
        results, _ = db.cypher_query(query, {"name": name})
        return [row[0] for row in results]

    @staticmethod
    def search_dishes(
        all_of_ingredients: list = None,
        any_of_ingredients: list = None,
        exclude_ingredients: list = None,
        all_of_techniques: list = None,
        any_of_techniques: list = None,
        exclude_techniques: list = None,
        license_uid: str = None,
        min_license_grade: int = 0,
        order_uid: str = None,
        restaurant_uid: str = None,
        planet_uid: str = None,
        max_distance: int = None,
        min_count_ingredients_from_list: list = None,
        min_count: int = 0
    ) -> list:
        """
        Performs a comprehensive fuzzy-enabled search for Dish nodes based on multiple optional criteria.

        Args:
            all_of_ingredients (list): Dishes must contain ALL of these ingredients (fuzzy).
            any_of_ingredients (list): Dishes must contain at least one of these ingredients (fuzzy).
            exclude_ingredients (list): Exclude dishes that contain any of these ingredients (fuzzy).
            all_of_techniques (list): Dishes must use ALL of these techniques (fuzzy).
            any_of_techniques (list): Dishes must use at least one of these techniques (fuzzy).
            exclude_techniques (list): Exclude dishes that use any of these techniques (fuzzy).
            license_uid (str): Dishes must be created by chefs holding this license (exact match).
            min_license_grade (int): The minimum license grade required.
            order_uid (str): Dishes must belong or be associated to this order (exact match).
            restaurant_uid (str): Dishes must be served at this specific restaurant (exact match).
            planet_uid (str): Dishes must be served in restaurants on this planet (or within distance).
            max_distance (int): The maximum distance from the planet for restaurants serving these dishes.
            min_count_ingredients_from_list (list): Fuzzy ingredients from which a dish must contain at least 'min_count'.
            min_count (int): Required count of matched ingredients from 'min_count_ingredients_from_list'.

        Returns:
            list: A list of Dish nodes matching all specified filtering criteria. May be empty if no matches are found.
        """

        positive_sets = []

        # 1) INGREDIENTS
        if all_of_ingredients:
            positive_sets.append(DishRepository._all_of_ingredients(all_of_ingredients))
        if any_of_ingredients:
            positive_sets.append(DishRepository._any_of_ingredients(any_of_ingredients))

        # 2) TECHNIQUES
        if all_of_techniques:
            positive_sets.append(DishRepository._all_of_techniques(all_of_techniques))
        if any_of_techniques:
            positive_sets.append(DishRepository._any_of_techniques(any_of_techniques))

        # 3) LICENSE
        if license_uid:
            positive_sets.append(DishRepository._by_chef_license(license_uid, min_license_grade))

        # 4) ORDER
        if order_uid:
            positive_sets.append(DishRepository._by_order(order_uid))

        # 5) RESTAURANT
        if restaurant_uid:
            positive_sets.append(DishRepository._by_restaurant(restaurant_uid))

        # 6) DISTANCE
        if planet_uid is not None and max_distance is not None:
            positive_sets.append(DishRepository._by_restaurant_distance(planet_uid, max_distance))

        # Intersect all positive sets if any, else retrieve all dishes.
        if not positive_sets:
            current_uids = DishRepository._all_dishes()
        else:
            current_uids = set.intersection(*positive_sets) if positive_sets else set()

        # 7) EXCLUSION
        if exclude_ingredients:
            to_exclude = DishRepository._any_of_ingredients(exclude_ingredients)
            current_uids -= to_exclude

        if exclude_techniques:
            to_exclude = DishRepository._any_of_techniques(exclude_techniques)
            current_uids -= to_exclude

        # 8) MIN COUNT OF SPECIFIC INGREDIENTS (FUZZY)
        if min_count_ingredients_from_list and min_count > 0:
            query = """
            UNWIND $ingredient_queries AS fq
            CALL db.index.fulltext.queryNodes("ingredient_fulltext", fq) YIELD node AS ing, score
            WHERE score > 2
            MATCH (d:Dish)-[:DISH_CONTAINS_INGREDIENT]->(ing)
            WITH d, COUNT(DISTINCT ing) AS matched_ingredients
            WHERE matched_ingredients >= $min_count
            RETURN DISTINCT d.id
            """

            fuzzy_queries = []
            for uid in min_count_ingredients_from_list:
                tokens = uid.split()
                fuzzy_tokens = [f"{t}~1" for t in tokens]
                fuzzy_query = " ".join(fuzzy_tokens)
                fuzzy_queries.append(fuzzy_query)

            params = {"ingredient_queries": fuzzy_queries, "min_count": min_count}
            results, _ = db.cypher_query(query, params)
            dish_with_enough = {row[0] for row in results}

            # Assicuriamoci di applicare l'intersezione correttamente
            current_uids = current_uids.intersection(dish_with_enough) if current_uids else dish_with_enough

        # Final return
        if not current_uids:
            return []

        final_query = """
        UNWIND $uids AS duid
        MATCH (d:Dish {id: duid})
        RETURN d
        """
        results, _ = db.cypher_query(final_query, {"uids": list(current_uids)})
        return [Dish.inflate(row[0]) for row in results]
