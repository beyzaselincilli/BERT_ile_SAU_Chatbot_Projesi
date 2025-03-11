import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
import os

def load_dataset(file_path):
    """Eğitim veya test verisini yükle"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Veriyi uygun formata dönüştür
    formatted_data = []
    for item in data:
        formatted_data.append({
            "text": f"Soru: {item['question']} Cevap: {item['answer']}",
            "label": 1  # Pozitif örnek
        })
    
    return Dataset.from_list(formatted_data)

def train_model():
    # Model ve tokenizer'ı yükle
    model_name = "dbmdz/bert-base-turkish-cased"  # Türkçe BERT modeli
    
    print("Model yükleniyor...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # Veri setlerini yükle
    print("Veri setleri yükleniyor...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    train_dataset = load_dataset(os.path.join(current_dir, "outputs", "train.json"))
    test_dataset = load_dataset(os.path.join(current_dir, "outputs", "test.json"))
    
    # Veriyi tokenize et
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding=True,
            truncation=True,
            max_length=512
        )
    
    print("Veriler tokenize ediliyor...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_test = test_dataset.map(tokenize_function, batched=True)
    
    # Eğitim argümanlarını ayarla
    training_args = TrainingArguments(
        output_dir=os.path.join(current_dir, "outputs", "model"),
        num_train_epochs=5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=os.path.join(current_dir, "outputs", "logs"),
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=50,
        load_best_model_at_end=True,
        save_total_limit=2
    )
    
    # Data collator oluştur
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # Trainer oluştur
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        data_collator=data_collator,
    )
    
    print("Model eğitimi başlıyor...")
    print("Not: CPU üzerinde eğitim yapıldığı için bu işlem biraz zaman alabilir.")
    # Modeli eğit
    trainer.train()
    
    # Modeli kaydet
    model_save_path = os.path.join(current_dir, "outputs", "final_model")
    trainer.save_model(model_save_path)
    tokenizer.save_pretrained(model_save_path)
    
    print(f"Model başarıyla eğitildi ve {model_save_path} konumuna kaydedildi.")

if __name__ == "__main__":
    train_model() 