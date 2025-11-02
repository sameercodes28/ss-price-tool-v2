        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /**
         * Format LLM response into beautiful, professional HTML
         * Parses response and creates structured, visual sections
