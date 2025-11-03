        function formatLLMResponse(content) {
            let html = '';

            // Parse response into sections
            const lines = content.split('\n');
            let currentSection = '';
            let inOpportunities = false;
            let suggestions = [];  // Collect follow-up suggestions

            for (let line of lines) {
                line = line.trim();
                if (!line) continue;

                // Section headers with icons
                if (line.startsWith('### 💰')) {
                    html += '<div class="price-section">';
                    html += '<div class="section-header price-header">💰 Price</div>';
                    continue;
                } else if (line.startsWith('### ✨')) {
                    // Close previous section (price or breakdown)
                    if (currentSection === 'price') html += '</div>';
                    if (currentSection === 'breakdown') html += '</ul></div></div>';
                    html += '<div class="features-section">';
                    html += '<div class="section-header features-header">✨ Key Features</div>';
                    currentSection = 'features';
                    continue;
                } else if (line.startsWith('### 🎯')) {
                    // Close previous section (features or price)
                    if (currentSection === 'features') html += '</div>';
                    if (currentSection === 'price') html += '</div>';
                    if (currentSection === 'breakdown') html += '</ul></div></div>';
                    html += '<div class="opportunities-section">';
                    html += '<div class="section-header opportunities-header">🎯 Opportunities to Enhance</div>';
                    currentSection = 'opportunities';
                    inOpportunities = true;
                    continue;
                } else if (line.startsWith('### 💬')) {
                    // Close previous section (opportunities)
                    console.log('[SUGGESTIONS] Section detected');
                    if (currentSection === 'opportunities') html += '</div>';
                    currentSection = 'suggestions';
                    continue;  // Don't render header yet, will render with chips
                }

                // Total price (for multiple items) - CHECK THIS FIRST
                if (line.startsWith('**TOTAL:') || line.startsWith('TOTAL:')) {
                    // Pattern: **TOTAL: £amount** or TOTAL: £amount
                    const totalMatch = line.match(/\*\*?TOTAL:\s*£([\d,]+)\*\*?/);
                    const savingsMatch = line.match(/\(Save £([\d,]+)!\)/);
                    if (totalMatch) {
                        const totalAmount = totalMatch[1];
                        html += `<div class="total-price">TOTAL: £${totalAmount}`;
                        if (savingsMatch) {
                            html += ` <span style="font-size: 1.25rem; color: #dc2626;">(Save £${savingsMatch[1]}!)</span>`;
                        }
                        html += '</div>';
                        html += '<div class="price-breakdown"><ul>';
                        currentSection = 'breakdown';
                        continue;
                    }
                }

                // Price breakdown items (bullet list after TOTAL)
                if (currentSection === 'breakdown' && (line.startsWith('-') || line.startsWith('•'))) {
                    const text = line.substring(1).trim();

                    // Extract item name (everything before the colon)
                    const colonIndex = text.indexOf(':');
                    if (colonIndex !== -1) {
                        const itemName = text.substring(0, colonIndex).trim();
                        const priceInfo = text.substring(colonIndex + 1).trim();

                        // Extract new price - find last **£amount** pattern
                        const newPriceMatch = priceInfo.match(/\*\*£([\d,]+)\*\*/g);
                        if (newPriceMatch && newPriceMatch.length > 0) {
                            // Get the last match (the new price, not old price)
                            const lastMatch = newPriceMatch[newPriceMatch.length - 1];
                            const priceValue = lastMatch.match(/£([\d,]+)/)[1];

                            html += `<li><span>${escapeHtml(itemName)}</span><strong>£${priceValue}</strong></li>`;
                        } else {
                            // No price found, just show the item
                            html += `<li>${escapeHtml(itemName)}</li>`;
                        }
                    } else {
                        // No colon, just show the whole line
                        html += `<li>${escapeHtml(text)}</li>`;
                    }
                    continue;
                }

                // Close breakdown when we hit a non-bullet line
                if (currentSection === 'breakdown' && !line.startsWith('-') && !line.startsWith('•')) {
                    html += '</ul></div>';
                    currentSection = 'price';
                }

                // Price line with old and new prices (for single items, NOT breakdown items)
                if (line.includes('~~£') && line.includes('**£') && !line.startsWith('-') && !line.startsWith('•') && currentSection !== 'breakdown') {
                    const oldPriceMatch = line.match(/~~£([\d,]+)~~/);
                    const newPriceMatch = line.match(/\*\*£([\d,]+)\*\*/);
                    const savingsMatch = line.match(/\(Save £([\d,]+)!\)/);

                    if (oldPriceMatch && newPriceMatch) {
                        const oldPrice = oldPriceMatch[1];
                        const newPrice = newPriceMatch[1];
                        const savings = savingsMatch ? savingsMatch[1] : null;

                        html += '<div class="price-display">';
                        html += `<div class="old-price">Was £${oldPrice}</div>`;
                        html += `<div class="new-price">£${newPrice}</div>`;
                        if (savings) {
                            html += `<div class="savings-badge">Save £${savings}!</div>`;
                        }
                        html += '</div>';
                        currentSection = 'price';
                        continue;
                    }
                }

                // Product name (bold text not in price display)
                if (line.startsWith('**') && line.endsWith('**')) {
                    const productName = line.replace(/\*\*/g, '');
                    if (currentSection === 'price' || !currentSection) {
                        // Parse product name and fabric (format: "Product in Fabric")
                        const parts = productName.split(' in ');
                        if (parts.length === 2) {
                            html += `<div class="product-name">${escapeHtml(parts[0])} <span class="fabric-detail">in ${escapeHtml(parts[1])}</span></div>`;
                        } else {
                            html += `<div class="product-name">${escapeHtml(productName)}</div>`;
                        }
                    }
                    continue;
                }

                // Bullet points
                if (line.startsWith('•') || line.startsWith('-')) {
                    // Check if this is a suggestion bullet
                    if (currentSection === 'suggestions') {
                        const suggestion = line.substring(1).trim();
                        console.log('[SUGGESTION] Found:', suggestion);
                        suggestions.push(suggestion);
                        continue;
                    }

                    // Regular feature bullet
                    if (!html.includes('<ul class="feature-list">')) {
                        html += '<ul class="feature-list">';
                    }
                    const text = line.substring(1).trim();
                    html += `<li>${escapeHtml(text)}</li>`;
                    continue;
                }

                // Opportunities (blockquote items)
                if (line.startsWith('>')) {
                    const text = line.substring(1).trim();
                    // Parse bold and pricing from opportunity
                    const formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    html += `<div class="opportunity-item">${formatted}</div>`;
                    continue;
                }

                // Regular text
                if (line && !line.startsWith('#')) {
                    html += `<p class="response-text">${escapeHtml(line)}</p>`;
                }
            }

            // Close any open sections
            if (currentSection && currentSection !== 'suggestions') html += '</div>';

            // Render suggestions if we have any
            if (suggestions.length > 0) {
                console.log('[SUGGESTIONS] Rendering', suggestions.length, 'suggestions');
                html += '<div class="suggestions-section">';
                html += '<div class="section-header suggestions-header">💬 What next?</div>';
                html += '<div class="suggestions-chips">';
                suggestions.forEach(suggestion => {
                    html += `<button class="suggestion-chip" onclick="handleSuggestionClick('${escapeHtml(suggestion).replace(/'/g, "\\'")}')">${escapeHtml(suggestion)}</button>`;
                });
                html += '</div>';
                html += '</div>';
            }

            // Close any open lists
            if (html.includes('<ul class="feature-list">') && !html.includes('</ul>')) {
                html += '</ul>';
            }

            return html || `<p class="response-text">${escapeHtml(content)}</p>`;
        }

        /**
         * Handle suggestion chip click
         * Auto-fills input and sends message
         */
