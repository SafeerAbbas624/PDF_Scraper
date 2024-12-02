# PDF Scraper with OCR

This project is a Python-based PDF scraper that utilizes Optical Character Recognition (OCR) to extract information from PDF documents. It processes PDF files, extracts relevant data, and saves the results in an Excel spreadsheet. The project is designed to handle various formats of property-related documents, making it useful for real estate professionals, researchers, and data analysts.

## Features

- **OCR Processing**: Uses `ocrmypdf` to convert scanned PDF documents into searchable PDFs.
- **Data Extraction**: Extracts key information such as:
  - CFN (Case File Number)
  - Parcel ID
  - Property Address
  - Mailing Address
  - Company Name
  - Owner's Name
  - Violation Details
  - Penalty Costs
  - Dates of Violations and Compliance
- **Duplicate Removal**: Cleans up mailing addresses by removing duplicate entries.
- **Excel Output**: Saves the extracted data into an Excel file for easy access and analysis.
- **Logging**: Provides detailed logging of the processing steps and any errors encountered.

## Installation

To set up the project on your local machine, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/pdf_scraper.git
   cd pdf_scraper
   ```

2. **Install Required Dependencies**:
   Make sure you have Python installed (preferably Python 3.6 or higher). Then, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install OCRmyPDF**:
   This project requires `ocrmypdf` for OCR processing. You can install it using the following command:
   - For Ubuntu:
     ```bash
     sudo apt-get install ocrmypdf
     ```
   - For macOS (using Homebrew):
     ```bash
     brew install ocrmypdf
     ```

4. **Install Tesseract**:
   You also need to install Tesseract OCR. Follow the instructions for your operating system:
   - For Ubuntu:
     ```bash
     sudo apt-get install tesseract-ocr
     ```
   - For macOS (using Homebrew):
     ```bash
     brew install tesseract
     ```

5. **Install Additional Libraries**:
   Ensure you have the following libraries installed:
   ```bash
   pip install PyMuPDF pytesseract Pillow openpyxl
   ```

## Usage

1. **Prepare Your PDF Files**:
   Place all the PDF files you want to process in a folder named `all_pdf` within the project directory.

2. **Run the Script**:
   Execute the script to start processing the PDFs:
   ```bash
   python pdf_scraper.py
   ```

3. **Output**:
   The processed data will be saved in an Excel file named `code_enforcement_data.xlsx` in the project directory. You can open this file with any spreadsheet software to view the extracted information.

## Code Overview

- **ocr_pdf(input_path, output_path)**: This function runs OCRmyPDF on a single PDF file to convert it into a searchable format.
- **remove_duplicates(value)**: This function removes duplicate words from a string, preserving the order of the first occurrences.
- **extract_info(text, filename)**: This function extracts relevant information from the text of the PDF using regular expressions.
- **process_pdfs(folder_path)**: This function processes all PDF files in the specified folder, running OCR and extracting data.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

