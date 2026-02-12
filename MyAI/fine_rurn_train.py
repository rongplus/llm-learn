# using a pipeline
from transformers import pipeline

qa = pipeline("text2text-generation", model="google/flan-t5-small")
question  = "When was ACDC formed?"
knowledge = """
    ACDC is the name of a band that was formed in Sydney in 1973.
    The members of the band include Malcolm as the rhythm guitarist and Angus as the lead guitarist.
"""
result = qa("Context: " + knowledge + " Question: " + question)
print("Answer:")
print(result)


#Training
from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import Trainer, AutoModelForSeq2SeqLM
from transformers import Seq2SeqTrainingArguments
from peft import LoraConfig, TaskType, get_peft_model

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
dataset = load_dataset("json", data_files="acdc_qa.json")

def preprocess(example):
    inputs = tokenizer(example["question"], max_length=128, truncation=False, padding="max_length")
    targets = tokenizer(example["answer"], max_length=128, truncation=False, padding="max_length")
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized_dataset = dataset.map(preprocess)
tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])



model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

peft_config = LoraConfig(
    task_type=TaskType.SEQ_2_SEQ_LM,
    inference_mode=False,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1
)

model = get_peft_model(model, peft_config)


#configure and run the trainer:
training_args = Seq2SeqTrainingArguments(
    output_dir="./acdc-finetuned-model",
    per_device_train_batch_size=8,
    num_train_epochs=100,
    logging_steps=1,
    push_to_hub=False,
    learning_rate=1e-3,
    eval_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['train'].select(range(20)),
)

trainer.train()

model.save_pretrained("./acdc-finetuned-model")
tokenizer.save_pretrained("./acdc-finetuned-model")


#Using the Fine Tuned Model
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




#another training sample
from peft import LoraConfig
 
# LoRA config based on QLoRA paper & Sebastian Raschka experiment
peft_config = LoraConfig(
        lora_alpha=128,
        lora_dropout=0.05,
        r=256,
        bias="none",
        target_modules="all-linear",
        task_type="CAUSAL_LM",
)

from transformers import TrainingArguments
 
args = TrainingArguments(
    output_dir="code-llama-7b-text-to-sql", # directory to save and repository id
    num_train_epochs=3,                     # number of training epochs
    per_device_train_batch_size=3,          # batch size per device during training
    gradient_accumulation_steps=2,          # number of steps before performing a backward/update pass
    gradient_checkpointing=True,            # use gradient checkpointing to save memory
    optim="adamw_torch_fused",              # use fused adamw optimizer
    logging_steps=10,                       # log every 10 steps
    save_strategy="epoch",                  # save checkpoint every epoch
    learning_rate=2e-4,                     # learning rate, based on QLoRA paper
    bf16=True,                              # use bfloat16 precision
    tf32=True,                              # use tf32 precision
    max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,                      # warmup ratio based on QLoRA paper
    lr_scheduler_type="constant",           # use constant learning rate scheduler
    push_to_hub=True,                       # push model to hub
    report_to="tensorboard",                # report metrics to tensorboard
)


from trl import SFTTrainer
 
max_seq_length = 3072 # max sequence length for model and packing of the dataset
 
trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    peft_config=peft_config,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    packing=True,
    dataset_kwargs={
        "add_special_tokens": False,  # We template with special tokens
        "append_concat_token": False, # No need to add additional separator token
    }
)

# start training, the model will be automatically saved to the hub and the output directory
trainer.train()
 
# save model
trainer.save_model()
