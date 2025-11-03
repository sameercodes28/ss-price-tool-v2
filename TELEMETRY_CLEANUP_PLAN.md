# Telemetry Code Cleanup Plan

## Current Status
**Lines of Analytics Code:** ~600 lines
**LocalStorage Usage:** ~50KB+ (bloated with unused Maps/Arrays)
**Complexity:** HIGH (10+ tracking systems)

## Problems
1. **90% of code is never used** - conversionFunnel, userJourneys, crossSell, etc.
2. **Slows down page load** - Loading/saving massive objects
3. **Confusing for debugging** - Too many data structures
4. **LocalStorage bloat** - Unnecessary data persistence

## What's Actually Used

### BY DEBUG.HTML:
```javascript
// ONLY these 3 things:
Analytics.events[]          // Event log for history
Analytics.p1Errors          // Error tracking
Analytics.sessionId         // Session ID
```

### BY INDEX.HTML:
```javascript
Analytics.track('query', {...})        // Track queries
Analytics.track('llm_response', {...}) // Track responses
Analytics.track('p1_error', {...})     // Track errors
Analytics.trackFeedback(...)           // Thumbs up/down (optional)
```

## Proposed Simplified Version

```javascript
const Analytics = {
    events: [],
    p1Errors: { noPriceErrors: [], totalCount: 0, lastOccurred: null },
    sessionId: null,
    maxEvents: 500, // Keep last 500 events only

    init() {
        this.sessionId = localStorage.getItem('sessionId') || this.generateSessionId();
        localStorage.setItem('sessionId', this.sessionId);
        this.loadData();

        // Auto-save every 30s
        setInterval(() => this.saveData(), 30000);
    },

    track(eventName, data = {}) {
        const event = {
            name: eventName,
            timestamp: Date.now(),
            data: { ...data, sessionId: this.sessionId }
        };

        this.events.push(event);

        // Keep only last 500 events
        if (this.events.length > this.maxEvents) {
            this.events = this.events.slice(-this.maxEvents);
        }

        // Special handling for P1 errors
        if (eventName === 'p1_error') {
            this.p1Errors.noPriceErrors.push({
                timestamp: Date.now(),
                query: data.query,
                error: data.error,
                sessionId: this.sessionId
            });
            this.p1Errors.totalCount++;
            this.p1Errors.lastOccurred = Date.now();
        }

        this.saveData();
    },

    trackFeedback(messageId, feedback, responseContent) {
        this.track('feedback', { messageId, feedback, responseContent });
    },

    saveData() {
        try {
            const data = {
                events: this.events,
                p1Errors: this.p1Errors,
                timestamp: Date.now()
            };
            localStorage.setItem('analyticsComprehensive', JSON.stringify(data));
            localStorage.setItem('analyticsEvents', JSON.stringify(this.events));
        } catch (e) {
            console.error('[Analytics] Save failed:', e);
        }
    },

    loadData() {
        try {
            const saved = localStorage.getItem('analyticsComprehensive');
            if (saved) {
                const data = JSON.parse(saved);
                this.events = data.events || [];
                this.p1Errors = data.p1Errors || { noPriceErrors: [], totalCount: 0, lastOccurred: null };
            } else {
                // Legacy support
                const legacyEvents = localStorage.getItem('analyticsEvents');
                if (legacyEvents) {
                    this.events = JSON.parse(legacyEvents);
                }
            }
        } catch (e) {
            console.error('[Analytics] Load failed:', e);
        }
    },

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
};
```

## Changes

### REMOVE (10 unused systems):
- ❌ conversionFunnel (sessions, stages)
- ❌ productPopularity
- ❌ fabricPopularity
- ❌ priceSensitivity
- ❌ queryPatterns
- ❌ userJourneys
- ❌ crossSell
- ❌ peakUsage
- ❌ nluScoring
- ❌ healthChecks
- ❌ performanceMetrics

### KEEP (3 essentials):
- ✅ events[] - Basic event log
- ✅ p1Errors - Error tracking
- ✅ sessionId - Session identification

### REMOVE (unused methods):
- ❌ trackQuery() - use track('query') instead
- ❌ trackResponse() - use track('llm_response') instead
- ❌ trackError() - use track('p1_error') instead
- ❌ trackOpportunityClick() - unused
- ❌ checkAPIHealth() - moved to debug.html
- ❌ monitorPerformance() - unused
- ❌ calculateAvgResponseTime() - moved to debug.html
- ❌ flush() - auto-save instead
- ❌ getAnalytics() - use events directly

### UPDATE (simplify calls):
```javascript
// OLD:
Analytics.trackQuery(query, 'typed');
Analytics.trackResponse(content, responseTime);
Analytics.trackError('api_error', { error: err });

// NEW:
Analytics.track('query', { query, source: 'typed' });
Analytics.track('llm_response', { response: content, responseTime });
Analytics.track('p1_error', { error: err });
```

## Benefits

1. **~500 lines removed** (600 → ~100 lines)
2. **Faster page load** (less to parse/load)
3. **Simpler localStorage** (50KB+ → ~10KB)
4. **Easier debugging** (3 data structures instead of 12)
5. **Still works with debug.html** (uses same events/p1Errors)

## Risks

### LOW RISK:
- Code is self-contained in Analytics object
- No other code depends on removed features
- Debug.html only uses events/p1Errors (keeping these)

### TESTING NEEDED:
1. Page loads without errors
2. Queries still tracked
3. Errors still logged
4. Debug.html still works
5. Thumbs up/down still works

## Approval Needed

**Ready to proceed?** I'll:
1. Create backup: `index-before-telemetry-cleanup.html`
2. Replace Analytics object with simplified version
3. Update all Analytics calls to use new format
4. Test locally
5. Commit with detailed changelog

**Estimated time:** 20 minutes
**Risk level:** LOW (easily reversible)
