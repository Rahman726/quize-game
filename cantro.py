from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Master AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .chat-container {
            background-color: white;
            border-radius: 0 0 5px 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            height: 500px;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
        }
        .bot-message {
            background-color: #f1f1f1;
            margin-right: auto;
        }
        .input-container {
            display: flex;
            margin-bottom: 20px;
        }
        #user-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        #send-button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
            font-size: 16px;
        }
        #send-button:hover {
            background-color: #45a049;
        }
        .typing-indicator {
            display: none;
            color: #888;
            font-style: italic;
            margin-bottom: 15px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 10px;
            }
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Python Master AI</h1>
        </div>
        <div class="chat-container" id="chat-container">
            <div class="bot-message message">
                Hello! I'm your Python Master AI. How can I help you with Python today?
            </div>
            <div class="typing-indicator" id="typing-indicator">
                Python Master is typing...
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Ask me anything about Python..." autocomplete="off">
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const typingIndicator = document.getElementById('typing-indicator');

        function addMessage(message, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.textContent = message;
            chatContainer.insertBefore(messageDiv, typingIndicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (message === '') return;

            addMessage(message, true);
            userInput.value = '';
            showTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                const data = await response.json();
                hideTypingIndicator();
                addMessage(data.response, false);
            } catch (error) {
                hideTypingIndicator();
                addMessage("Sorry, I encountered an error. Please try again.", false);
                console.error('Error:', error);
            }
        }

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# AI responses - simple Python knowledge base
PYTHON_KNOWLEDGE = {
    "hello": "Hello! I'm your Python Master AI. How can I help you with Python today?",
    "hi": "Hi there! Ready to dive into Python programming? What's your question?",
    "what is python": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data analysis, AI, and more.",
    "how to install python": "You can install Python from the official website (python.org). Download the installer for your operating system and run it. Make sure to check 'Add Python to PATH' during installation.",
    "print hello world": "To print 'Hello World' in Python, use: `print('Hello World')`",
    "create a function": "Here's how to create a function in Python:\n\n```python\ndef function_name(parameters):\n    # Function body\n    return result\n```",
    "list comprehension": "List comprehension is a concise way to create lists. Example:\n\n```python\nsquares = [x**2 for x in range(10)]\n```",
    "dictionary": "A dictionary stores key-value pairs:\n\n```python\nmy_dict = {'key1': 'value1', 'key2': 'value2'}\n```",
    "for loop": "A for loop in Python:\n\n```python\nfor item in sequence:\n    # do something with item\n```",
    "while loop": "A while loop in Python:\n\n```python\nwhile condition:\n    # do something\n```",
    "import module": "To import a module:\n\n```python\nimport module_name\n```\nOr import specific functions:\n\n```python\nfrom module_name import function_name\n```",
    "virtual environment": "To create a virtual environment:\n\n```bash\npython -m venv myenv\n```\nActivate it:\n- Windows: `myenv\\Scripts\\activate`\n- Mac/Linux: `source myenv/bin/activate`",
    "pip install": "To install a package with pip:\n\n```bash\npip install package_name\n```",
    "python frameworks": "Popular Python frameworks:\n- Web: Django, Flask, FastAPI\n- Data: Pandas, NumPy\n- AI: TensorFlow, PyTorch",
    "flask": "Flask is a lightweight web framework. Basic app:\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello, World!'\n\nif __name__ == '__main__':\n    app.run()\n```",
    "django": "Django is a full-featured web framework. To start a project:\n\n```bash\ndjango-admin startproject projectname\n```",
    "data types": "Python has several built-in data types:\n- Numeric: int, float, complex\n- Sequence: list, tuple, range\n- Text: str\n- Mapping: dict\n- Set: set, frozenset\n- Boolean: bool\n- Binary: bytes, bytearray",
    "exception handling": "Use try-except blocks:\n\n```python\ntry:\n    # code that might raise an exception\nexcept ExceptionType:\n    # handle the exception\n```",
    "classes": "Here's a simple class:\n\n```python\nclass MyClass:\n    def __init__(self, name):\n        self.name = name\n    \n    def greet(self):\n        return f'Hello, {self.name}!'\n```",
    "decorators": "Decorators modify function behavior:\n\n```python\ndef my_decorator(func):\n    def wrapper():\n        print('Before function')\n        func()\n        print('After function')\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print('Hello!')\n```",
    "generators": "Generators yield values one at a time:\n\n```python\ndef count_up_to(max):\n    count = 1\n    while count <= max:\n        yield count\n        count += 1\n```",
    "lambda": "Lambda functions are anonymous functions:\n\n```python\nsquare = lambda x: x * x\n```",
    "file handling": "To read a file:\n\n```python\nwith open('file.txt', 'r') as file:\n    content = file.read()\n```",
    "json": "Working with JSON:\n\n```python\nimport json\n\n# Convert to JSON\njson_str = json.dumps(python_dict)\n\n# Parse JSON\npython_dict = json.loads(json_str)\n```",
    "requests": "To make HTTP requests:\n\n```python\nimport requests\n\nresponse = requests.get('https://api.example.com')\ndata = response.json()\n```",
    "sqlite": "Using SQLite with Python:\n\n```python\nimport sqlite3\n\nconn = sqlite3.connect('database.db')\ncursor = conn.cursor()\ncursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')\nconn.commit()\nconn.close()\n```",
    "matplotlib": "Basic plotting:\n\n```python\nimport matplotlib.pyplot as plt\n\nplt.plot([1, 2, 3], [1, 4, 9])\nplt.xlabel('X axis')\nplt.ylabel('Y axis')\nplt.show()\n```",
    "pandas": "Basic Pandas usage:\n\n```python\nimport pandas as pd\n\ndata = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}\ndf = pd.DataFrame(data)\nprint(df)\n```",
    "numpy": "Basic NumPy usage:\n\n```python\nimport numpy as np\n\narr = np.array([1, 2, 3])\nprint(arr * 2)  # [2 4 6]\n```",
}

def get_ai_response(user_message):
    user_message = user_message.lower().strip()
    
    # Check for direct matches
    for key in PYTHON_KNOWLEDGE:
        if key in user_message:
            return PYTHON_KNOWLEDGE[key]
    
    # Default responses
    if "thank" in user_message:
        return "You're welcome! Let me know if you have any other Python questions."
    elif "bye" in user_message or "goodbye" in user_message:
        return "Goodbye! Happy coding with Python!"
    elif "?" in user_message:
        return "That's an interesting Python question! While I'm a simple demo, a real AI would provide a detailed answer. Try asking about specific Python concepts like 'functions', 'loops', or 'classes'."
    else:
        return "I'm focused on Python programming. Ask me about Python syntax, concepts, or best practices!"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = get_ai_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    # Get the local IP address
    from socket import gethostbyname, gethostname
    local_ip = gethostbyname(gethostname())
    
    print(f"Starting Python Master AI server...")
    print(f"Open http://{local_ip}:5000 in your browser")
    print(f"On mobile, connect to the same network and visit http://{local_ip}:5000")
    
    # Run the app with host='0.0.0.0' to make it accessible on the network
app.run(host='0.0.0.0', port=5001, debug=True)