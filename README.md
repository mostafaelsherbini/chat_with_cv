# 🤖 Flask AI Agent - CV Expert & Assistant

A production-ready Flask AI Agent designed to answer questions about a personal resume and background. It features robust multi-user session isolation via secure cookies, SQLite database memory management, automated tool execution, and built-in infinite loop safety limits.

---

## ✨ Features
- **Multi-User Session Isolation:** Uses unique UUIDs stored in secure sessions so each user has their own private conversation history.
- **Persistent Memory:** SQLite database integration storing messages securely (`ORDER BY rowid ASC LIMIT 20` to optimize token context).
- **Smart Tool Execution:** 
  - Records unknown questions or communication requests.
  - Sends instant push notifications via Pushover API.
- **Safety Limits:** Built-in `max_iterations` counter to prevent LLM tool infinite loops and control token costs.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask, Flask-Session
- **Database:** SQLite
- **AI / LLM:** Groq API / OpenAI SDK
- **Notifications:** Pushover API

---

## 🚀 Getting Started & Installation

Follow these steps to run the project locally on your machine:

### 1. Clone the Repository
```bash
git clone [https://github.com/mostafaelsherbini/chat_with_cv.git](https://github.com/mostafaelsherbini/chat_with_cv.git)
cd chat_with_cv

2. Create and Activate a Virtual Environment

python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate
# On Linux/Mac:
source venv/bin/activate

3. Install Dependencies

Bash
pip install flask requests openai pypdf python-dotenv

4. Configure Environment Variables

Create a .env file in the root directory of the project and add your API keys:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
PUSHOVER_TOKEN=your_pushover_app_token_here
PUSHOVER_USER=your_pushover_user_key_here

5. Run the Application

Bash
python app.py
Open your browser and navigate to: http://127.0.0.1:5000

🔔 How to Use Pushover Notifications (Optional)
If you want the agent to send notifications to your phone when an important inquiry or unknown question happens:

Create an account on Pushover.

Get your User Key from your dashboard.

Create a new Application/API Token on Pushover to get your App Token.

Add both keys into your .env file as shown above.