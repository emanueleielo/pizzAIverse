import json
import re

import PyPDF2 as pypdf
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def get_openai_api_key():
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")
def get_model(model="gpt-4o-mini", temperature=0):
    api_key = get_openai_api_key()
    model = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    return model

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing unwanted characters and formatting errors.

    :param text: The raw text extracted from the PDF.
    :return: A cleaned version of the text.
    """
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Removes non-ASCII characters

    # Normalize spacing (replace multiple spaces with a single space)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def read_pdf_text(pdf_path: str, clean = True) -> str:
    """
    Read text from a PDF file using PyPDF2.
    :param pdf_path:
    :return:
    """
    pdf = pypdf.PdfReader(pdf_path)
    text = ''
    for page_num in range(len(pdf.pages)):
        text += pdf.pages[page_num].extract_text()

    if clean:
        text = clean_text(text)
    return text


def get_pdf_files(directory: str) -> list:
    """
    Retrieve all PDF file paths from a given directory.

    :param directory: The directory containing PDF files.
    :return: List of PDF file paths.
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".pdf")]


def json_to_markdown_with_llm(
        json_data: dict,
        output_file: str,
        prompt_adding: str = "",
        append: bool = False
):
    """
    Converts JSON data into a well-formatted Markdown using an LLM.

    :param json_data: The JSON data to convert.
    :param output_file: The path to the Markdown file where the content will be written.
    :param prompt_adding: Additional instructions that will be appended to the prompt.
    :param append: If True, the generated Markdown will be appended to the existing file.
                   If False, the file will be overwritten.
    """
    # Build the prompt string
    prompt = f"""
    Convert the following JSON data into a well-structured Markdown format:

    ```json
    {json.dumps(json_data, indent=4)}
    ```

    The Markdown should be:
    - **Concise but readable**
    - **Formatted with headings, lists, and sections**
    - **Avoid unnecessary repetition**
    - **Maintain structured data representation**
    {prompt_adding}

    Output only the Markdown content.
    """

    # Invoke the model to generate the Markdown output
    model = get_model()
    markdown_output = model.invoke(prompt)

    # Determine the file mode based on the 'append' parameter
    file_mode = "a" if append else "w"

    # Write (or append) the Markdown output to file
    with open(output_file, file_mode, encoding="utf-8") as f:
        f.write("\n" + markdown_output.content.strip() + "\n")

    print(f"Markdown file '{output_file}' {'updated' if append else 'created'} successfully using LLM.")
