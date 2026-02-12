from google import genai 
from google.genai import types 

read_file_definition = {  
    "name": "read_file",  
    "description": "Reads a file and returns its contents.",  
    "parameters": {  
        "type": "object",  
        "properties": {  
            "file_path": {"type": "string"}  
        },  
        "required": ["file_path"],  
    },  
}  
   
list_dir_definition = {  
    "name": "list_dir",  
    "description": "Lists the files in a directory.",  
    "parameters": {  
        "type": "object",  
        "properties": {  
            "directory_path": {"type": "string"}  
        },  
        "required": ["directory_path"],  
    },  
}  
   
write_file_definition = {  
    "name": "write_file",  
    "description": "Writes contents to a file.",  
    "parameters": {  
        "type": "object",  
        "properties": {  
            "file_path": {"type": "string"},  
            "contents": {"type": "string"},  
        },  
        "required": ["file_path", "contents"],  
    },  
 }

def read_file(file_path: str) -> dict:  
    with open(file_path, "r") as f:  
        return f.read()  
   
def write_file(file_path: str, contents: str) -> bool:  
    with open(file_path, "w") as f:  
        f.write(contents)  
    return True  
   
def list_dir(directory_path: str) -> list[str]:  
     return os.listdir(directory_path)


file_tools = {  
     "read_file": {"definition": read_file_definition, "function": read_file},  
     "write_file": {"definition": write_file_definition, "function": write_file},  
     "list_dir": {"definition": list_dir_definition, "function": list_dir},  
 }

class Agent:  
    def __init__(self, model: str, tools: dict,   
                 system_instruction="You are a helpful assistant."):  
        self.model = model  
        self.client = genai.Client(api_key='AIzaSyBfy5axAy04KvRiC5KUkTwo_sCsMuWlb2Y')  
        self.contents = []  
        self.tools = tools  
        self.system_instruction = system_instruction  
   
    def run(self, contents):  
        # Add user input to history  
        if isinstance(contents, list):  
            self.contents.append({"role": "user", "parts": contents})  
        else:  
            self.contents.append({"role": "user", "parts": [{"text": contents}]})  
   
        config = types.GenerateContentConfig(  
            system_instruction=self.system_instruction,  
            tools=[types.Tool(  
                function_declarations=[  
                    tool["definition"] for tool in self.tools.values()  
                ]  
            )],  
        )  
   
        response = self.client.models.generate_content(  
            model=self.model,  
            contents=self.contents,  
            config=config  
        )  
   
        # Save model output  
        self.contents.append(response.candidates[0].content)  
   
        # If model wants to call tools  
        if response.function_calls:  
            functions_response_parts = []  
   
            for tool_call in response.function_calls:  
                print(f"[Function Call] {tool_call}")  
   
                if tool_call.name in self.tools:  
                    result = {"result": self.tools[tool_call.name]["function"](**tool_call.args)}  
                else:  
                    result = {"error": "Tool not found"}  
   
                print(f"[Function Response] {result}")  
   
                functions_response_parts.append(  
                    {"functionResponse": {"name": tool_call.name, "response": result}}  
                )  
   
            # Feed tool results back to the model  
            return self.run(functions_response_parts)  
          
        return response


agent = Agent(  
    #model="gemini-3-pro-preview",  
    model="gemini-3-flash-preview",
    tools=file_tools,  
    system_instruction="You are a helpful Coding Assistant. Respond like Linus Torvalds."  
)  
   
print("Agent ready. Type something (or 'exit').")  
while True:  
    user_input = input("You: ")  
    if user_input.lower() in ['exit', 'quit']:  
        break  
   
    response = agent.run(user_input)  
    print("Linus:", response.text, "\n")