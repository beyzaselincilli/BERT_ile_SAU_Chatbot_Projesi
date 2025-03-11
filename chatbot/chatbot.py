import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import json

class UniversityChatbot:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "outputs", "final_model")
        
        print("Model yükleniyor...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        
        # Dökümanları yükle
        self.documents = self.load_documents()
    
    def load_documents(self):
        """Eğitim verilerini yükle"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "outputs", "extracted_documents.json")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_best_document(self, question):
        """Soru için en uygun dökümanı bul"""
        max_score = -float('inf')
        best_answer = None
        
        # Her döküman için benzerlik skoru hesapla
        for doc in self.documents:
            inputs = self.tokenizer(
                f"Soru: {question} Cevap: {doc['text'][:1000]}",  # İlk 1000 karakter
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                score = outputs.logits[0][1].item()  # Pozitif sınıf skoru
            
            if score > max_score:
                max_score = score
                best_answer = doc['text'][:1500]  # İlk 1500 karakter
        
        return best_answer if best_answer else "Üzgünüm, bu soru için uygun bir cevap bulamadım."

    def generate_response(self, user_input):
        """Kullanıcı sorusuna cevap üret"""
        try:
            # En uygun cevabı bul
            answer = self.find_best_document(user_input)
            
            # Cevabı formatla
            if len(answer) > 1500:
                answer = answer[:1500] + "..."
            
            return answer
            
        except Exception as e:
            return f"Üzgünüm, bir hata oluştu: {str(e)}"

# Global chatbot instance
chatbot = UniversityChatbot()

def ask_chatbot(user_input):
    """Chatbot'a soru sor ve yanıt al"""
    return chatbot.generate_response(user_input)
