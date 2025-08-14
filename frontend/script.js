// script.js (v2.0 - Upgraded with Sources, Markdown, and Chips)

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const suggestionChips = document.querySelectorAll('.chip');

const API_URL = 'http://127.0.0.1:8010/ask';

// --- ✨ NEW: Handle suggestion chip clicks ---
suggestionChips.forEach(chip => {
    chip.addEventListener('click', () => {
        const query = chip.textContent;
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit'));
    });
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    addMessage(userMessage, 'user');
    userInput.value = '';

    showTypingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userMessage }),
        });

        hideTypingIndicator();

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        const botMessage = data.answer;
        const sources = data.sources;

        addMessage(botMessage, 'bot', sources);

    } catch (error) {
        console.error('Error fetching API:', error);
        hideTypingIndicator();
        addMessage('ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์ กรุณาลองใหม่อีกครั้ง', 'bot');
    }
});

function addMessage(message, sender, sources = []) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('chat-message', sender);

    const messageElement = document.createElement('div');
    messageElement.classList.add('message-content');

    if (sender === 'user') {
        messageElement.textContent = message;
    } else {
        messageElement.innerHTML = marked.parse(message);
    }
    
    messageContainer.appendChild(messageElement);

    if (sources && sources.length > 0) {
        const sourceListContainer = document.createElement('div');
        sourceListContainer.classList.add('source-list');
        
        const title = document.createElement('strong');
        title.textContent = 'แหล่งข่าวอ้างอิง:';
        sourceListContainer.appendChild(title);

        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.classList.add('source-item');
            
            const link = document.createElement('a');
            link.href = source.url;
            link.textContent = source.title;
            link.target = '_blank'; // เปิดในแท็บใหม่
            
            sourceItem.appendChild(link);
            sourceListContainer.appendChild(sourceItem);
        });
        
        messageContainer.appendChild(sourceListContainer);
    }
    
    chatBox.appendChild(messageContainer);
    scrollToBottom();
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.classList.add('chat-message', 'bot');
    
    const content = document.createElement('div');
    content.classList.add('message-content');
    content.innerHTML = '<span></span><span></span><span></span>'; // For CSS animation
    
    indicator.appendChild(content);
    chatBox.appendChild(indicator);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}