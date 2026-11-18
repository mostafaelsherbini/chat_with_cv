from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio
import os

load_dotenv(override=True)

open_router_api = os.getenv('OPENROUTER_API_KEY')

model = "nvidia/nemotron-3.5-super-vl:free"
system_prompt = "You are a helpful assistant"
    
while True:
    user_prompt = input("Enter your Question? ")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=open_router_api
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role":"system",
                "content":system_prompt
            },
            {
                "role":"user",
                "content":user_prompt
            }
        ]


    )
    answer = response.choices[0].message.content
    if "quit" in user_prompt:
        break
    else:
        print(answer)

