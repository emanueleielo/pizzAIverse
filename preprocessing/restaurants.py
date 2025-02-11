import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from schemas.restaurant import Ristorante
from utils import read_pdf_text, get_pdf_files, json_to_markdown_with_llm, get_model

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
MENU_DIR = os.path.join(os.path.dirname(PROJECT_PATH), "Hackapizza Dataset/Menu")
OUTPUT_JSON = os.path.join(os.path.dirname(PROJECT_PATH), "database/restaurants.json")
OUTPUT_MARKDOWN = os.path.join(os.path.dirname(PROJECT_PATH), "database/restaurants.md")

MAX_THREADS = 5


def extract_restaurant_info(menu_path: str) -> Ristorante:
    """
    Extract restaurant information from a menu PDF file.
    """
    model = get_model()
    menu_str: str = read_pdf_text(menu_path)
    llm = model.with_structured_output(Ristorante)
    restaurant: Ristorante = llm.invoke(
        "Extract all restaurant information present in the menu text:\nMENU:\n" + menu_str
    )
    return restaurant


def save_restaurants_to_json(restaurants: list, output_file: str):
    """
    Save a list of restaurants (Ristorante objects) to a JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([restaurant.dict() for restaurant in restaurants], f, ensure_ascii=False, indent=4)
    print(f"Saved {len(restaurants)} restaurants to {output_file}")


def process_pdf(pdf, progress_bar):
    """
    Process a single PDF to extract restaurant information.
    """
    try:
        restaurant = extract_restaurant_info(pdf)
        return restaurant
    except Exception as e:
        print(f"Error extracting {pdf}: {e}")
        return None
    finally:
        progress_bar.update(1)


def convert_single_restaurant_to_markdown(restaurant, prompt_adding: str = "") -> str:
    """
    Calls the LLM to convert a single restaurant (dict or Ristorante object)
    into a Markdown string, returning the generated Markdown.

    We intentionally return the Markdown string here, rather than writing
    to a file directly, so that we can do all writes in one batch later.
    """
    # Depending on how your schema is stored, you may need to convert
    # the restaurant to a dictionary (if it's a Pydantic object).
    # If it's already a dict, you can pass it as is.
    if hasattr(restaurant, "dict"):
        data = restaurant.dict()
    else:
        data = restaurant  # assume it's already a dict

    # Instead of writing directly to the file, we capture the output as a string.
    # We'll do this by temporarily modifying the existing function or
    # by creating a small utility in 'utils' that returns the string.
    # For simplicity, let's call the existing method with an output file
    # that we won't use, then read the content back. Alternatively,
    # you can copy its logic to generate the string directly.
    #
    # Here, I'll show you a simplified approach to get a markdown string:
    # (Assumes you can make a small function that returns the string
    #  rather than writing to disk.)
    from io import StringIO

    # Build the prompt
    import json
    prompt = f"""
    Convert the following JSON data into a well-structured Markdown format:

    ```json
    {json.dumps(data, indent=4)}
    ```

    The Markdown should be:
    - **Concise but readable**
    - **Formatted with headings, lists, and sections**
    - **Avoid unnecessary repetition**
    - **Maintain structured data representation**
    {prompt_adding}

    Output only the Markdown content.
    """

    # Call your model
    model = get_model()
    response = model.invoke(prompt)

    # Return the Markdown text
    # (some LLMs return a .content attribute, others might just return a string)
    return response.content.strip()


def process_restaurants():
    """
    Extract structured information from restaurant menus and save it to JSON if not present.
    Then, convert each restaurant in the JSON file to Markdown in parallel,
    and finally write a single Markdown file.
    """
    # ---- 1) Check if JSON already exists ----
    if os.path.exists(OUTPUT_JSON):
        print(f"JSON file '{OUTPUT_JSON}' already exists. Skipping PDF processing.")
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # If your JSON data is saved as a list, use it directly
        # If it has a "restaurants" key, use json_data["restaurants"] etc.
        # Adjust accordingly.
        restaurants = json_data
    else:
        # ---- 2) If JSON does NOT exist, process the PDFs and generate it ----
        pdf_files = get_pdf_files(MENU_DIR)
        restaurants = []

        with tqdm(total=len(pdf_files), desc="Extracting Menus") as progress_bar:
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                future_to_pdf = {executor.submit(process_pdf, pdf, progress_bar): pdf for pdf in pdf_files}
                for future in as_completed(future_to_pdf):
                    result = future.result()
                    if result:
                        restaurants.append(result)

        # Save to JSON
        save_restaurants_to_json(restaurants, OUTPUT_JSON)

    # ---- 3) Convert each restaurant to Markdown **in parallel** ----
    # We'll collect the Markdown strings in a list to avoid file concurrency issues.
    markdown_list = [None] * len(restaurants)

    print("Converting restaurants to Markdown (parallel) ...")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Map each restaurant to a future that returns its Markdown
        futures = {
            executor.submit(
                convert_single_restaurant_to_markdown,
                restaurant,
                "Each dish should contain the name and even the ID, don't use table data"
            ): idx
            for idx, restaurant in enumerate(restaurants)
        }

        with tqdm(total=len(restaurants), desc="Converting to Markdown") as pbar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    markdown_list[idx] = future.result()
                except Exception as e:
                    markdown_list[idx] = f"**Error converting restaurant #{idx}:** {e}"
                pbar.update(1)

    # ---- 4) Write all Markdown strings to one file (in order) ----
    with open(OUTPUT_MARKDOWN, "w", encoding="utf-8") as f:
        for md in markdown_list:
            f.write(md + "\n\n")  # Separate each restaurant's content with blank lines

    print(f"Saved restaurant markdown to {OUTPUT_MARKDOWN}")


def main():
    """
    Execute the restaurant extraction process.
    """
    process_restaurants()


if __name__ == "__main__":
    main()
