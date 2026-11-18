from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio as gr
import os
import requests
from pypdf import PdfReader
from flask import Flask, render_template , request , jsonify ,session
import sqlite3
import uuid


app = Flask(__name__)

load_dotenv(override=True)
app.secret_key  = os.getenv("flask_secrete_key")
groq_api = os.getenv("GroQ_API_KEY")
pushover_user = os.getenv("PUSH_OVER_USER")
pushover_token = os.getenv("PUSH_OVER_TOKEN")
pushover_base_url = "https://api.pushover.net/1/messages.json"
groq_url = "https://api.groq.com/openai/v1"
model = "openai/gpt-oss-120b"
my_cv = r"E:\Python APIs_Flask\cvs\my_cv.pdf"

client = OpenAI(
    api_key=groq_api,
    base_url=groq_url
)

def get_db():
    return sqlite3.connect("memmory.db")


db = get_db()
cr = db.cursor()
cr.execute("CREATE TABLE if not exists memmory(role text,content text,id_session text)")
    

reader = PdfReader(my_cv)
cv_text = ""
for page in reader.pages:
    cv_text += page.extract_text() + "\n"

system_prompt = f"""
You are my assistant. You have my cv: {cv_text} 
Use it to answer questions about me and my cv.
Instructions: 1. Don't answer questions out of that topic (e.g., what's the capital of Egypt?), except for basic greeting questions (e.g., how are you?).
2. **CRITICAL RULE FOR TOOLS**: You have full access to the conversation history. When using `record_communication`, you MUST review the entire chat history to collect ALL required details (`email`, `name`, `note` containing agency name and role info) before invoking the tool. Do NOT call the tool prematurely if the user provided their name or agency in previous messages. 
If any crucial detail is genuinely missing across the whole conversation, ask the user for it first.
You have full access to the conversation history. When using `record_communication`, you MUST review the entire chat history to collect ALL required details (`email`, `name`, `note` containing agency name and role info) before invoking the tool. 

3. **CRITICAL RULE FOR SENDER DATA (MOUSTAFA'S DATA PROTECTION)**: 
- Moustafa (the owner of this CV and bot) is the person **receiving** the offers. 
- **NEVER** use Moustafa's own name, email, or personal data found in the CV or system prompt as the sender's data in `record_communication`. 
- If the person talking to you (the sender) has not explicitly provided **their own** separate email and name in the conversation, you MUST stop and ask them for their email and name first before calling the tool. Do not guess or substitute.
You have two tools you can use: 
1. `record_unknown_question`: Use it when the user asks you a question about me or my cv that you don't know. (Don't use it for unrelated questions).
2. `record_communication`: Use it when someone asks to talk to me about work like an interview, job, internship, or meeting. (Don't use it if the user wants to talk about something else or doesn't specify the work purpose).
"""

def push(message):
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_base_url, data=payload)

def record_unknown_question(question):
    push(f"The question is: {question}")
    return "recorded done"

def record_communication(email, name="not provided", note="not provided"):
    push(f"Email: {email}, Name: {name}, Note: {note}")
    return "recorded done"

# تصحيح مكان required ونوع الـ email
record_unknown_tool = {
    "name": "record_unknown_question",
    "description": "Use this tool when the user asks you a question you don't know about me or my cv",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The unknown question"
            }
        },
        "required": ["question"]
    }   
}

record_communicate_tool = {
    "name": "record_communication",
    "description": "Use it when the user asks to talk to me about work or offers a job, interview, or internship",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",  # الصح string مش email
                "description": "The email of the user"
            },
            "name": {
                "type": "string",
                "description": "The name of the user if available"
            },
            "note": {
                "type": "string",
                "description": "Note about what he wants"
            }
        },
        "required": ["email"]
    }
}

tools_to_use = [
    {"type": "function", "function": record_unknown_tool},
    {"type": "function", "function": record_communicate_tool}
]

def handel_tools_use(tool_calls):
    results = []
    for tool in tool_calls:
        name = tool.function.name
        try:
            arguments = json.loads(tool.function.arguments)
            if name == "record_communication":
                result = record_communication(**arguments)
            elif name == "record_unknown_question":
                result = record_unknown_question(**arguments)
            else:
                result = f"This tool {name} is not found"
        except Exception as e:
            result = f"Error handling tool {name}: {e}"
        
        results.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool.id
        })
    return results


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=['POST'])
def chat():
    db = get_db()
    cr = db.cursor()
    try:
        data = request.get_json()

        if not data:
            db.close()
            return jsonify({"response": "Please send a message."}), 400

        user_prompt = data.get("message", "")
        if not user_prompt:
            db.close()
            return jsonify({"response": "message cannot be empty."}), 400
        

        current_user_id = session.get('user_id')
        if not current_user_id:
            current_user_id = str(uuid.uuid4())
            session['user_id'] = current_user_id
            user_history = []
        else:
            cr.execute("SELECT role,content FROM memmory WHERE id_session=? ORDER BY rowid ASC LIMIT 20",(current_user_id,))
            user_history = cr.fetchall()


        history_raws = user_history

        history = [
            {"role":str(row[0]), "content":str(row[1])}
            for row in history_raws
        ]

        cr.execute("INSERT INTO memmory(role,content,id_session) values(?,?,?)",("user",user_prompt,current_user_id,))
        db.commit()

        messages = [{"role":"system","content":system_prompt}] + history + [{"role":"user","content":user_prompt}] 

        max_iterations = 5
        turns = 0
        while True:
            if turns >= max_iterations:
                return jsonify({"response": "Excuse me Thers is something wrong happed in the tools"}), 500

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools_to_use
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            llm_resp = message.content
            if finish_reason == "tool_calls":
                turns = turns+1
                print(f"This tool is {message.tool_calls[0].function.name}")
                result = handel_tools_use(message.tool_calls)
                messages.append(message)
                messages.extend(result)
            else:
                if llm_resp:
                
                    cr.execute("insert into memmory(role,content,id_session) values(?,?,?)", ("assistant",llm_resp,current_user_id,))
                    db.commit()
                return jsonify({"response": llm_resp})
    finally:
        db.close()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)