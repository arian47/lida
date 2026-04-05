import nbformat
from nbconvert import WebPDFExporter

def convert_ipynb_to_pdf(input_filepath, output_filepath):
    """
    Converts a Jupyter Notebook to PDF using a headless browser.
    This guarantees that what you see in Jupyter is what you get in the PDF.
    """
    print(f"Loading '{input_filepath}'...")
    
    # 1. Read the notebook file
    with open(input_filepath, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    print("Rendering PDF via headless browser (this may take a few seconds)...")
    
    # 2. Initialize the WebPDFExporter
    exporter = WebPDFExporter()
    
    # Optional: Hide input code cells if you only want the output/report
    # exporter.exclude_input = True 
    
    # 3. Convert the notebook to PDF bytes
    pdf_data, resources = exporter.from_notebook_node(notebook)

    # 4. Write the bytes to a file
    with open(output_filepath, 'wb') as f:
        f.write(pdf_data)
        
    print(f"Success! Saved as '{output_filepath}'")

# if __name__ == "__main__":
#     # Replace with your actual filenames
#     convert_ipynb_to_pdf("your_notebook.ipynb", "final_report.pdf")

convert_ipynb_to_pdf(
    "notebooks/report.ipynb",
    "notebooks/final_report.pdf"
)