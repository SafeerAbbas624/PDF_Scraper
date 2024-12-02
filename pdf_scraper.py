import os
import re
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import openpyxl
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ocr_pdf(input_path, output_path):
    """Run OCRmyPDF on a single PDF file."""
    try:
        subprocess.run(['ocrmypdf', input_path, output_path], check=True)
        logging.info(f"Successfully ran OCR on {input_path}, saved to {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running OCR on {input_path}: {e}")


# Example dictionary with duplicate values
info = {
    'mailing_address': '1743 NW 45 ST 1743 NW 45ST'
}

# Function to remove duplicates within a specific string value
def remove_duplicates(value):
    parts = value.split()  # Split the string into parts
    unique_parts = list(dict.fromkeys(parts))  # Remove duplicates while preserving order
    return ' '.join(unique_parts)  # Join the parts back into a single string



def extract_info(text, filename):
    info = {
        'cfn': '', 'parcel_id': '', 'property_address': '', 'property_city': '', 
        'property_state': '', 'property_zipcode': '', 'mailing_address': '', 
        'mailing_city': '', 'mailing_state': '', 'mailing_zipcode': '', 
        'company_name': '', 'owner_first_name': '', 'owner_last_name': '', 
        'deceased': '', 'notes': '', 'property_tag': '', 'penalty_cost': '', 
        'date_of_violation': '', 'violation': '', 'deadline_of_compliance': '',
    }

    logging.info(f"First 500 characters of extracted text from {filename}:\n{text[:500]}")

    try:
        # Extract CFN, parcel ID, and address information
        cfn_match = re.search(r'(CFN:\s*\d+\s*BOOK\s*\d+\s*PAGE\s*\d+)', text, re.IGNORECASE)
        if cfn_match:
            info['cfn'] = cfn_match.group(1)
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract CFN from the file {filename}.")


    try:
        parcel_match = re.search(r'Folio:\s*(\d+)', text, re.IGNORECASE)
        if parcel_match:
            info['parcel_id'] = parcel_match.group(1)
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Parcel ID or Folio from the file {filename}.")

    try:
        property_match = re.search(r'(?:Property Address|Location of Violation|Address):\s*(.*)', text)
        if property_match:
            info['property_address'] = property_match.group(1).strip()
            info['property_city'] = 'MAIMI'
            info['property_state'] = 'FL'
            info['property_zipcode'] = ''
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Property address fields from the file {filename}.")



    try:
        # Extract mailing address
        mailing_match = re.search(r'(\d+[^,\n]+)\n([^,\n]+),?\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', text) 
        if mailing_match: 
            info['mailing_address'] = mailing_match.group(1).strip()
            info['mailing_address'] = remove_duplicates(info['mailing_address']) 
            info['mailing_city'] = mailing_match.group(2).strip().split()[0]
            info['mailing_state'] = mailing_match.group(3).strip() 
            info['mailing_zipcode'] = mailing_match.group(4).strip()

    except Exception as e:
        logging.error(f"Error processing the mailing zipcode fields: {str(e)}\n Unable to extract mailing zipcode.")

    try:
        # Patterns to identify individual names and company names 
        company_name_pattern = re.compile(r'Name of Violator\(s\):\s*([A-Za-z ]+(?: LLC| INC| CORPORATION| TR| PROPCO| CENTERS))', re.IGNORECASE) 
        individual_name_pattern = re.compile(r'Name of Violator\(s\):\s*([A-Z ,]+(?: &W [A-Z ,]+)?)', re.IGNORECASE)

        company_names = set()
        company_matches = company_name_pattern.findall(text)
        if company_matches:
            for match in company_matches:
                company_names.add(match.strip())
        info['company_name'] = ", ".join(company_names)
        
        individual_matches = individual_name_pattern.findall(text)
        if individual_matches:
            for match in individual_matches:
                if ' LLC' in match or ' INC' in match or ' CORPORATION' in match or ' TR' in match or ' PROPCO' in match or ' CENTERS' in match: 
                    continue
                names = match.split() 
                if len(names) > 1:
                    info['owner_first_name'] = names[0].strip() 
                    info['owner_last_name'] = names[1].strip() 
                else: 
                    info['owner_first_name'] = names[0].strip() 
                    info['owner_last_name'] = ''

    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Owner Name fields from the file {filename}.")

    try:
        # Extract other fields if they exist in the text
        deceased_match = re.search(r'Deceased:\s*(Yes|No)', text, re.IGNORECASE)
        if deceased_match:
            info['deceased'] = deceased_match.group(1).strip()

        notes_match = re.search(r'Notes:\s*(.+)', text, re.IGNORECASE)
        if notes_match:
            info['notes'] = notes_match.group(1).strip()

        if 'Unsafe Structure' in text:
            info['property_tag'] = 'Unsafe Structure'

    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Deceased, Notes & Property tag from the file {filename}.")
    

    # Extracting Panelty Cost
    try:
        pattern = re.compile(r'totaling\s*\$(\d+\.\d{2})')
        penalty = pattern.findall(text)
        if penalty:
            dollar_sign = f'${penalty[0]}'
            info['penalty_cost'] = dollar_sign
        else:
           info['penalty_cost'] = '' 
    
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Panelty cost from the file {filename}.")


    # Extracting Date of Violation
    try:
        pattern1 = re.compile(r'Violation Date\/Time:\s+(\d+\/\d+\/\d+,\s+\d+:\d+\s+[AP]M)')
        date_violation = pattern1.findall(text)
        if date_violation:
            date_of_violation = date_violation[0]
            info['date_of_violation'] = date_of_violation
        else:
           info['date_of_violation'] = '' 
    
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Date of Violation from the file {filename}.")


    # Extracting Code of Violation
    try:
        pattern2 = re.compile(r'Code Section\(s\) Violated:\s*(.*)')
        violation = pattern2.findall(text)
        if violation:
            code_violation = violation[0]
            info['violation'] = code_violation
        else:
           info['violation'] = '' 
    
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract Code of Violation from the file {filename}.")


    # Extracting deadline for compliance
    try:
        pattern3 = re.compile(r'Deadline for Compliance:\s+(\d+\/\d+\/\d+)')
        compliance = pattern3.findall(text)
        if compliance:
            deadline_compliance = compliance[0]
            info['deadline_of_compliance'] = deadline_compliance
        else:
           info['deadline_of_compliance'] = '' 
    
    except Exception as e:
        logging.error(f"Error processing {filename}: {str(e)}\n Unable to extract deadline for compliance from the file {filename}.")


    return info

