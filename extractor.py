import pdfplumber

def extract_text_from_pdf(file_path):
    print(f"Attempting to read: {file_path}...\n")
    
    try:
        # Open the PDF file
        with pdfplumber.open(file_path) as pdf:
            # Grab the first page (index 0)
            first_page = pdf.pages[0]
            
            # Extract the raw text from that page
            text = first_page.extract_text()
            
            print("--- EXTRACTED TEXT ---")
            print(text)
            print("\n--- END OF TEXT ---")
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function and pass in the name of your sample PDF
extract_text_from_pdf('sample_resume.pdf')