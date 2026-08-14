from flask import Flask, render_template_string, request
import requests
import os
from core.ai_providers import load_provider_keys

app = Flask(__name__)

_keys = load_provider_keys()
API_KEY = _keys.get("openrouter") or os.getenv("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenRouter Prompt Tester</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #0078d7, #00b7c3);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }
        .container {
            background: #fff;
            margin-top: 50px;
            padding: 30px;
            border-radius: 12px;
            width: 700px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #0078d7;
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 15px;
            resize: vertical;
            margin-bottom: 15px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #0078d7;
            color: white;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #005fa3;
        }
        .response-box {
            margin-top: 25px;
            padding: 20px;
            background: #f9fafb;
            border-left: 5px solid #0078d7;
            border-radius: 8px;
            white-space: pre-wrap;
            font-family: Consolas, monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        .response-box strong {
            color: #333;
            font-size: 18px;
        }
        code {
            background: #eee;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: Consolas, monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OpenRouter Prompt Tester</h1>
        <form method="POST">
            <label><strong>Enter your prompt:</strong></label><br>
            <textarea name="prompt" rows="5"></textarea><br>
            <button type="submit">Send Prompt</button>
        </form>
        {% if response %}
            <div class="response-box">
                <strong>Response:</strong><br>
                {{ response }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None
    if request.method == "POST":
        user_prompt = request.form["prompt"]
        payload = {
            "model": "tencent/hy3:free",  # ✅ correct model ID
            "messages": [{"role": "user", "content": user_prompt}]
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        r = requests.post(BASE_URL, json=payload, headers=headers)
        data = r.json()

        if "choices" in data:
            response_text = data["choices"][0]["message"]["content"]
        else:
            response_text = f"Error: {data}"
    return render_template_string(HTML_TEMPLATE, response=response_text)

if __name__ == "__main__":
    app.run(debug=True)
