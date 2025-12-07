const chatContainer = document.getElementById('chatContainer');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

let isProcessing = false;

// Check health status on load
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Database connected';
            queryInput.disabled = false;
            submitBtn.disabled = false;
        } else {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Database disconnected';
        }
    } catch (error) {
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Connection error';
        console.error('Health check failed:', error);
    }
}

// Add message to chat
function addMessage(content, isUser = false, sqlQuery = null, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'message-user' : 'message-bot'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isError) {
        contentDiv.innerHTML = `
            <div>${content}</div>
            <div class="error-message">${isError}</div>
        `;
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(contentDiv);

    // Add SQL query if present
    if (sqlQuery && !isError) {
        const sqlDiv = document.createElement('div');
        sqlDiv.innerHTML = `
            <span class="sql-label">SQL Query:</span>
            <div class="sql-query">${sqlQuery}</div>
        `;
        contentDiv.appendChild(sqlDiv);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add loading indicator
function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message message-bot';
    loadingDiv.id = 'loadingMessage';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    contentDiv.innerHTML = `
        <div class="loading">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;

    loadingDiv.appendChild(contentDiv);
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove loading indicator
function removeLoading() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Handle form submission
queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const query = queryInput.value.trim();
    if (!query || isProcessing) return;

    // Remove welcome message if present
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Add user message
    addMessage(query, true);

    // Clear input
    queryInput.value = '';

    // Set processing state
    isProcessing = true;
    queryInput.disabled = true;
    submitBtn.disabled = true;

    // Add loading indicator
    addLoading();

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        // Remove loading indicator
        removeLoading();

        if (data.success) {
            addMessage(data.response, false, data.sql_query);
        } else {
            addMessage(
                'Sorry, I encountered an error processing your query.',
                false,
                null,
                data.error
            );
        }
    } catch (error) {
        removeLoading();
        addMessage(
            'Sorry, I encountered an error processing your query.',
            false,
            null,
            error.message
        );
        console.error('Query error:', error);
    } finally {
        // Reset processing state
        isProcessing = false;
        queryInput.disabled = false;
        submitBtn.disabled = false;
        queryInput.focus();
    }
});

// Check health on load
checkHealth();

// Auto-focus input
queryInput.focus();
