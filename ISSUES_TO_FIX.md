# Issues to Fix While S&S API is Down

**Last Updated:** 2025-11-03
**Status:** S&S API returning 400 errors - waiting for recovery

> **✅ COMPLETED (v2.4.0):** Telemetry cleanup - Removed 488 lines of bloat, enhanced debug tracking

---

## 🔴 CRITICAL (Do First)

### 1. **Add Google Analytics for Real User Tracking**
**Current Issue:** telemetry.html only tracks localStorage (single browser, easily lost)
**Impact:** You have ZERO visibility into actual user behavior
**What's Missing:**
- Total users/sessions
- Real query patterns across all users
- Geographic data
- Device/browser stats
- Retention metrics

**Action:**
1. Get GA4 tracking ID from https://analytics.google.com/
2. Add GA4 script to index.html `<head>`
3. Track events: query_submitted, price_shown, error_occurred, button_clicked
4. Set up custom dashboard in GA4

**Files:** `index.html`
**Effort:** 30 minutes
**Priority:** CRITICAL - You're flying blind without this

---

### 2. **No Monitoring for External API Health**
**Current Issue:** When S&S API goes down, you only find out when users complain
**What's Missing:**
- Automated health checks
- Email/SMS alerts when APIs fail
- Uptime monitoring
- API response time tracking

**Options:**
- **Quick:** UptimeRobot (free, 5-minute checks) monitoring britishmade.ai
- **Better:** Google Cloud Monitoring with alerting
- **Best:** Status page for users (e.g., status.britishmade.ai)

**Effort:** 15-45 minutes depending on option
**Priority:** HIGH - Prevents future surprises

---

### 3. **No Logging for Production Issues**
**Current Issue:** When things break in production, you have no logs
**What's Missing:**
- GCF logs aren't being reviewed
- No error aggregation/alerts
- Can't debug user-reported issues

**Action:**
1. Set up Google Cloud Logging alerts for:
   - 502/500 errors
   - OpenRouter 401 errors
   - Response times >20s
2. Configure email notifications
3. Create log query shortcuts for common issues

**Files:** GCP Console
**Effort:** 30 minutes
**Priority:** HIGH

---

## 🟡 MEDIUM Priority (Important but Not Urgent)

### 4. **Console.log Statements in Production**
**Current:** 22 console.log statements in index.html
**Issue:** Clutters browser console, exposes internal logic
**Action:**
- Wrap in `if (DEBUG_MODE)` flag
- Or remove non-critical logs
- Keep only error logs

**Files:** `index.html` (lines throughout)
**Effort:** 15 minutes
**Priority:** MEDIUM

---

### 5. **No Rate Limiting on Frontend**
**Issue:** User can spam queries → high OpenRouter costs
**What's Missing:**
- Rate limit (e.g., 10 queries per minute)
- Cooldown between queries
- Warning when approaching limits

**Action:**
1. Add client-side rate limiting
2. Show "Please wait X seconds" message
3. Track query frequency in analytics

**Files:** `index.html`
**Effort:** 20 minutes
**Priority:** MEDIUM - Could save on API costs

---

### 6. **No Graceful Degradation When Grok is Slow**
**Issue:** Users wait 10+ seconds with just loading animation
**What's Missing:**
- Progress indicators
- Timeout with fallback
- "This is taking longer than usual..." message

**Action:**
1. Add timeout after 15s
2. Show progressive status: "Thinking..." → "Still working..." → "Almost there..."
3. Fallback to simpler response or suggest trying again

**Files:** `index.html`
**Effort:** 30 minutes
**Priority:** MEDIUM

---

### 7. **Password Protection is Client-Side Only**
**Issue:** telemetry.html password can be bypassed by viewing source
**Security Risk:** Low (no sensitive data), but looks unprofessional
**Action:**
- Move password check to backend
- Or use Basic Auth via GCP
- Or accept it's just obscurity, not security

**Files:** `telemetry.html`
**Effort:** 10 minutes (accept) to 60 minutes (fix properly)
**Priority:** LOW-MEDIUM

---

## 🟢 LOW Priority (Nice to Have)

### 8. **No User Onboarding/Help**
**Issue:** First-time users don't know what queries to try
**Missing:**
- Example queries prominently displayed
- "Try asking..." suggestions
- Help button/tooltip

**Files:** `index.html`
**Effort:** 30 minutes
**Priority:** LOW

---

### 9. **No Mobile Optimization Verification**
**Issue:** Unknown if UI works well on mobile devices
**Action:**
- Test on actual mobile devices
- Check responsive design
- Verify touch targets are large enough

**Files:** `index.html` CSS
**Effort:** 30 minutes
**Priority:** LOW (unless users are mobile-heavy)

---

### 10. **No Automated Testing**
**Issue:** Manual testing required for every change
**Missing:**
- Unit tests for price calculation logic
- Integration tests for API calls
- Frontend tests for UI interactions

**Files:** New test files needed
**Effort:** 4+ hours
**Priority:** LOW (overkill for current scale)

---

### 11. **Hardcoded Contact Phone Number**
**Current:** 01798 343844 in multiple places
**Issue:** If number changes, need to update everywhere
**Action:** Move to config constant

**Files:** `index.html`, `main.py`
**Effort:** 5 minutes
**Priority:** LOW

---

### 12. **No Backup/Recovery Plan**
**Issue:** If GitHub Pages or GCF deleted, no backup
**Missing:**
- Automated backups of JSON data files
- Deployment rollback procedure
- Recovery documentation

**Action:** Document current deployment, create backup script
**Effort:** 30 minutes
**Priority:** LOW

---

## ⚡ QUICK WINS (While Waiting)

### 13. **Add Version Number to Frontend**
**Action:** Show "v2.3.1" in footer
**Files:** `index.html`
**Effort:** 2 minutes

### 14. **Add Link to Telemetry from Main Page**
**Action:** Add hidden link (Ctrl+K or footer) to telemetry
**Files:** `index.html`
**Effort:** 5 minutes

### 15. **Update README with Current Status**
**Action:** Add "Known Issues" section mentioning S&S API dependency
**Files:** `README.md`
**Effort:** 5 minutes

---

## 📝 DOCUMENTATION GAPS

### 16. **No Runbook for Common Issues**
**Missing:**
- What to do when S&S API is down
- How to rotate OpenRouter API key
- How to deploy emergency fixes
- Rollback procedure

**Action:** Create RUNBOOK.md
**Effort:** 30 minutes
**Priority:** MEDIUM

---

### 17. **No Architecture Diagram**
**Missing:** Visual diagram showing:
- Frontend → GCF → S&S API flow
- OpenRouter integration
- Data storage locations

**Action:** Create simple diagram (draw.io or ASCII)
**Files:** New `ARCHITECTURE.md` or update existing
**Effort:** 20 minutes
**Priority:** LOW

---

## 🎯 RECOMMENDED ACTION PLAN

**Today (while S&S is down):**
1. ✅ Add Google Analytics (30 min) - CRITICAL
2. ✅ Set up UptimeRobot monitoring (15 min) - HIGH
3. ✅ Add version to footer (2 min) - QUICK WIN
4. ✅ Create RUNBOOK.md (30 min) - MEDIUM
5. ✅ Update README with known issues (5 min) - QUICK WIN

**This Week:**
6. Set up GCP Logging alerts (30 min)
7. Add rate limiting (20 min)
8. Clean up console.logs (15 min)

**Later:**
- Everything else as time permits

---

**Total Critical Items:** 3
**Total High Priority:** 3
**Total Medium Priority:** 4
**Total Low Priority:** 7

**Estimated Time for Critical+High:** 2-3 hours
