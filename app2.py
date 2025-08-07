from flask import Flask, render_template, request, jsonify
import openai  # or your preferred AI provider
import json
import os

app = Flask(__name__)

# Configure your API key (use environment variables in production)
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    try:
        # Call OpenAI API (or your AI model)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_message = response.choices[0].message
        return jsonify({
            'role': 'assistant',
            'content': ai_message['content']
        })
        
    except Exception as e:
        return jsonify({
            'role': 'assistant',
            'content': f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)