        function generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7);
        }

        /**
         * Reset conversation (new session)
         * Why: Lets user start fresh without page refresh
         */
