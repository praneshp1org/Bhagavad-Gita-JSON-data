import nest_asyncio
import os
import json
from llama_parse import LlamaParse


def create_output_directory(directory_path):
    """Creates the output directory if it doesn't already exist."""
    os.makedirs(directory_path, exist_ok=True)


def parse_and_save_markdown(api_key, pdf_path, output_dir):
    """Parses a PDF to Markdown and saves it."""
    print("\nParsing to Markdown...")
    markdown_parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        num_workers=4,
        verbose=True,
        language="en",
    )

    # Load the data as markdown
    markdown_documents = markdown_parser.load_data(pdf_path)

    # Define the output path for markdown
    md_output_filename = "gita.md"
    md_output_path = os.path.join(output_dir, md_output_filename)

    # Create the output directory
    create_output_directory(output_dir)

    # Save the parsed markdown content to a file
    with open(md_output_path, "w", encoding="utf-8") as f:
        # Concatenate text from all documents
        f.write("\n\n".join([doc.text for doc in markdown_documents]))

    print(f"Saved parsed Markdown content to {md_output_path}")


def parse_and_save_json(api_key, pdf_path, output_dir):
    """Parses a PDF to JSON and saves it."""
    print("\nParsing to JSON...")
    json_parser = LlamaParse(
        api_key=api_key,
        result_type="json",
        parsing_instruction="include page breaks in the output",
        num_workers=4,
        verbose=True,
        language="en",
    )

    # Load the data as JSON
    json_documents = json_parser.load_data(pdf_path)

    # Define the output path for JSON
    json_output_filename = "gita.json"
    json_output_path = os.path.join(output_dir, json_output_filename)

    # Create the output directory
    create_output_directory(output_dir)

    # Since result_type is "json", each doc.text is a JSON string.
    # We'll parse them and save as a single, valid JSON file.
    parsed_json_data = [json.loads(doc.text) for doc in json_documents]

    # Save the parsed content to a file
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_json_data, f, indent=4, ensure_ascii=False)

    print(f"Saved parsed JSON content to {json_output_path}")


def main():
    """Main function to run the parsing process."""
    # --- Setup ---
    # Ensure the API key is set in your environment variables
    api_key = os.environ.get("LlamaParse_Key")
    if not api_key:
        raise ValueError("LlamaParse_Key environment variable not set.")

    nest_asyncio.apply()

    pdf_path = os.path.join("textbook_gita", "Gita.pdf")
    print(f"Processing file: {pdf_path}")

    # Define output directories
    base_output_dir = "textbook_gita"
    markdown_dir = os.path.join(base_output_dir, "markdown")
    json_dir = os.path.join(base_output_dir, "json")

    # --- Run Parsers ---
    parse_and_save_markdown(api_key, pdf_path, markdown_dir)
    parse_and_save_json(api_key, pdf_path, json_dir)

    print("\nParsing complete. Both Markdown and JSON files have been saved.")


if __name__ == "__main__":
    main()