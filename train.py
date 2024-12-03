from transformers import LlamaForCausalLM, LlamaTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Carregar modelo e tokenizer
model_name = "meta-llama/Llama-3.1-8B"
model = LlamaForCausalLM.from_pretrained(model_name)
tokenizer = LlamaTokenizer.from_pretrained(model_name)

# Preparar dados
dataset = load_dataset("json", data_files={"train": "data.jsonl"})
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Configurar treinamento
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=2,
    num_train_epochs=3,
    weight_decay=0.01,
    save_strategy="epoch",
    logging_dir='./logs',
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
)

# Treinar o modelo
trainer.train()

from transformers import pipeline

model_path = "./results"
generator = pipeline("text-generation", model=model_path, tokenizer=model_path)

response = generator("Quem é a equipe da reitoria da UERN?")
print(response)
