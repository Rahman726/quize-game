document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-button');
    const fileInput = document.getElementById('file-input');
    const fileNameSpan = document.getElementById('file-name');
    const modelSelect = document.getElementById('model-select');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeStylesheet = document.getElementById('dark-mode');
    
    // State
    let conversationHistory = [];
    let currentConversationId = null;
    let fileText = '';
    let isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Initialize
    if (isDarkMode) {
        enableDarkMode();
    }
    
    // Initialize Marked (Markdown parser)
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(lang, code).value;
            }
            return hljs.highlightAuto(code).value;
        }
    });
    
    // Dark mode toggle
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
    
    function toggleDarkMode() {
        isDarkMode = !isDarkMode;
        if (isDarkMode) {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
        localStorage.setItem('darkMode', isDarkMode);
        
        // Send to server to persist user preference
        fetch('/toggle-dark-mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dark_mode: isDarkMode })
        });
    }
    
    function enableDarkMode() {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
        darkModeStylesheet.disabled = false;
        if (darkModeToggle) darkModeToggle.textContent = '☀️';
    }
    
    function disableDarkMode() {
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');
        darkModeStylesheet.disabled = true;
        if (darkModeToggle) darkModeToggle.textContent = '🌙';
    }
    
    // File upload handling
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileNameSpan.textContent = file.name;
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage('assistant', `File upload error: ${data.error}`);
                } else {
                    fileText = data.text;
                    addMessage('assistant', `File "${data.filename}" uploaded successfully. I can now reference its content.`);
                }
            })
            .catch(error => {
                addMessage('assistant', `File upload failed: ${error.message}`);
            });
        }
    });
    
    // Send message function
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message && !fileText) return;
        
        // Add user message to chat
        if (message) {
            addMessage('user', message);
            conversationHistory.push({ role: 'user', content: message });
        }
        
        // Clear input
        userInput.value = '';
        fileInput.value = '';
        fileNameSpan.textContent = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message assistant';
        typingIndicator.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            // Get selected model
            const model = modelSelect.value;
            
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: conversationHistory,
                    model: model,
                    file_text: fileText
                })
            });
            
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const data = await response.json();
            addMessage('assistant', data.content);
            conversationHistory.push({ role: 'assistant', content: data.content });
            
            // Clear file text after first use
            fileText = '';
            
        } catch (error) {
            chatMessages.removeChild(typingIndicator);
            addMessage('assistant', `Error: ${error.message}`);
            console.error('Error:', error);
        }
    }
    
    // Add message to chat
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        // Parse markdown and highlight code
        messageDiv.innerHTML = marked.parse(content);
        
        // Highlight any code blocks
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Clear conversation
    function clearConversation() {
        chatMessages.innerHTML = '';
        conversationHistory = [];
        currentConversationId = null;
        fileText = '';
        fileNameSpan.textContent = '';
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    clearButton.addEventListener('click', clearConversation);
    
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Load previous conversations if any
    loadConversations();
    
    // Initial greeting
    setTimeout(() => {
        addMessage('assistant', 'Hello! I\'m your AI assistant. How can I help you today?');
    }, 500);
    
    // Load previous conversations (simplified)
    function loadConversations() {
        // In a real app, you'd fetch this from your backend
        console.log('Loading previous conversations...');
    }
});