def process_pdfs(folder_path):
    # Create the output folder for OCR'd PDFs
    ocr_output_folder = 'OCR_Documents'
    os.makedirs(ocr_output_folder, exist_ok=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        'CFN', 'Parcel ID', 'Property Address', 'Property City', 'Property State', 
        'Property Zipcode', 'Mailing Address', 'Mailing City', 'Mailing State', 
        'Mailing Zipcode', 'Company Name', 'Owner First Name', 'Owner Last Name', 
        'Deceased', 'Notes', 'Property Tag', 'Penalty Cost', 
        'Date of Violation', 'Violation Code', 'Deadline for Compliance',
    ])

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            ocr_output_path = os.path.join(ocr_output_folder, filename)

            # Run OCR on the PDF and save to the output folder
            ocr_pdf(pdf_path, ocr_output_path)

            try:
                doc = fitz.open(ocr_output_path)
                text = ""
                for page in doc:
                    text += page.get_text()

                # If no text was extracted, try OCR with PyTesseract
                if not text.strip():
                    for page in doc:
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        text += pytesseract.image_to_string(img)

                info = extract_info(text, filename)
                ws.append([
                    info['cfn'], info['parcel_id'], info['property_address'], info['property_city'], 
                    info['property_state'], info['property_zipcode'], info['mailing_address'], 
                    info['mailing_city'], info['mailing_state'], info['mailing_zipcode'], 
                    info['company_name'], info['owner_first_name'], info['owner_last_name'], 
                    info['deceased'], info['notes'], info['property_tag'], info['penalty_cost'],
                    info['date_of_violation'], info['violation'], info['deadline_of_compliance']
                ])
                logging.info(f"Successfully processed {filename}")
            except Exception as e:
                logging.error(f"Error processing {filename}: {str(e)}")

    output_file = 'code_enforcement_data.xlsx'
    wb.save(output_file)
    logging.info(f"Data saved to {output_file}")

if __name__ == "__main__":
    folder_path = 'all_pdf'
    process_pdfs(folder_path)
