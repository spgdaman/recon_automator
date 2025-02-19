import os

# statement = "Statement 31_01_2025 15_11_59 EAT new.pdf.pdf"
# erp_file = 'C:\Users\Simon\My Drive\Documents\Development\finance_automation\files\BRSListing.xls'

class InvalidFileFormatError(Exception):
    """Custom exception for invalid file formats."""
    pass

# a function to check the csv format of a file
def is_valid_csv_file_format(file):
    valid_extensions = {'.csv'}
    file_extension = os.path.splitext(file)[1].lower()

    if file_extension in valid_extensions:
        return True
    else:
        raise InvalidFileFormatError(f"Invalid file format: {file_extension}. Allowed formats is CSV")
    
# a function to check the Excel format of a file
def is_valid_excel_file_format(file):
    valid_extensions = {'.xlsx', '.xls'}
    file_extension = os.path.splitext(file)[1].lower()

    if file_extension in valid_extensions:
        return True
    else:
        raise InvalidFileFormatError(f"Invalid file format: {file_extension}. Allowed formats is Excel (.xlsx or .xls)")


# a function to check the Excel format of a file
def is_valid_pdf_file_format(file):
    valid_extensions = {'.pdf'}
    file_extension = os.path.splitext(file)[1].lower()

    if file_extension in valid_extensions:
        return True
    else:
        raise InvalidFileFormatError(f"Invalid file format: {file_extension}. Allowed formats is Excel (.xlsx or .xls)")
    

def pdf_cleaner(file):
    import pandas as pd
    import pdfplumber

    def extract_pdf_table(pdf_path, page_num=0):
        """Extracts tables from a given PDF page into a Pandas DataFrame."""
        with pdfplumber.open(pdf_path) as pdf:
            table = pdf.pages[page_num].extract_table()
        
        if table:
            df = pd.DataFrame(table[1:], columns=table[0])  # First row as headers
            return df
        else:
            raise ValueError("No tables found in the PDF.")

    if is_valid_pdf_file_format(file) == True:
        # Example usage
        df = extract_pdf_table(file)
        print(df)

