from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio
import os
import requests

load_dotenv(override=True)
groq_api = os.getenv('GroQ_API_KEY')
groq_url = "https://api.groq.com/openai/v1"
model_groq = "openai/gpt-oss-120b"
system_prompt = """
You are helpful agent, You have tools such as: {add} when user asks for adding two numbers use it.
{reverse_string} when user asks for reversing a string use it. that's it.
"""

def add(x: int, y: int):
    """
    function adds two numbers
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError("Both arguments must be integers or floats.")
    
    return x + y



add_tool = {
    "name":"add",
    "description":"use this when user asks for adding two numbers",
    "parameters" : {
        "type":"object",
        "properties":{
            "x":{
                "type":"integer",
                "description":"First number"
            },
            "y":{
                "type":"integer",
                "description":"second number"
            }
        },
        "required":["x" , "y"]
    }
}



def reverse_string(string: str):
    """
    function reverses a string
    """

    reversed_string = string[::-1]
    return reversed_string





reverse_tool = {
    "name":"reverse_string",
    "description":"use this when user asks for reversing a string",
    "parameters":{
        "type":"object",
            "properties":{
            "string":{
                "type":"string"
            }
        },

        "required":["string"]
        }

}
tools = [
    {"type":"function","function":reverse_tool},
    {"type":"function","function":add_tool}
]

def execute_tool_use(tools_call):
    
    results =[]
    for tool in tools_call:

        name = tool.function.name
        arguments = json.loads(tool.function.arguments)
        try: 
            if name == "reverse_string":
                result =  reverse_string(**arguments)
            elif name == "add":
                result =  add(**arguments)
            else:
                result = f"That tool {name} not found"
            
        except Exception as e:
            result =  f"Error executing tool {name}: str {e}"

        results.append({
            "role":"tool",
            "content":json.dumps(result),
            "tool_call_id":tool.id
        })
    return results

go = True

while True:
    user_prompt = input("Enter your question: ")

    client = OpenAI(
        api_key=groq_api,
        base_url=groq_url
    )
    massages =[{"role":"user","content":user_prompt},
            {"role":"system","content":system_prompt}]

    response = client.chat.completions.create(
        model=model_groq,
        messages=massages,
        tools=tools
        
    )
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        print(f"The tool is {tool_calls[0].function.name}")
        result = execute_tool_use(tool_calls)
        massages.append(message)
        massages.extend(result)

    else:
        go = False
    answer = client.chat.completions.create(model=model_groq,messages=massages,tools=tools)
    if "quit" in user_prompt:
        break
    else:
        print(answer.choices[0].message.content)

