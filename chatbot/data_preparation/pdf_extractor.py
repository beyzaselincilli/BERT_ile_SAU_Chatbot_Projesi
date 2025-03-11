import os
import json
import PyPDF2
from tqdm import tqdm

def extract_text_from_pdf(pdf_path):
    """PDF dosyasından metin çıkarma"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"Hata: {pdf_path} dosyası işlenirken bir sorun oluştu - {str(e)}")
        return ""

def clean_text(text):
    """Metni temizleme ve düzenleme"""
    # Gereksiz boşlukları temizle
    text = " ".join(text.split())
    # Birden fazla yeni satırı tek yeni satıra indir
    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
    return text

def process_pdfs(pdf_folder, output_folder):
    """Tüm PDF'leri işle ve sonuçları kaydet"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    documents = []
    
    # PDF dosyalarını listele
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    for pdf_file in tqdm(pdf_files, desc="PDF'ler İşleniyor"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        # PDF'den metin çıkar
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue
            
        # Metni temizle
        cleaned_text = clean_text(text)
        
        # Döküman bilgilerini sakla
        doc_info = {
            "filename": pdf_file,
            "text": cleaned_text,
            "sections": [] # İleride bölümlere ayırmak için
        }
        documents.append(doc_info)
    
    # Sonuçları JSON formatında kaydet
    output_path = os.path.join(output_folder, "extracted_documents.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"\nToplam {len(documents)} PDF dosyası işlendi.")
    print(f"Sonuçlar {output_path} dosyasına kaydedildi.")

if __name__ == "__main__":
    # Doğru klasör yollarını kullan
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_folder = os.path.join(current_dir, "sau_cs_pdf")
    output_folder = os.path.join(current_dir, "outputs")
    process_pdfs(pdf_folder, output_folder) 