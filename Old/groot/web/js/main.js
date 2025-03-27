// Initialize Feather icons
document.addEventListener('DOMContentLoaded', function() {
    feather.replace();

    // Chat functionality
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    if (chatInput && sendButton && chatMessages) {
        // Send message when button is clicked
        sendButton.addEventListener('click', sendMessage);

        // Send message when Enter key is pressed
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Quick action buttons
    const scanDefaultBtn = document.getElementById('scan-default');
    const checkPodsBtn = document.getElementById('check-pods');

    if (scanDefaultBtn) {
        scanDefaultBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addChatMessage('Scan the default namespace for issues', 'user');
            fetchChatResponse('Scan the default namespace for issues');
        });
    }

    if (checkPodsBtn) {
        checkPodsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addChatMessage('Check all pods in the cluster', 'user');
            fetchChatResponse('Check all pods in the cluster');
        });
    }

    // Function to send a message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message to chat
            addChatMessage(message, 'user');

            // Clear input
            chatInput.value = '';

            // Get response from server
            fetchChatResponse(message);
        }
    }

    // Function to add a message to the chat
    function addChatMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const paragraph = document.createElement('p');
        paragraph.textContent = message;

        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to fetch response from the server
    function fetchChatResponse(message) {
        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const paragraph = document.createElement('p');
        paragraph.textContent = 'Thinking...';

        contentDiv.appendChild(paragraph);
        loadingDiv.appendChild(contentDiv);
        chatMessages.appendChild(loadingDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Fetch response from server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                // Remove loading indicator
                chatMessages.removeChild(loadingDiv);

                // Add response to chat
                if (data.error) {
                    addChatMessage(`Error: ${data.error}`, 'assistant');
                } else {
                    addChatMessage(data.response, 'assistant');
                }
            })
            .catch(error => {
                // Remove loading indicator
                chatMessages.removeChild(loadingDiv);

                // Add error message
                addChatMessage(`Error: ${error.message}`, 'assistant');
            });
    }
});