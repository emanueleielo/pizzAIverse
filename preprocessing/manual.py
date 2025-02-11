import os
import json
from dotenv import load_dotenv
from schemas.manual import ManualeCucinaSpaziale
from utils import read_pdf_text, json_to_markdown_with_llm, get_model

load_dotenv()


# Define paths
MANUAL_PATH = "../Hackapizza Dataset/Misc/Manuale di Cucina.pdf"
OUTPUT_MANUAL = "../database/manual.json"
OUTPUT_MARKDOWN = "../database/manual.md"

def extract_manual_info(manual_path: str) -> ManualeCucinaSpaziale:
    """
    Extract structured information from the cooking manual PDF file.

    :param manual_path: The path to the manual PDF file.
    :return: A ManualeCucinaSpaziale object with extracted details.
    """
    manual_str: str = read_pdf_text(manual_path)
    model = get_model()
    llm = model.with_structured_output(ManualeCucinaSpaziale)
    manual: ManualeCucinaSpaziale = llm.invoke(
        "Extract all relevant structured information from the cooking manual:\n" + manual_str
    )
    return manual

def save_to_json(data: ManualeCucinaSpaziale, output_file: str):
    """
    Save extracted manual data to a JSON file, if it does not already exist.

    :param data: Extracted ManualeCucinaSpaziale object.
    :param output_file: The JSON file path where data will be stored.
    """
    if os.path.exists(output_file):
        print(f"JSON file '{output_file}' already exists. Skipping creation.")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data.dict(), f, ensure_ascii=False, indent=4)
    print(f"Saved manual information to {output_file}")

def process_manual():
    """
    Extract structured information from the cooking manual and save it to a JSON file.
    Then, convert it into a Markdown file using an LLM.
    """
    try:
        if not os.path.exists(OUTPUT_MANUAL):
            manual = extract_manual_info(MANUAL_PATH)
            save_to_json(manual, OUTPUT_MANUAL)

        # Convert JSON to Markdown using LLM
        with open(OUTPUT_MANUAL, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        json_to_markdown_with_llm(json_data, OUTPUT_MARKDOWN)
        print(f"Saved manual markdown to {OUTPUT_MARKDOWN}")

    except Exception as e:
        print(f"Error processing manual: {e}")

def main():
    """
    Execute the manual extraction process.
    """
    process_manual()

if __name__ == "__main__":
    main()
