from langchain_classic.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate

from langchain_ollama import ChatOllama, OllamaEmbeddings

llm = ChatOllama(
    model="llama3",
    temperature=0.7
)
prompt = PromptTemplate(
    input_variables=["image_desc"],
    template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
)
chain = LLMChain(llm=llm, prompt=prompt)
image_desc = chain.invoke("halloween night at a haunted museum")

#image_desc = "halloween night at a haunted museum"
refined_prompt = chain.invoke({"image_desc": image_desc})["text"]
print(f"Refined Prompt: {refined_prompt}")

import cv2
from diffusers import StableDiffusionPipeline
import torch
# Check for CUDA availability
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", torch_dtype=dtype).to(device)



image = pipe(refined_prompt).images[0]
image.save("generated.png")
cv2.imshow("image", cv2.imread("generated.png"))
