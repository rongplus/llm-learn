import torch
from transformers import pipeline
pipe = pipeline(
    task="image-text-to-text",
    model="Qwen/Qwen2.5-VL-7B-Instruct",
    device=0,
    dtype=torch.bfloat16
)
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                #"url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/pipeline-cat-chonk.jpeg", #use url
                "image": "screen.png", # 直接填写本地文件路径
            },
            { "type": "text", "text": "Describe this image."},
        ]
    }
]
aaa = pipe(text=messages,max_new_tokens=20, return_full_text=False)

print("=====-----------------------------------------------------------")
print(aaa)
