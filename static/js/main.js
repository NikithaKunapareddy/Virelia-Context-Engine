// Main JavaScript for Agentic RAG Application


class ChatApp {
    constructor() {
        this.isConnected = true; // Always true for REST
        this.isTyping = false;
        this.isSending = false; // Flag to prevent duplicate sends
        this.allMessages = []; // Store all messages for filtering
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateConnectionStatus('connected');
        // this.trackMouseForBubbles();

        // Add filter input event listener
        const filterInput = document.getElementById('chatFilterInput');
        if (filterInput) {
            filterInput.addEventListener('input', () => {
                this.renderFilteredMessages();
            });
        }

        // Start bubble generation immediately
        console.log('🫧 Starting bubble generation from ChatApp init...');
        setTimeout(() => {
            this.testBubbleGeneration();
        }, 1000);

        setTimeout(() => {
            this.startBubbleGeneration();
        }, 3000);
    }

    // Removed connectSocket and all Socket.IO logic. Only REST will be used.

 setupEventListeners() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    if (chatForm) {
        chatForm.onsubmit = (e) => {
            e.preventDefault();
            console.log('📝 Form submit triggered');
            this.sendMessage();
        };
    }

    if (messageInput) {
        messageInput.onkeypress = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('📝 Enter key pressed');
                this.sendMessage();
            }
        };
        messageInput.oninput = () => {
            const isEmpty = messageInput.value.trim() === '';
            if (sendButton) {
                sendButton.disabled = isEmpty || !this.isConnected;
            }
        };
    }

    if (sendButton) {
        sendButton.onclick = (e) => {
            e.preventDefault();
            console.log('📝 Send button clicked');
            this.sendMessage();
        };
    }
}

    sendMessage() {
        // Prevent duplicate sends
        if (this.isSending) {
            console.log('⚠️ Message already being sent, ignoring duplicate request');
            return false;
        }

        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) {
            console.log('⚠️ Cannot send message:', { message: !!message });
            return false;
        }

        // Set sending flag immediately
        this.isSending = true;
        console.log('📤 Sending message:', message);

        // Add user message to chat with particle effect
        this.addMessageWithEffect('user', message);
        
        // Clear input immediately
        messageInput.value = '';
        
        // Update send button state
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.disabled = true;
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }

        // Always use REST API
        this.sendMessageREST(message);
        return true;
    }

    async sendMessageREST(message) {
        try {
            this.showTypingIndicator();
            // Use explicit port for API calls
            const apiPort = 5003;
            const apiUrl = `${window.location.protocol}//${window.location.hostname}:${apiPort}/api/chat`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            // Debug: log the raw response object
            console.log('🔍 Raw fetch response:', response);

            const data = await response.json();

            // Debug: log the parsed data
            console.log('🔍 Parsed response data:', data);

            this.hideTypingIndicator();

            if (response.ok) {
                this.addMessage('assistant', data.response);
                this.addActivityLog('Received AI response via REST');
            } else {
                this.showError(data.error || 'Failed to send message');
            }

            this.resetSendingState();
        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Network error occurred');
            console.error('Error:', error);
            this.resetSendingState();
        }
    }

    addMessage(role, content) {
        // Store all messages for filtering
        this.allMessages.push({ role, content, timestamp: Date.now() });
        this.renderFilteredMessages();
    }

    // Render messages based on filter
    renderFilteredMessages() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        // Get filter value
        const filterInput = document.getElementById('chatFilterInput');
        const filterValue = filterInput ? filterInput.value.trim().toLowerCase() : '';

        // Clear chat
        chatMessages.innerHTML = '';

        // Filter and render
        this.allMessages.forEach(msg => {
            if (!filterValue || msg.content.toLowerCase().includes(filterValue)) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.role}-message`;
                messageDiv.setAttribute('data-timestamp', msg.timestamp);

                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                if (msg.role === 'user') {
                    messageContent.innerHTML = `<strong>👤 You:</strong> ${this.escapeHtml(msg.content)}`;
                } else {
                    messageContent.innerHTML = `<strong>🤖 Assistant:</strong> ${this.formatAssistantMessage(msg.content)}`;
                }

                const timestamp = document.createElement('div');
                timestamp.className = 'message-timestamp';
                timestamp.textContent = new Date(msg.timestamp).toLocaleTimeString();

                messageDiv.appendChild(messageContent);
                messageDiv.appendChild(timestamp);
                chatMessages.appendChild(messageDiv);
            }
        });

        // Scroll to bottom with smooth animation
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }

    formatAssistantMessage(content) {
        // Basic markdown-like formatting
        let formatted = this.escapeHtml(content);
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Code blocks
        formatted = formatted.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
        
        // Inline code
        formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
            this.isTyping = true;
        }
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
            this.isTyping = false;
        }
        
        // Re-enable send button
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        if (messageInput && sendButton) {
            sendButton.disabled = messageInput.value.trim() === '' || !this.isConnected;
        }
    }

    updateConnectionStatus(status) {
        const indicator = document.getElementById('status-indicator');
        if (!indicator) return;

        switch (status) {
            case 'connected':
                indicator.className = 'badge bg-success';
                indicator.textContent = 'Connected';
                break;
            case 'connecting':
                indicator.className = 'badge bg-warning';
                indicator.textContent = 'Connecting...';
                break;
            case 'disconnected':
                indicator.className = 'badge bg-danger';
                indicator.textContent = 'Disconnected';
                break;
        }

        // Update send button state
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        if (sendButton && messageInput) {
            sendButton.disabled = messageInput.value.trim() === '' || !this.isConnected;
        }
    }

    showError(message) {
        // Create error toast or alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 70px; right: 20px; z-index: 1050; max-width: 400px;';
        
        alertDiv.innerHTML = `
            <strong>Error:</strong> ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    addActivityLog(message) {
        const activityLog = document.getElementById('activityLog');
        if (!activityLog) return;

        const logItem = document.createElement('div');
        logItem.className = 'activity-item';
        
        const timestamp = new Date().toLocaleTimeString();
        logItem.innerHTML = `
            <div>${this.escapeHtml(message)}</div>
            <div class="activity-timestamp">${timestamp}</div>
        `;
        
        activityLog.insertBefore(logItem, activityLog.firstChild);
        
        // Limit log items
        const items = activityLog.querySelectorAll('.activity-item');
        if (items.length > 50) {
            items[items.length - 1].remove();
        }
    }

    // Particle effects for message sending
    createParticleEffect(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const effectContainer = document.createElement('div');
        effectContainer.className = 'message-sent-effect';
        effectContainer.style.left = centerX + 'px';
        effectContainer.style.top = centerY + 'px';
        document.body.appendChild(effectContainer);
        
        // Create multiple particles
        for (let i = 0; i < 8; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random direction
            const angle = (i * 45) * Math.PI / 180;
            const distance = 30 + Math.random() * 20;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            
            particle.style.transform = `translate(${x}px, ${y}px)`;
            effectContainer.appendChild(particle);
        }
        
        // Remove effect after animation
        setTimeout(() => {
            document.body.removeChild(effectContainer);
        }, 1000);
    }

    // Enhanced message adding with effects
    addMessageWithEffect(role, content) {
        this.addMessage(role, content);
        // Removed call to this.activateBubbleBackground(); as it does not exist
        if (role === 'user') {
            const sendButton = document.getElementById('sendButton');
            this.createParticleEffect(sendButton);
            // Create a burst of bubbles when user sends a message
            this.createBubbleBurst();
        } else if (role === 'assistant') {
            // Create gentle bubbles when assistant responds
            this.createGentleBubbles();
        }
        // Create message-specific bubble effects
        this.createMessageBubbles(role);
    }

    // Create a burst of bubbles for user messages
    createBubbleBurst() {
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                this.createRandomBubble();
            }, i * 100);
        }
    }

    // Create gentle bubbles for assistant messages
    createGentleBubbles() {
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                this.createRandomBubble();
            }, i * 300);
        }
    }

    // Enhanced bubble animation for background
    createRandomBubble() {
        const bubbleContainer = document.querySelector('.bubble-background');
        if (!bubbleContainer) {
            console.log('Bubble container not found!');
            return;
        }
        
        console.log('Creating new bubble...');
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble dynamic-bubble';
        
        // Random properties with more variety
        const size = 25 + Math.random() * 80; // More visible size range
        const left = Math.random() * 100;
        const duration = 8 + Math.random() * 10; // Slower for visibility
        const delay = Math.random() * 2;
        
        // Random bubble types based on our CSS styles
        const bubbleTypes = ['soap', 'water', 'glass', 'crystal', 'rainbow'];
        const bubbleType = bubbleTypes[Math.floor(Math.random() * bubbleTypes.length)];
        
        bubble.style.width = size + 'px';
        bubble.style.height = size + 'px';
        bubble.style.left = left + '%';
        bubble.style.animationDuration = duration + 's';
        bubble.style.animationDelay = delay + 's';
        bubble.style.opacity = '0.8'; // More visible
        
        // Apply different bubble styles
        this.applyBubbleStyle(bubble, bubbleType, size);
        
        bubbleContainer.appendChild(bubble);
        console.log('Bubble added to container');
        
        // Remove bubble after animation
        setTimeout(() => {
            if (bubbleContainer.contains(bubble)) {
                bubbleContainer.removeChild(bubble);
                console.log('Bubble removed after animation');
            }
        }, (duration + delay) * 1000);
    }

    // Apply different visual styles to bubbles
    applyBubbleStyle(bubble, type, size) {
        const opacity = 0.6 + Math.random() * 0.3;
        bubble.style.opacity = opacity;
        
        switch(type) {
            case 'soap':
                bubble.style.background = `
                    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.4) 20%, transparent 40%),
                    radial-gradient(circle at 70% 80%, rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 255, 0.3) 0%, transparent 50%),
                    linear-gradient(135deg, rgba(52, 152, 219, 0.2) 0%, rgba(155, 89, 182, 0.15) 50%, rgba(241, 196, 15, 0.1) 100%)
                `;
                bubble.style.border = '2px solid rgba(255, 255, 255, 0.2)';
                bubble.style.boxShadow = 'inset 0 0 20px rgba(255, 255, 255, 0.2), 0 0 30px rgba(52, 152, 219, 0.3)';
                break;
            case 'water':
                bubble.style.background = `
                    radial-gradient(circle at 25% 15%, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.6) 15%, transparent 35%),
                    radial-gradient(circle at 75% 85%, rgba(46, 204, 113, 0.3) 0%, transparent 50%),
                    linear-gradient(135deg, rgba(46, 204, 113, 0.25) 0%, rgba(26, 188, 156, 0.2) 100%)
                `;
                bubble.style.border = '1px solid rgba(255, 255, 255, 0.3)';
                bubble.style.boxShadow = 'inset 0 0 15px rgba(255, 255, 255, 0.3), 0 0 25px rgba(46, 204, 113, 0.4)';
                break;
            case 'glass':
                bubble.style.background = `
                    radial-gradient(circle at 20% 10%, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0.3) 25%, transparent 50%),
                    radial-gradient(circle at 80% 90%, rgba(230, 126, 34, 0.2) 0%, transparent 40%),
                    linear-gradient(135deg, rgba(230, 126, 34, 0.15) 0%, rgba(231, 76, 60, 0.1) 100%)
                `;
                bubble.style.border = '1px solid rgba(255, 255, 255, 0.4)';
                bubble.style.boxShadow = 'inset 0 0 25px rgba(255, 255, 255, 0.2), 0 0 35px rgba(230, 126, 34, 0.3)';
                break;
            case 'crystal':
                bubble.style.background = `
                    radial-gradient(circle at 35% 25%, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0.5) 18%, transparent 38%),
                    radial-gradient(circle at 65% 75%, rgba(142, 68, 173, 0.3) 0%, transparent 45%),
                    linear-gradient(135deg, rgba(142, 68, 173, 0.2) 0%, rgba(155, 89, 182, 0.15) 50%, rgba(52, 73, 94, 0.1) 100%)
                `;
                bubble.style.border = '2px solid rgba(255, 255, 255, 0.25)';
                bubble.style.boxShadow = 'inset 0 0 22px rgba(255, 255, 255, 0.25), 0 0 35px rgba(142, 68, 173, 0.35)';
                break;
            case 'rainbow':
                const hue = Math.floor(Math.random() * 360);
                bubble.style.background = `
                    radial-gradient(circle at 28% 18%, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.6) 16%, transparent 36%),
                    linear-gradient(135deg, hsl(${hue}, 70%, 60%) 0%, hsl(${(hue + 60) % 360}, 70%, 60%) 50%, hsl(${(hue + 120) % 360}, 70%, 60%) 100%)
                `;
                bubble.style.border = '1px solid rgba(255, 255, 255, 0.3)';
                bubble.style.boxShadow = `0 0 20px hsla(${hue}, 70%, 60%, 0.4)`;
                break;
        }
        
        // Add size-based effects
        if (size > 70) {
            bubble.style.filter = 'drop-shadow(0 0 15px rgba(255, 255, 255, 0.4))';
        } else if (size < 30) {
            bubble.style.filter = 'drop-shadow(0 0 5px rgba(255, 255, 255, 0.2))';
        }
        
        // Random animation variations
        const animations = ['floatUp', 'floatUp, pulse', 'floatUp, wobble', 'floatUp, shimmer'];
        const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
        bubble.style.animation = `${randomAnimation} ${bubble.style.animationDuration} infinite linear`;
    }

    // Initialize enhanced bubble generation
    startBubbleGeneration() {
        console.log('Starting bubble generation...');
        
        // Create bursts of bubbles periodically
        setInterval(() => {
            console.log('Creating bubble burst...');
            // Create 1-3 bubbles in a burst
            const burstSize = 1 + Math.floor(Math.random() * 3);
            for (let i = 0; i < burstSize; i++) {
                setTimeout(() => {
                    this.createRandomBubble();
                }, i * 200); // Stagger bubble creation
            }
        }, 3000 + Math.random() * 4000);
        
        // Also create single bubbles more frequently
        setInterval(() => {
            console.log('Creating single bubble...');
            this.createRandomBubble();
        }, 2000 + Math.random() * 3000);
    }

    // Test bubble generation - start immediately
    testBubbleGeneration() {
        console.log('🧪 Test: Setting up bubble generation...');
        
        // Create a test bubble every 2 seconds
        setInterval(() => {
            console.log('🧪 Test: Creating test bubble...');
            this.createTestBubble();
        }, 2000);
        
        // Also create one immediately
        console.log('🧪 Test: Creating immediate test bubble...');
        this.createTestBubble();
    }

    // Create a simple test bubble
    createTestBubble() {
        const bubbleContainer = document.querySelector('.bubble-background');
        if (!bubbleContainer) {
            console.error('🧪 Test: Bubble container not found!');
            return;
        }
        
        console.log('🧪 Test: Creating test bubble in container...');
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble test-bubble';
        
        // Make it VERY visible
        bubble.style.width = '80px';
        bubble.style.height = '80px';
        bubble.style.left = (Math.random() * 80) + 10 + '%';
        bubble.style.background = 'radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(255, 0, 0, 0.9) 30%, rgba(255, 0, 0, 0.6) 60%, transparent 100%)';
        bubble.style.border = '4px solid rgba(255, 255, 255, 1)';
        bubble.style.boxShadow = '0 0 40px rgba(255, 0, 0, 1), inset 0 0 20px rgba(255, 255, 255, 0.5)';
        bubble.style.opacity = '1';
        bubble.style.animation = 'floatUp 8s infinite linear';
        bubble.style.zIndex = '100'; // Very high z-index
        bubble.style.position = 'absolute';
        bubble.style.borderRadius = '50%';
        
        // Add highlight effects
        bubble.innerHTML = '<div style="position: absolute; top: 15%; left: 20%; width: 25%; height: 25%; background: rgba(255, 255, 255, 0.8); border-radius: 50%;"></div>';
        
        bubbleContainer.appendChild(bubble);
        console.log('🧪 Test: Test bubble added to container. Total children:', bubbleContainer.children.length);
        
        // Log bubble properties
        console.log('🧪 Test: Bubble properties:', {
            width: bubble.style.width,
            height: bubble.style.height,
            left: bubble.style.left,
            zIndex: bubble.style.zIndex,
            animation: bubble.style.animation
        });
        
        // Remove after animation
        setTimeout(() => {
            if (bubbleContainer.contains(bubble)) {
                bubbleContainer.removeChild(bubble);
                console.log('🧪 Test: Test bubble removed');
            }
        }, 8000);
    }

    resetSendingState() {
        this.isSending = false;
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
        console.log('✅ Reset sending state');
    }
}

