from transformers import AutoTokenizer
from transformers import AutoModel,AutoModelForCausalLM


import torch
from transformers import pipeline
from huggingface_hub import login
login(token = "YOUR_TOKEN")
pipe = pipeline("text-generation", "meta-llama/Meta-Llama-3-8B-Instruct", torch_dtype=torch.bfloat16, device_map="auto")
response = pipe("chat", max_new_tokens=512)
print(response[0]['generated_text']) #[-1]['content']

#model = BertModel.from_pretrained("./test/saved_model/")
checkpoint = "meta-llama/Meta-Llama-3.1-70B-Instruct" #"bert-base-uncased"
model = AutoModelForCausalLM.from_pretrained(checkpoint,is_decoder=True)
tokenizer = AutoTokenizer.from_pretrained(checkpoint,is_decoder=True)

prompt = "卢浮宫在哪年被命名为中央艺术博物馆?"

# Tokenize the prompt
input_ids = tokenizer.encode(prompt, return_tensors="pt")

# Generate text
output = model.generate(input_ids, max_length=100, num_return_sequences=1)

# Decode and print the generated text
generated_text = tokenizer.decode(output, skip_special_tokens=True)
print(generated_text)


import transformers
import torch

model_id = "meta-llama/Meta-Llama-3.1-70B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

outputs = pipeline(
    messages,
    max_new_tokens=256,
)
print(outputs)
print("------------------------")
print(outputs[0])
print("------------------------")
print(outputs[0]["generated_text"])
print("------------------------")
print(outputs[0]["generated_text"][-1])
print("------------------------")

