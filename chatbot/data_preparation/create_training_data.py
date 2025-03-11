import json
import os
from sklearn.model_selection import train_test_split

def load_documents(json_path):
    """JSON dosyasından dökümanları yükle"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_qa_pairs(documents):
    """Dökümanlardan soru-cevap çiftleri oluştur"""
    qa_pairs = []
    
    for doc in documents:
        text = doc['text']
        filename = doc['filename']
        
        # Başlık bilgisinden soru oluştur
        title = filename.replace('.pdf', '').replace('_', ' ')
        qa_pairs.append({
            'question': f"{title} hakkında bilgi ver?",
            'answer': text[:1000],  # İlk 1000 karakter
            'document': filename
        })
        
        # Yönetmelik/yönerge içeriği hakkında genel soru
        qa_pairs.append({
            'question': f"Bu yönetmelik/yönergenin amacı nedir?",
            'answer': text[:1500],  # İlk 1500 karakter
            'document': filename
        })
        
        # Bölümler ve maddeler hakkında sorular
        if "MADDE" in text:
            qa_pairs.append({
                'question': f"Bu yönetmelik/yönergede hangi maddeler bulunmaktadır?",
                'answer': text,
                'document': filename
            })
    
    return qa_pairs

def save_dataset(qa_pairs, output_folder):
    """Veri setini eğitim ve test olarak kaydet"""
    # Veri setini böl
    train_pairs, test_pairs = train_test_split(
        qa_pairs, test_size=0.2, random_state=42
    )
    
    # Eğitim verisini kaydet
    train_path = os.path.join(output_folder, "train.json")
    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_pairs, f, ensure_ascii=False, indent=2)
    
    # Test verisini kaydet
    test_path = os.path.join(output_folder, "test.json")
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"Toplam {len(qa_pairs)} soru-cevap çifti oluşturuldu")
    print(f"Eğitim seti: {len(train_pairs)} çift")
    print(f"Test seti: {len(test_pairs)} çift")

if __name__ == "__main__":
    # Doğru klasör yollarını kullan
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(current_dir, "outputs", "extracted_documents.json")
    output_folder = os.path.join(current_dir, "outputs")
    
    # Dökümanları yükle
    documents = load_documents(json_path)
    
    # Soru-cevap çiftleri oluştur
    qa_pairs = create_qa_pairs(documents)
    
    # Veri setini kaydet
    save_dataset(qa_pairs, output_folder) 