// Admin functionality
class AdminApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add knowledge form
        const addKnowledgeForm = document.getElementById('addKnowledgeForm');
        if (addKnowledgeForm) {
            addKnowledgeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addKnowledge();
            });
        }

        // Search form
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.searchKnowledge();
            });
        }
    }

    async addKnowledge() {
        const docId = document.getElementById('docId').value.trim();
        const content = document.getElementById('docContent').value.trim();
        const topic = document.getElementById('docTopic').value.trim();

        if (!content) {
            this.showAlert('Content is required', 'danger');
            return;
        }

        try {
            const response = await fetch('/api/knowledge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: docId || undefined,
                    content: content,
                    metadata: { topic: topic || 'general' }
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert(`Document added successfully (ID: ${data.doc_id})`, 'success');
                document.getElementById('addKnowledgeForm').reset();
                this.refreshStatus();
            } else {
                this.showAlert(data.error || 'Failed to add document', 'danger');
            }
        } catch (error) {
            this.showAlert('Network error occurred', 'danger');
            console.error('Error:', error);
        }
    }

    async searchKnowledge() {
        const query = document.getElementById('searchQuery').value.trim();
        const topK = parseInt(document.getElementById('topK').value) || 5;

        if (!query) {
            this.showAlert('Search query is required', 'danger');
            return;
        }

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: topK
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.displaySearchResults(data.results);
            } else {
                this.showAlert(data.error || 'Search failed', 'danger');
            }
        } catch (error) {
            this.showAlert('Network error occurred', 'danger');
            console.error('Error:', error);
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        if (!container) return;

        if (!results || results.length === 0) {
            container.innerHTML = '<div class="text-muted">No results found</div>';
            return;
        }

        const html = results.map((result, index) => `
            <div class="search-result">
                <div class="d-flex justify-content-between">
                    <strong>#${index + 1}</strong>
                    <span class="search-result-score">Score: ${result.similarity_score.toFixed(3)}</span>
                </div>
                <div class="mt-2">${this.escapeHtml(result.content.substring(0, 200))}${result.content.length > 200 ? '...' : ''}</div>
                <div class="search-result-metadata mt-2">
                    ID: ${result.id} | Topic: ${result.metadata.topic || 'N/A'}
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            this.updateSystemStatus(data);
            this.updateStatistics(data);
        } catch (error) {
            console.error('Error refreshing status:', error);
            this.updateSystemStatus({ status: 'error', error: error.message });
        }
    }

    updateSystemStatus(data) {
        const container = document.getElementById('systemStatus');
        if (!container) return;

        const components = data.components || {};
        const status = data.status || 'unknown';
        
        const html = `
            <div class="row">
                <div class="col-12 mb-3">
                    <h6>Overall Status: <span class="badge bg-${status === 'healthy' ? 'success' : 'danger'}">${status}</span></h6>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <h6>Components:</h6>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-${components.vector_db ? 'check text-success' : 'times text-danger'}"></i> Vector Database</li>
                        <li><i class="fas fa-${components.memory_manager ? 'check text-success' : 'times text-danger'}"></i> Memory Manager</li>
                        <li><i class="fas fa-${components.mcp_server ? 'check text-success' : 'times text-danger'}"></i> MCP Server</li>
                        <li><i class="fas fa-${components.mcp_client ? 'check text-success' : 'times text-danger'}"></i> MCP Client</li>
                        <li><i class="fas fa-${components.agent ? 'check text-success' : 'times text-danger'}"></i> Agent</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Last Updated:</h6>
                    <p class="text-muted">${new Date().toLocaleString()}</p>
                    ${data.error ? `<div class="alert alert-danger">${data.error}</div>` : ''}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    updateStatistics(data) {
        // This would be updated with real statistics from the backend
        document.getElementById('knowledgeCount').textContent = '6'; // Default sample count
        document.getElementById('activeUsers').textContent = '1';
        document.getElementById('totalMessages').textContent = '0';
        document.getElementById('memoryUsage').textContent = 'Normal';
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 70px; right: 20px; z-index: 1050; max-width: 400px;';
        
        alertDiv.innerHTML = `
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Debug function to check bubble status
function debugBubbles() {
    const bubbleContainer = document.querySelector('.bubble-background');
    if (bubbleContainer) {
        const allBubbles = bubbleContainer.querySelectorAll('.bubble');
        const dynamicBubbles = bubbleContainer.querySelectorAll('.dynamic-bubble');
        const testBubbles = bubbleContainer.querySelectorAll('.test-bubble');
        
        console.log('🔍 Bubble Debug Report:');
        console.log('  Total bubbles:', allBubbles.length);
        console.log('  Dynamic bubbles:', dynamicBubbles.length);
        console.log('  Test bubbles:', testBubbles.length);
        console.log('  Container dimensions:', bubbleContainer.offsetWidth, 'x', bubbleContainer.offsetHeight);
        console.log('  Container z-index:', window.getComputedStyle(bubbleContainer).zIndex);
        console.log('  Container visibility:', window.getComputedStyle(bubbleContainer).visibility);
        console.log('  Container display:', window.getComputedStyle(bubbleContainer).display);
        
        // Check individual bubbles
        allBubbles.forEach((bubble, index) => {
            const styles = window.getComputedStyle(bubble);
            console.log(`  Bubble ${index + 1}:`, {
                width: styles.width,
                height: styles.height,
                opacity: styles.opacity,
                zIndex: styles.zIndex,
                visibility: styles.visibility,
                display: styles.display,
                animation: styles.animation
            });
        });
    } else {
        console.error('❌ Bubble container not found for debugging!');
    }
}

// Export debug function to global scope
window.debugBubbles = debugBubbles;

// Global functions
function initializeChat() {
    console.log('🔧 Initializing chat app...');
    
    // Prevent multiple instances
    if (window.chatApp) {
        console.log('⚠️ ChatApp already exists, skipping initialization');
        return;
    }
    
    window.chatApp = new ChatApp();
    
    // Check if bubble container exists
    const bubbleContainer = document.querySelector('.bubble-background');
    if (bubbleContainer) {
        console.log('✅ Bubble container found!');
        console.log('📊 Bubble container dimensions:', bubbleContainer.offsetWidth, 'x', bubbleContainer.offsetHeight);
        console.log('📊 Static bubbles in container:', bubbleContainer.children.length);
        
        // Start immediate bubble generation for testing
        console.log('🚀 Creating immediate bubbles for visual confirmation...');
        
        // Debug initial state
        setTimeout(() => {
            debugBubbles();
        }, 500);
        
        // Create multiple test bubbles immediately
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                console.log(`🧪 Creating test bubble ${i + 1}...`);
                window.chatApp.createTestBubble();
            }, i * 200);
        }
        
        // Debug after creating test bubbles
        setTimeout(() => {
            console.log('🔍 After creating test bubbles:');
            debugBubbles();
        }, 2000);
        
        // Set up continuous bubble generation
        setTimeout(() => {
            console.log('🌟 Starting continuous bubble generation...');
            window.chatApp.startBubbleGeneration();
        }, 3000);
        
    } else {
        console.error('❌ Bubble container NOT found!');
        // Try to find any element with 'bubble' in the class name
        const allElements = document.querySelectorAll('*');
        let foundBubbleElements = [];
        allElements.forEach(el => {
            if (el.className && el.className.includes('bubble')) {
                foundBubbleElements.push(el);
            }
        });
        console.log('🔍 Elements with "bubble" in class name:', foundBubbleElements);
    }
}

function initializeAdmin() {
    window.adminApp = new AdminApp();
}

function refreshStatus() {
    if (window.adminApp) {
        window.adminApp.refreshStatus();
    }
}

function clearActivityLog() {
    const activityLog = document.getElementById('activityLog');
    if (activityLog) {
        activityLog.innerHTML = '<div class="text-muted">Activity log cleared</div>';
    }
}

// Initialize based on page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing application...');
    
    // Check which page we're on and initialize accordingly
    if (document.querySelector('.chat-container')) {
        console.log('📱 Chat page detected, initializing chat...');
        initializeChat();
    } else if (document.querySelector('.admin-container')) {
        console.log('⚙️ Admin page detected, initializing admin...');
        initializeAdmin();
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add loading states to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                submitBtn.disabled = true;
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    });
});
