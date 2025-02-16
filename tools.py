import difflib
import json

from langchain.tools import tool

from repository import DishRepository


@tool
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
        min_count: int = 0):
    """
    Searches for Dish nodes based on multiple criteria.

    Args:
        all_of_ingredients (list): Dishs must contain all these ingredients (fuzzy)
        any_of_ingredients (list): Dishs must contain at least one of these ingredients
        exclude_ingredients (list): Exclude dishes containing these ingredients
        all_of_techniques (list): Dishs must use all these techniques
        any_of_techniques (list): Dishs must use at least one of these techniques
        exclude_techniques (list): Exclude dishes using these techniques
        license_uid (str): Filter by chef license
        min_license_grade (int): Min license grade
        order_uid (str): Filter by order association
        restaurant_uid (str): Filter by restaurant
        planet_uid (str): Filter by planet or within max_distance
        max_distance (int): Max distance from planet_uid
        min_count_ingredients_from_list (list): Dishes must have at least min_count of these ingredients.
        min_count (int): Min matched ingredients from list

    Returns:
        list: Matching Dish nodes
    """

    return DishRepository().search_dishes(
        all_of_ingredients=all_of_ingredients,
        any_of_ingredients=any_of_ingredients,
        exclude_ingredients=exclude_ingredients,
        all_of_techniques=all_of_techniques,
        any_of_techniques=any_of_techniques,
        exclude_techniques=exclude_techniques,
        license_uid=license_uid,
        min_license_grade=min_license_grade,
        order_uid=order_uid,
        restaurant_uid=restaurant_uid,
        planet_uid=planet_uid,
        max_distance=max_distance,
        min_count_ingredients_from_list=min_count_ingredients_from_list,
        min_count=min_count
    )

@tool
def get_dish_by_name(name: str) -> list:
    """
    Get a Dish node by its name.

    Args:
        name (str): The name of the Dish node.

    Returns:
        list: Matching Dish nodes
    """

    return DishRepository().get_dish_by_name(name)


def get_dish_by_name(dish_name: str) -> dict:
    """
    Searches for a dish by name across restaurant menus and returns the dish's details with its ID,
    along with the restaurant name, chef, and planet.

    The function first attempts a case-insensitive exact match. If none is found, it collects all
    dish names from the menus and uses difflib.get_close_matches to find the closest match based on
    a similarity cutoff.

    Additionally, it transforms the 'ingredienti' and 'tecniche' fields to lists of strings (only their names).

    Args:
        dish_name (str): The name of the dish to search for.

    Returns:
        dict: A dictionary containing the dish's details, its ID, restaurant name, chef, and planet,
              with 'ingredienti' and 'tecniche' as lists of names, or an empty dictionary if not found.
    """
    # Read JSON 'restaurants.json'
    with open('./database/restaurants.json', encoding='utf-8') as f:
        restaurants = json.load(f)

    # Read JSON 'dish_mapping.json'
    with open('./database/dish_mapping.json', encoding='utf-8') as f:
        dish_ids = json.load(f)

    # Helper function to extract only the 'nome' field from a list of dicts
    def extract_names(items, key="nome"):
        return [item.get(key, "") for item in items if isinstance(item, dict)]

    # Attempt an exact case-insensitive match first
    for restaurant in restaurants:
        menu = restaurant.get("menu", [])
        for dish in menu:
            if dish.get("nome", "").lower() == dish_name.lower():
                dish_id = dish_ids.get(dish.get("nome", ""), None)
                dish_data = dish.copy()
                dish_data["id"] = dish_id
                # Add restaurant-specific details
                dish_data["ristorante"] = restaurant.get("nome", "")
                dish_data["chef"] = restaurant.get("chef", "")
                dish_data["pianeta"] = restaurant.get("pianeta", "")
                # Convert ingredienti and tecniche to lists of names if they exist
                if "ingredienti" in dish_data:
                    dish_data["ingredienti"] = extract_names(dish_data["ingredienti"])
                if "tecniche" in dish_data:
                    dish_data["tecniche"] = extract_names(dish_data["tecniche"])
                return dish_data

    # If no exact match is found, perform fuzzy matching using difflib
    # Build a list of tuples (dish, restaurant) for fuzzy matching
    candidate_dishes = []
    for restaurant in restaurants:
        menu = restaurant.get("menu", [])
        for dish in menu:
            candidate_dishes.append((dish, restaurant))

    # Create a list of candidate dish names
    candidate_names = [dish.get("nome", "") for dish, _ in candidate_dishes]

    # Use difflib.get_close_matches to find the closest match.
    # The cutoff (0.8) can be adjusted for tolerance.
    close_matches = difflib.get_close_matches(dish_name, candidate_names, n=1, cutoff=0.8)

    if close_matches:
        best_match = close_matches[0]
        # Retrieve the corresponding dish details and restaurant data for the best match
        for dish, restaurant in candidate_dishes:
            if dish.get("nome", "") == best_match:
                dish_id = dish_ids.get(best_match, None)
                dish_data = dish.copy()
                dish_data["id"] = dish_id
                # Include restaurant-specific details
                dish_data["ristorante"] = restaurant.get("nome", "")
                dish_data["chef"] = restaurant.get("chef", "")
                dish_data["pianeta"] = restaurant.get("pianeta", "")
                # Convert ingredienti and tecniche to lists of names if they exist
                if "ingredienti" in dish_data:
                    dish_data["ingredienti"] = extract_names(dish_data["ingredienti"])
                if "tecniche" in dish_data:
                    dish_data["tecniche"] = extract_names(dish_data["tecniche"])
                return dish_data

    # If no match is found, return an empty dictionary
    return {}