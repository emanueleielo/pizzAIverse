import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from schemas.code import CodiceGalattico
from utils import read_pdf_text, json_to_markdown_with_llm, get_model

# Define paths
CODICE_PATH = "../Hackapizza Dataset/Codice Galattico/Codice Galattico.pdf"
OUTPUT_CODICE = "../database/code.json"
OUTPUT_MARKDOWN = "../database/code.md"


def extract_galactic_code(codice_path: str) -> CodiceGalattico:
    """
    Extract structured information from the Galactic Code PDF file.

    :param codice_path: The path to the Codice Galattico PDF file.
    :return: A CodiceGalattico object with extracted details.
    """
    codice_str: str = read_pdf_text(codice_path)
    model = get_model()
    llm = model.with_structured_output(CodiceGalattico)

    codice: CodiceGalattico = llm.invoke(
        "Extract all relevant structured information from the Galactic Code:\n" + codice_str
    )
    return codice


def save_to_json(data: CodiceGalattico, output_file: str):
    """
    Save extracted Galactic Code data to a JSON file, if it does not already exist.

    :param data: Extracted CodiceGalattico object.
    :param output_file: The JSON file path where data will be stored.
    """
    if os.path.exists(output_file):
        print(f"JSON file '{output_file}' already exists. Skipping creation.")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data.dict(), f, ensure_ascii=False, indent=4)
    print(f"Saved Galactic Code information to {output_file}")



def process_galactic_code():
    """
    Extract structured information from the Galactic Code and save it to a JSON file.
    Then, convert it into a Markdown file using an LLM.
    """
    try:
        if not os.path.exists(OUTPUT_CODICE):
            codice = extract_galactic_code(CODICE_PATH)
            save_to_json(codice, OUTPUT_CODICE)

        # Convert JSON to Markdown using LLM
        with open(OUTPUT_CODICE, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        json_to_markdown_with_llm(json_data, OUTPUT_MARKDOWN, prompt_adding='Dont use table structure for this conversion')
        print(f"Saved Galactic Code markdown to {OUTPUT_MARKDOWN}")

    except Exception as e:
        print(f"Error processing Galactic Code: {e}")


def main():
    """
    Execute the Galactic Code extraction process.
    """
    process_galactic_code()


if __name__ == "__main__":
    main()
