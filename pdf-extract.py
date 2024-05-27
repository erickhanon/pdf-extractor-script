import PyPDF2
import requests
import os
import json
import re

def extract_data_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

    print(f"--- Full text from {pdf_path} ---")
    print(text)
    print("-------------------------------")

    data = {
        "client_number": None,
        "reference_month": None,
        "energia_eletrica_kwh": None,
        "energia_eletrica_valor": None,
        "energia_scee_kwh": None,
        "energia_scee_valor": None,
        "energia_compensada_kwh": None,
        "energia_compensada_valor": None,
        "contrib_ilum_valor": None,
        "installation_number": None,
    }

    client_number_match = re.search(r"\b7\d{9}\b", text)
    if client_number_match:
        data["client_number"] = client_number_match.group(0)

    reference_month_match = re.search(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{2,4}", text)
    if reference_month_match:
        data["reference_month"] = reference_month_match.group(0)

    installation_number_match = re.search(r"\b3\d{9}\b", text)
    if installation_number_match:
        data["installation_number"] = installation_number_match.group(0)

    energia_eletrica_kwh_match = re.search(r"Energia Elétrica\s+kWh\s+(\d+)", text)
    if energia_eletrica_kwh_match:
        data["energia_eletrica_kwh"] = int(energia_eletrica_kwh_match.group(1))

    energia_eletrica_valor_match = re.search(r"Energia Elétrica\s+kWh\s+\d+\s+\S+\s+(\d+,\d+)", text)
    if energia_eletrica_valor_match:
        data["energia_eletrica_valor"] = energia_eletrica_valor_match.group(1).replace(',', '.')

    energia_scee_kwh_match = re.search(r"Energia SCEE s/ ICMS\s+kWh\s+(\d+)", text)
    if energia_scee_kwh_match:
        data["energia_scee_kwh"] = int(energia_scee_kwh_match.group(1))

    energia_scee_valor_match = re.search(r"Energia SCEE s/ ICMS\s+kWh\s+\d+\s+\S+\s+(\d+,\d+)", text)
    if energia_scee_valor_match:
        data["energia_scee_valor"] = energia_scee_valor_match.group(1).replace(',', '.')

    energia_compensada_kwh_match = re.search(r"Energia compensada GD I\s+kWh\s+(\d+)", text)
    if energia_compensada_kwh_match:
        data["energia_compensada_kwh"] = int(energia_compensada_kwh_match.group(1))

    energia_compensada_valor_match = re.search(r"Energia compensada GD I\s+kWh\s+\d+\s+\S+\s+(-\d+,\d+)", text)
    if energia_compensada_valor_match:
        data["energia_compensada_valor"] = energia_compensada_valor_match.group(1).replace(',', '.')

    contrib_ilum_valor_match = re.search(r"Contrib Ilum Publica Municipal\s+(\d+,\d+)", text)
    if contrib_ilum_valor_match:
        data["contrib_ilum_valor"] = contrib_ilum_valor_match.group(1).replace(',', '.')

    print(f"Extracted data from {pdf_path}: {data}")
    
    return data

def send_post_request(data, url):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.status_code, response.text

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_folder_path = os.path.join(script_dir, 'pdf')
    post_url = "http://localhost:3000/faturas"
    
    for pdf_file in os.listdir(pdf_folder_path):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder_path, pdf_file)
            data = extract_data_from_pdf(pdf_path)
            
            if data["client_number"] is None or data["reference_month"] is None or data["installation_number"] is None:
                print(f"Skipping {pdf_file} due to missing required fields.")
                continue
            
            status_code, response_text = send_post_request(data, post_url)
            print(f"Sent data from {pdf_file}, status code: {status_code}, response: {response_text}")

if __name__ == "__main__":
    main()
