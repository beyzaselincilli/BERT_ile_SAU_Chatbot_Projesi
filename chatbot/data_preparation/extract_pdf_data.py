import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import pandas as pd
import json
import sqlite3
from glob import glob
import re
import textwrap  

def extract_text_with_ocr(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    extracted_text = []
    for page in pages:
        text = pytesseract.image_to_string(page, lang="tur")
        extracted_text.append(text.strip())
    return "\n".join(extracted_text)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9ğüşöçıİĞÜŞÖÇ,.!?;:\n ]', '', text)
    return text.strip()

def classify_document(text):
    categories = {
        "Eğitim": ["ders", "üniversite", "öğrenci", "akademik"],
        "Sağlık": ["hastane", "doktor", "tedavi", "ilaç"],
        "Finans": ["banka", "bütçe", "vergi", "yatırım"],
        "Teknoloji": ["yazılım", "kod", "sistem", "donanım"]
    }
    for category, keywords in categories.items():
        if any(keyword in text.lower() for keyword in keywords):
            return category
    return "Genel"

def chunk_text(text, max_length=500):
    """
    Chatbot sistemleri için uzun metni küçük parçalara böl.
    """
    return textwrap.wrap(text, width=max_length)

def save_to_database(db_path, pdf_name, tables):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_name TEXT,
            table_data TEXT
        )
    """)
    for table in tables:
        table_json = json.dumps(table)
        cursor.execute("INSERT INTO pdf_tables (pdf_name, table_data) VALUES (?, ?)", (pdf_name, table_json))
    conn.commit()
    conn.close()

def process_pdfs(pdf_folder, output_folder, db_path):
    metinler_folder = os.path.join(output_folder, "metinler")
    tablolar_folder = os.path.join(output_folder, "tablolar")
    chatbot_folder = os.path.join(output_folder, "chatbot_chunks")
    os.makedirs(metinler_folder, exist_ok=True)
    os.makedirs(tablolar_folder, exist_ok=True)
    os.makedirs(chatbot_folder, exist_ok=True)

    chatbot_jsonl_path = os.path.join(chatbot_folder, "chatbot_dataset.jsonl")
    with open(chatbot_jsonl_path, "w", encoding="utf-8") as chatbot_file:

        pdf_files = sorted(glob(os.path.join(pdf_folder, "*.pdf")))
        for pdf_path in pdf_files:
            text_content = []
            tables_list = []
            ocr_used = False

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(clean_text(text))
                    else:
                        print(f"OCR kullanılıyor: {pdf_path}")
                        text_content.append(clean_text(extract_text_with_ocr(pdf_path)))
                        ocr_used = True

                    for table in page.extract_tables():
                        if table:
                            df = pd.DataFrame(table).dropna(how='all')
                            if df.shape[1] > 2:
                                tables_list.append(df.to_dict(orient='records'))

            pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
            full_text = "\n".join(text_content)
            category = classify_document(full_text)

          
            output_json = {
                "pdf_name": pdf_basename,
                "category": category,
                "ocr_used": ocr_used,
                "text": full_text
            }

            json_path = os.path.join(metinler_folder, f"{pdf_basename}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(output_json, f, ensure_ascii=False, indent=4)

          
            if tables_list:
                table_json_path = os.path.join(tablolar_folder, f"{pdf_basename}.json")
                with open(table_json_path, "w", encoding="utf-8") as f:
                    json.dump(tables_list, f, ensure_ascii=False, indent=4)
                save_to_database(db_path, pdf_basename, tables_list)
            else:
                print(f"{pdf_path} içinde geçerli tablo bulunamadı.")

           
            for chunk in chunk_text(full_text):
                chatbot_entry = {
                    "text": chunk,
                    "source": pdf_basename,
                    "category": category
                }
                chatbot_file.write(json.dumps(chatbot_entry, ensure_ascii=False) + "\n")

            print(f"{pdf_path} işlendi: {json_path} ve {len(tables_list)} tablo kaydedildi.")

if __name__ == "__main__":
    pdf_folder = r"C:\\Users\\User\\Desktop\\sau_cs_pdf\\sau_cs_pdf"
    output_folder = r"C:\\Users\\User\\Desktop\\outputs\\outputs"
    db_path = os.path.join(output_folder, "tablo_verileri.db")
    process_pdfs(pdf_folder, output_folder, db_path)
