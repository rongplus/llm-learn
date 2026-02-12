from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from diffusers import StableDiffusionPipeline
import torch

import pyttsx3
from gtts import gTTS

llm = ChatOllama(model="llama3", temperature=0.5)

def text_to_storyboard(text: str):
    prompt = f"""
你是一个视频导演，请把下面文字拆成 5 个分镜。
每个分镜包含：
- scene: 场景描述（适合生成图片）
- narration: 对应旁白

文字：
{text}

用 JSON 数组返回。
"""
    res = llm.invoke([HumanMessage(content=prompt)])
    print(res.content)
    storyboard = json.loads(res.content)

    return {
        "storyboard": storyboard,
        "frames": [],
        "audios": []
    }



# Check for CUDA availability
device = "cpu"
dtype_ = torch.float16 if device == "cuda" else torch.float32

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    dtype=dtype_
).to(device)

def generate_image(prompt, idx):
    image = pipe(prompt).images[0]
    path = f"frames/frame_{idx}.png"
    image.save(path)
    return path




tts =pyttsx3.init()

def generate_voice(text, idx):
    language = 'en' # English
    speech = gTTS(text=text, lang=language, slow=False)
    path = f"audio/audio_{idx}.wav"
    speech.save(path)
    return path




import json, os

os.makedirs("frames", exist_ok=True)
os.makedirs("audio", exist_ok=True)

text = "AI 正在改变世界，但真正重要的是人类如何使用它。"
#json.loads(text_to_storyboard(text))
storyboard = [
  {
    "scene": "A futuristic cityscape with towering skyscrapers and flying cars zipping by",
    "narration": "AI is changing the world..."
  },
  {
    "scene": "A group of people working together in a high-tech laboratory, surrounded by screens and machinery",
    "narration": "...but what's truly important is how humans use it."
  },
  {
    "scene": "A close-up shot of a person holding a smartphone, with AI-powered apps open on the screen",
    "narration": "From personal assistants to medical breakthroughs, AI has the potential to revolutionize our daily lives."
  },
  {
    "scene": "A montage of people from different walks of life using AI-powered tools and technologies, such as virtual reality headsets and self-driving cars",
    "narration": "But it's not just about the tech itself – it's about how we choose to use it to shape our future."
  },
  {
    "scene": "A group of people from different backgrounds and ages gathered around a table, discussing and debating the implications of AI on society",
    "narration": "The question is: will we use AI to create a brighter tomorrow, or just replicate yesterday's problems?"
  }
]

frames = []
audios = []

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
def build_video(frames, audios):
    clips = []

    for img, aud in zip(frames, audios):
        audio = AudioFileClip(aud)
        clip = ImageClip(img).with_duration(audio.duration)
        clip = clip.with_audio(audio)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile("output.mp4", fps=24)

for i, scene in enumerate(storyboard):
    frames.append(generate_image(scene["scene"], i))
    audios.append(generate_voice(scene["narration"], i))

build_video(frames, audios)



