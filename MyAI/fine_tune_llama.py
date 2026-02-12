

from transformers import LlamaForCausalLM, AutoTokenizer, Trainer, TrainingArguments, AutoModelForCausalLM, \
    AutoTokenizer
from datasets import load_dataset
from huggingface_hub import login
login()
from huggingface_hub import whoami

user = whoami(token=...)
print(user)
# 加载模型和分词器
model_name = "llama3.2:3b-instruct-fp16 "  # 替换为你的模型名称
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name, legacy=False)

# 检查词汇文件路径
print(type(tokenizer))

# 确保分词器有 pad_token
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    model.resize_token_embeddings(len(tokenizer))

# 加载数据集
dataset = load_dataset("json", data_files="training_data.json")

# 数据预处理
def preprocess_function(examples):
    inputs = examples["prompt"]
    targets = examples["completion"]
    model_inputs = tokenizer(inputs, max_length=64, truncation=True, padding="max_length")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=64, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# 确保数据集不为空
if len(dataset["train"]) == 0:
    raise ValueError("The dataset is empty. Please check the dataset file.")

# 数据预处理
tokenized_dataset = dataset["train"].map(preprocess_function, batched=True)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="no",  # 设置为 "no" 以避免验证
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    num_train_epochs=5,  # 增加训练轮数
    weight_decay=0.01,
    remove_unused_columns=False,  # 设置为 False 以避免删除未使用的列
)

# 使用Trainer进行训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()

# 手动保存模型和分词器
trainer.save_model("./results")
tokenizer.save_pretrained("./results")