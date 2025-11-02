        function handleSuggestionClick(suggestionText) {
            console.log('[CLICK] Suggestion clicked:', suggestionText);
            // Fill input with suggestion text
            messageInput.value = suggestionText;
            // Send immediately
            sendMessage();
        }

        /**
         * Send message to backend
