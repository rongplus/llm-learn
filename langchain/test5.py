from langchain_ollama import OllamaLLM

# 创建Ollama模型实例
llm = OllamaLLM(model="bakllava")

# 绑定图像上下文信息
llm_with_image_context = llm.bind(images=["D:\\Download2024\\rong.bj\\aa.jpg"])

# 执行模型调用
response = llm_with_image_context.invoke("What is the dollar based gross retention rate:")
print(response)  # 输出：90%



import base64
from io import BytesIO
from PIL import Image

# 将PIL图像转换为Base64字符串
def convert_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# 从本地文件加载图像并转换为Base64
file_path = "D:\\Download2024\\rong.bj\\aa.jpg"
pil_image = Image.open(file_path)
image_b64 = convert_to_base64(pil_image)

from langchain_ollama import OllamaLLM

# 创建Ollama LLM
llm = OllamaLLM(model="bakllava")

# 绑定图像信息
llm_with_image_context = llm.bind(images=[image_b64])

# 发起模型调用
response = llm_with_image_context.invoke("What is the dollar based gross retention rate:")
print(response)  # 输出：90%
