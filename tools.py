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
    Searches for a dish by name across restaurant menus and returns the dish's details with its ID.

    This function iterates over each restaurant and its menu to find a dish whose name matches
    the provided dish_name (case-insensitive). It then merges the dish data with the corresponding
    dish ID from the dish_ids dictionary.

    Args:
        dish_name (str): The name of the dish to search for.
        dish_ids (dict): A mapping of dish names to their IDs.
        restaurants (list): A list of restaurant JSON objects that include menu data.

    Returns:
        dict: The JSON data of the dish including its ID, or an empty dictionary if not found.
    """
    #read json 'restaurants.json'
    with open('./database/restaurants.json') as f:
        restaurants = json.load(f)

    #read json 'dish_mapping.json'
    with open('./database/dish_mapping.json') as f:
        dish_ids = json.load(f)
    # Iterate over each restaurant in the provided list
    for restaurant in restaurants:
        # Retrieve the menu from the current restaurant; default to an empty list if not present
        menu = restaurant.get("menu", [])
        # Iterate over each dish in the restaurant's menu
        for dish in menu:
            # Check for a case-insensitive match for the dish name
            if dish.get("nome", "").lower() == dish_name.lower():
                # Retrieve the dish ID from dish_ids if available
                dish_id = dish_ids.get(dish_name)
                # Create a copy of the dish data to avoid modifying the original JSON
                dish_data = dish.copy()
                # Add the dish ID to the dish data
                dish_data["id"] = dish_id
                return dish_data
    # If the dish is not found in any restaurant's menu, return an empty dictionary
    return {}

