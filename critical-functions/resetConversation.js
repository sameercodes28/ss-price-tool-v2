        function resetConversation() {
            conversationHistory = [];
            sessionId = generateSessionId();
            console.log('[Frontend] Conversation reset. New session:', sessionId);
        }
