from unittest import result
from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
import re
import httpx
import requests
import xml.etree.ElementTree as ET
import json
from pydantic import BaseModel, Field
from google import genai 
from google.genai import types 
from typing import List, Optional

ARXIV_NAMESPACE = '{http://www.w3.org/2005/Atom}'

def wikipedia(q):
    try:
        response = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": q,
                "format": "json"
            },
            headers={
                "User-Agent": "LLMAgent/1.0 (learning-project)"
            },
            timeout=10
        )

        if response.status_code == 403:
            return "Wikipedia blocked automated access (403)."

        # Raise error on HTTP failures (403, 429, 500, etc.)
        response.raise_for_status()

        # Wikipedia sometimes returns empty content
        if not response.content:
            return "Wikipedia returned an empty response."

        data = response.json()

        results = data.get("query", {}).get("search", [])
        if not results:
            return f"No Wikipedia results found for '{q}'."

        return results[0]["snippet"]

    except httpx.HTTPError as e:
        return f"Wikipedia HTTP error: {e}"

    except ValueError:
        # JSON decoding failed
        return "Wikipedia returned non-JSON content."

def arxiv_search(q):
    url = f'http://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results=1'
    res = requests.get(url)
    et_root = ET.fromstring(res.content)
    for entry in et_root.findall(f"{ARXIV_NAMESPACE}entry"):
        title = entry.find(f"{ARXIV_NAMESPACE}title").text.strip()
        summary = entry.find(f"{ARXIV_NAMESPACE}summary").text.strip()
    return json.dumps({"title" : title, "summary" : summary})


def calculate(what):
    return eval(what)

client = genai.Client(api_key='AIzaSyBfy5axAy04KvRiC5KUkTwo_sCsMuWlb2Y')  


class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(description="Quantity of the ingredient, including units.")

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
    ingredients: List[Ingredient]
    instructions: List[str]
#print( chat_completion.candidates[0].content.text)
"""
# ----stream model------
chat_completion = client.models.generate_content_stream(  #generate_content_stream
    #model="gpt-4o",
    model="gemini-3-flash-preview",
    contents=[{"role": "user", "parts":  [{"text":  "Hello there!"}] }]
)
for chunk in chat_completion:
    print(chunk.candidates[0].content.parts[0].text)
"""


"""
###---------------------invoeke model------------------------

chat_completion = client.models.generate_content(  #generate_content_stream
    #model="gpt-4o",
    model="gemini-3-flash-preview",
    contents=[{"role": "user", "parts":  [{"text":  "Hello there!"}] }]
)
print("===== Recipe Output =====")
print(chat_completion.text)
#recipe = Recipe.model_validate_json(chat_completion.text)
#print(recipe)
print("===== Recipe Output end =====")

"""


class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if system:
            self.messages.append({"role": "system", "parts":[{"text": self.system}]})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "parts": [{"text": message}]})
        result = self.run_llm()
        self.messages.append({"role": "assistant", "parts": [{"text": result}]})
        return result

    def run_llm(self):
        completion = client.models.generate_content(
                        model="gemini-3-flash-preview",                     
                        contents=self.messages)
        return completion.text
    

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia:
Returns a summary from searching Wikipedia

arxiv_search:
e.g. arxiv_search:
Returns a summary of research papers

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
""".strip()
    
# abot = Agent(prompt)
action_re = re.compile(r'^Action:\s*(\w+)\s*:\s*(.*)$')


class Agent:
    def __init__(self, system_prompt="", max_turns=1, known_actions=None):
        self.max_turns = max_turns
        self.bot = ChatBot(system_prompt)
        self.known_actions = known_actions
        
    def run(self, question):
        i = 0
        next_prompt = question
        
        while i < self.max_turns:
            i += 1
            result = self.bot(next_prompt)
            print(result)
            if "Answer:" in result:
                    print("Final Answer reached. Stopping agent.")
                    return result
            actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
            if actions:
                # There is an action to run
                action, action_input = actions[0].groups()
                if action not in self.known_actions:
                    raise Exception("Unknown action: {}: {}".format(action, action_input))
                print(" -- running {} {}".format(action, action_input))
                observation = self.known_actions[action](action_input)
                print("Observation:", observation)
                next_prompt = "Observation: {}".format(observation) 
            else:
                return
            

known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "arxiv_search": arxiv_search
}
agent = Agent(prompt, max_turns=3, known_actions=known_actions)
agent.run("what is the capital of indonesia?")