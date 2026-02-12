from transformers import pipeline

qa_pipeline = pipeline("text2text-generation", model="./acdc-finetuned-model", tokenizer="./acdc-finetuned-model")

questions = [
    "When was ACDC formed?",
    "Where was ACDC formed?",
    "List the members of Cold Chisel.",
    "List the members of ACDC.",
]

for question in questions:
    answer = qa_pipeline(question)
    print(f"{question} Answer: {answer[0]['generated_text']}")