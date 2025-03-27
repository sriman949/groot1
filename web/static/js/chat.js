document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const namespaceSelector = document.getElementById('namespace-selector');

    let socket = null;

    // Initialize WebSocket connection
    function initWebSocket() {
        // Close existing socket if any
        if (socket) {
            socket.close();
        }

        // Create new WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

        // WebSocket event handlers
        socket.onopen = function(e) {
            console.log('WebSocket connection established');
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);

            if (data.type === 'response') {
                displayAssistantMessage(data.response);
            } else if (data.type === 'error') {
                displayErrorMessage(data.error);
            }
        };

        socket.onclose = function(event) {
            console.log('WebSocket connection closed');
            // Try to reconnect after a delay
            setTimeout(initWebSocket, 3000);
        };

        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    }

    // Load namespaces
    function loadNamespaces() {
        fetch('/api/namespaces')
            .then(response => response.json())
            .then(data => {
                if (data.namespaces) {
                    namespaceSelector.innerHTML = '';
                    data.namespaces.forEach(namespace => {
                        const option = document.createElement('option');
                        option.value = namespace;
                        option.textContent = namespace;
                        namespaceSelector.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading namespaces:', error);
            });
    }

    // Display user message
    function displayUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Display assistant message
    function displayAssistantMessage(response) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Parse markdown in the response
        if (response.ai_response) {
            contentDiv.innerHTML = marked.parse(response.ai_response);

            // Apply syntax highlighting to code blocks
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        } else {
            contentDiv.textContent = 'Sorry, I could not process your request.';
        }

        // Add suggested commands if any
        if (response.commands && response.commands.length > 0) {
            const commandsTitle = document.createElement('p');
            commandsTitle.innerHTML = '<strong>Suggested Commands:</strong>';
            contentDiv.appendChild(commandsTitle);

            const commandsList = document.createElement('ul');
            response.commands.forEach(cmd => {
                const cmdItem = document.createElement('li');
                cmdItem.innerHTML = `<code>${cmd.command}</code> - ${cmd.description}`;
                commandsList.appendChild(cmdItem);
            });
            contentDiv.appendChild(commandsList);
        }

        // Add follow-up questions if any
        if (response.follow_up_questions && response.follow_up_questions.length > 0) {
            const questionsTitle = document.createElement('p');
            questionsTitle.innerHTML = '<strong>Follow-up Questions:</strong>';
            contentDiv.appendChild(questionsTitle);

            const questionsList = document.createElement('ul');
            response.follow_up_questions.forEach(question => {
                const questionItem = document.createElement('li');
                questionItem.textContent = question;
                questionsList.appendChild(questionItem);
            });
            contentDiv.appendChild(questionsList);
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Display error message
    function displayErrorMessage(error) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.style.backgroundColor = '#ffebee';
        contentDiv.textContent = `Error: ${error}`;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Send message
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        displayUserMessage(message);

        // Clear input
        userInput.value = '';

        // Send message to server
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'query',
                query: message,
                namespace: namespaceSelector.value
            }));
        } else {
            displayErrorMessage('WebSocket connection is not open. Trying to reconnect...');
            initWebSocket();
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Initialize
    initWebSocket();
    loadNamespaces();
});