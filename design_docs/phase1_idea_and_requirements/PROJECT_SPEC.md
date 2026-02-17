# ArenaAgent - Project Specification

## Phase 1: Idea and Requirement Analysis

---

## 1. PROBLEM IDENTIFICATION

### Core Problem Statement:
**"Computer science students and self-taught developers need frontier AI models (Claude, GPT-4) for coding assistance but cannot afford $240/year in API costs."**

### Problem Breakdown:

1. **Financial Barrier:**
   - Claude API: $20/month = $240/year
   - GitHub Copilot: $10/month = $120/year
   - Target users earn $0-30k/year (students, self-learners)
   - $240/year = 1-2 weeks of part-time income (prohibitive)

2. **Context Loss:**
   - Free ChatGPT web loses context on page refresh
   - Users manually manage conversation history (error-prone)
   - Multi-turn coding tasks fail without persistent context

3. **Manual Workflow Friction:**
   - Copy code from ChatGPT → Paste to editor → Save → Run → Copy error → Paste back
   - 5+ manual steps per iteration
   - 60% of first attempts fail (missing dependencies, syntax errors)
   - Users give up after 2-3 error iterations

4. **Trust and Privacy:**
   - Cloud tools (Cursor, Copilot) send code to external servers
   - Students work on portfolio projects (want ownership)
   - No control over data retention/deletion

### Why This Problem Matters:

- **Market Size:** 500k+ CS students in US alone, millions globally
- **Access Inequality:** AI coding tools creating digital divide
- **Educational Impact:** Students without tools fall behind peers
- **Economic Impact:** Slower learning = delayed job entry = lost income

---

## 2. TARGET USERS

### Primary User Persona 1: **Computer Science Student**

**Demographics:**
- Age: 18-25
- Income: $0-15k/year (part-time job or internship)
- Education: Undergrad CS, bootcamp, or self-taught
- Location: University campus (unreliable WiFi)

**Characteristics:**
- Codes 10-30 hours/week on assignments and personal projects
- Comfortable with terminal/CLI
- Uses Python, JavaScript, Java
- Has Google account (for LM Arena access)
- Distrusts cloud vendors with academic work

**Pain Points:**
- Cannot afford paid AI tools
- Needs help debugging complex algorithms
- Wants to build portfolio projects faster
- Loses context when ChatGPT session expires

**Success Criteria:**
- Completes projects 30% faster with AI assistance
- Saves $240/year vs. paid alternatives
- Retains full ownership of code and conversation history

---

### Primary User Persona 2: **Self-Taught Developer (Career Switcher)**

**Demographics:**
- Age: 25-35
- Income: $20-40k/year (transitioning from other career)
- Education: Online courses, FreeCodeCamp, YouTube tutorials
- Location: Home (shared internet connection)

**Characteristics:**
- Codes 5-15 hours/week (evenings/weekends)
- Learning multiple languages simultaneously
- Building projects for job applications
- Price-sensitive (saving for career transition)

**Pain Points:**
- Subscription fatigue ($20/month feels expensive)
- Needs AI help but can't justify cost during learning phase
- Unreliable internet (budget ISP)
- Wants privacy (building portfolio, not for current employer to see)

**Success Criteria:**
- Builds 3-5 portfolio projects in 6 months (vs. 1-2 without AI)
- Learns debugging patterns from AI error recovery
- Zero ongoing costs during learning phase

---

### Primary User Persona 3: **Open Source Contributor (Occasional)**

**Demographics:**
- Age: 22-40
- Income: Varies (hobbyist contributor)
- Education: Varies
- Location: Anywhere

**Characteristics:**
- Contributes to OSS 2-5 hours/week
- Works across unfamiliar codebases
- Needs help understanding legacy code
- Doesn't want to pay for occasional use

**Pain Points:**
- Paid tools not worth it for 2-5 hours/week usage
- Each OSS project uses different language/framework
- Need quick understanding of unfamiliar code
- Want to contribute more but time-constrained

**Success Criteria:**
- Doubles number of PRs contributed per month
- Understands unfamiliar codebases 5x faster
- Only pays time, not money

---

### Secondary Users (Not Primary Focus):

- **Researchers/Academics:** Need model comparison, budget constraints
- **Developers in Low-Income Countries:** $20/month = significant income portion
- **Bootcamp Instructors:** Want free tools for students

---

## 3. FEATURE DEFINITION

### Core Features (Must-Have - Phase 1 MVP):

#### Feature 1: **Persistent Browser Session Management**
- **Description:** Maintain logged-in state to LM Arena across sessions
- **User Value:** Never re-login after initial setup (one-time 30-second login)
- **Technical:** Playwright persistent browser profile with cookie storage
- **Acceptance Criteria:**
  - User logs in once during `arenaagent init`
  - Subsequent runs use saved session automatically
  - Session expiry detected and prompts re-authentication
  - Works across system restarts

#### Feature 2: **Local Conversation Persistence**
- **Description:** Save all prompts and responses locally in JSON format
- **User Value:** Context never lost, can resume days/weeks later
- **Technical:** JSON file storage in `~/.arenaagent/sessions/[session_id]/`
- **Acceptance Criteria:**
  - Every message saved immediately after sending
  - Terminal crash/restart → context resumes seamlessly
  - User can view history: `arenaagent history`
  - User owns data (local storage, no cloud)

#### Feature 3: **Autonomous Code Execution**
- **Description:** Automatically execute code generated by model
- **User Value:** Zero copy-paste, immediate feedback on "does it work?"
- **Technical:** Subprocess execution with output capture
- **Acceptance Criteria:**
  - Detect code blocks in model response
  - Prompt user for approval before execution
  - Support Python, Bash, Node.js
  - Capture stdout, stderr, exit codes
  - Display results in real-time

#### Feature 4: **Automatic Error Recovery Loop**
- **Description:** Send execution errors back to model for automatic fixing
- **User Value:** 60% of failures auto-fixed without manual intervention
- **Technical:** Error detection → feedback to model → retry execution (max 3 times)
- **Acceptance Criteria:**
  - Non-zero exit code triggers recovery
  - Error traceback sent to model with context
  - Model generates fix
  - Auto-retry with user approval
  - After 3 failures, stop and show full log

#### Feature 5: **Safe File Operations with Auto-Backup**
- **Description:** Never overwrite files without backup
- **User Value:** Confidence to let AI modify files (can always undo)
- **Technical:** Timestamped backups before modifications, atomic writes
- **Acceptance Criteria:**
  - Before overwrite: Create `.backup.TIMESTAMP` file
  - Show diff before applying changes
  - Rollback command: `arenaagent rollback <file>`
  - Atomic writes (temp file + rename)
  - Auto-cleanup old backups (30+ days)

---

### Phase 2 Features (Post-MVP Enhancements):

- **Multi-Model Selection:** Choose between Claude, GPT-4, Gemini
- **Advanced Error Parsing:** Handle 50+ error types intelligently
- **Workspace Sandboxing:** Strict mode to prevent escaping workspace
- **Session Export:** Export conversation as Markdown for archival
- **Network Queue Mode:** Queue prompts when offline, send when online

---

### Explicitly Excluded Features (Scope Control):

❌ **GUI Interface** - Target users are CLI-native  
❌ **Cloud Sync** - Privacy-first, local-only design  
❌ **Team Collaboration** - Individual developer tool  
❌ **Built-in Linting** - Use existing tools (black, pylint)  
❌ **Auto-Deployment** - Safety concern (AI shouldn't have prod credentials)  
❌ **Custom Model Fine-Tuning** - LM Arena provides models  

---

## 4. TECHNOLOGY STACK SELECTION

### Backend/Core:

**Python 3.11+**
- **Why:** Target users already know Python, excellent library ecosystem
- **Pros:** Cross-platform, easy to distribute, great for subprocess management
- **Cons:** Slower than compiled languages (acceptable for our use case)
- **Alternatives Considered:** Node.js (worse subprocess handling), Go (harder to extend)

**Playwright (Browser Automation)**
- **Why:** Best-in-class for persistent browser profiles, handles modern SPAs
- **Pros:** Microsoft-backed, active development, excellent Python bindings
- **Cons:** Large download (Chromium ~300MB)
- **Alternatives Considered:** Selenium (poor persistent profile support), Puppeteer (Node.js only)

---

### CLI Framework:

**Click**
- **Why:** Industry standard, used by Flask/pip/AWS CLI
- **Pros:** Clean decorator syntax, excellent documentation, mature
- **Cons:** None significant
- **Alternatives Considered:** argparse (too low-level), Typer (newer, less battle-tested)

**Rich (Terminal Formatting)**
- **Why:** Beautiful output, progress bars, syntax highlighting
- **Pros:** Best terminal rendering library, maintained by Textualize
- **Cons:** Adds dependency size (~1MB)
- **Alternatives Considered:** Colorama (basic), Blessed (overkill)

---

### Data Storage:

**JSON Files (Local File System)**
- **Why:** Simple, transparent, human-readable, zero setup
- **Pros:** User can inspect/edit, portable, Git-friendly
- **Cons:** Not optimized for complex queries (don't need them)
- **Alternatives Considered:** SQLite (overkill), Pickle (not readable), YAML (slower)

---

### Execution Environment:

**Subprocess Module (Python Standard Library)**
- **Why:** Built-in, reliable, cross-platform
- **Pros:** No dependencies, well-documented, handles all shell types
- **Cons:** Security requires careful handling (we mitigate with validation)
- **Alternatives Considered:** os.system (less control), Docker (too heavy)

---

### Browser:

**Chromium (via Playwright)**
- **Why:** Most compatible with LM Arena, consistent cross-platform
- **Pros:** Same rendering as Chrome, well-supported by Playwright
- **Cons:** Large download size
- **Alternatives Considered:** Firefox (less reliable automation), WebKit (limited)

---

### Development Tools:

**Development:**
- pytest (testing)
- black (code formatting)
- mypy (type checking)
- pylint (linting)

**Distribution:**
- PyPI (package distribution)
- setuptools (packaging)
- pip (installation)

**CI/CD:**
- GitHub Actions (automated testing)
- Pre-commit hooks (code quality)

---

### Infrastructure:

**Hosting/Deployment:**
- None (100% local application)
- No cloud services
- No servers
- No APIs to maintain

**Authentication:**
- OS-level file permissions
- Browser cookies (managed by Chromium)
- No custom auth system

---

## 5. SYSTEM REQUIREMENTS

### Minimum Requirements:

**Hardware:**
- RAM: 4GB (8GB recommended)
- Storage: 1GB free (for Chromium + session data)
- CPU: Any modern processor (2+ cores recommended)

**Software:**
- Python 3.11 or higher
- Internet connection (for LM Arena access)
- Google account (for LM Arena login)

**Operating Systems:**
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora, Arch)

---

### Dependencies:

**Python Packages:**
```
playwright>=1.40.0
click>=8.1.0
rich>=13.0.0
requests>=2.31.0
```

**System Dependencies:**
- Chromium browser (installed via `playwright install chromium`)

---

## 6. SUCCESS METRICS

### Phase 1 (MVP) Success Criteria:

**Technical:**
- ✅ Browser automation works on Windows/Mac/Linux
- ✅ Session persists across restarts (100% reliability)
- ✅ Code execution supports Python + Bash
- ✅ Error recovery succeeds >60% of the time
- ✅ File backups never fail

**User Experience:**
- ✅ Setup time: <5 minutes
- ✅ First successful code generation: <2 minutes after setup
- ✅ Error recovery: Automatic in <30 seconds
- ✅ Context resumption: Instant (session load <1s)

**Reliability:**
- ✅ Uptime tied to LM Arena (>95% expected)
- ✅ Graceful degradation when LM Arena down
- ✅ Zero data loss on crashes
- ✅ Recovery from network failures

---

### Long-Term Success Metrics (6 months):

**Adoption:**
- 1,000+ active users (students, developers)
- 10+ GitHub stars/week
- Community contributions (bug reports, PRs)

**Usage:**
- Average 50+ prompts per user per month
- 70%+ user retention (return after 30 days)
- 5+ projects completed per user

**Impact:**
- $240,000+ saved collectively (1,000 users × $240/year)
- 10+ testimonials from students/developers
- Featured in CS course recommendations

---

## 7. RISKS AND MITIGATIONS

### Technical Risks:

**Risk 1: LM Arena Changes DOM Structure**
- **Impact:** Browser automation breaks
- **Probability:** High (monthly changes)
- **Mitigation:** Flexible selectors with fallbacks, community updates
- **Contingency:** Manual mode (open browser, user operates, we save context)

**Risk 2: LM Arena Blocks Automation**
- **Impact:** Tool becomes unusable
- **Probability:** Medium (ToS violation risk)
- **Mitigation:** Rate limiting (5s delay), user-agent identification, ethical use
- **Contingency:** Adapt to other free inference platforms (Hugging Face, Perplexity)

**Risk 3: Browser Profile Corruption**
- **Impact:** User must re-login
- **Probability:** Low (Playwright is stable)
- **Mitigation:** Profile validation on startup, auto-recovery
- **Contingency:** Re-init takes 30 seconds (acceptable)

---

### User Risks:

**Risk 1: Low Adoption (Users Don't Know It Exists)**
- **Impact:** No user base
- **Probability:** Medium (marketing challenge)
- **Mitigation:** GitHub README, Reddit posts (r/learnprogramming), YouTube demo
- **Contingency:** Even 100 users = impact (democratization goal)

**Risk 2: Users Don't Trust Local Tool**
- **Impact:** Hesitant to adopt
- **Probability:** Low (open source builds trust)
- **Mitigation:** Transparent code, security audit, clear privacy policy
- **Contingency:** Video demos showing data ownership

**Risk 3: Setup Too Complex**
- **Impact:** High abandonment rate
- **Probability:** Medium (Playwright install can be tricky)
- **Mitigation:** One-command install, detailed troubleshooting guide
- **Contingency:** Docker image for consistent environment

---

### Legal/Ethical Risks:

**Risk 1: LM Arena Terms of Service Violation**
- **Impact:** Legal action, tool shutdown
- **Probability:** Low (LM Arena is research platform, no explicit ToS against automation)
- **Mitigation:** Respectful use (rate limiting, contribute ratings back)
- **Contingency:** Adapt to other platforms

**Risk 2: Users Generate Destructive Code**
- **Impact:** Data loss, system damage
- **Probability:** Medium (AI hallucinations happen)
- **Mitigation:** Safety validator (blocklist), user approval required
- **Contingency:** Clear warnings, backups prevent data loss

---

## 8. TIMELINE ESTIMATES

### Phase 1: MVP Development (4-6 weeks)

**Week 1-2: Core Infrastructure**
- Playwright integration
- Browser profile management
- Session storage (JSON)

**Week 3-4: Execution Engine**
- Code parsing from responses
- Subprocess execution
- Error capture and retry logic

**Week 5-6: File Management + CLI**
- File operations with backups
- Click CLI interface
- Rich formatting for output

**Deliverable:** Working MVP with 5 core features

---

### Phase 2: Testing & Polish (2-3 weeks)

**Week 7-8: Testing**
- Unit tests (pytest)
- Integration tests
- Cross-platform testing (Windows/Mac/Linux)

**Week 9: Polish**
- Error messages improvement
- Edge case handling
- Performance optimization

**Deliverable:** Production-ready v1.0

---

### Phase 3: Documentation & Launch (1-2 weeks)

**Week 10-11: Documentation**
- README with setup instructions
- Usage examples
- Troubleshooting guide
- Architecture documentation

**Week 12: Launch**
- PyPI package publication
- GitHub repository public
- Reddit/HN announcement
- Video demo on YouTube

**Deliverable:** Public release v1.0.0

---

## 9. DELIVERABLES CHECKLIST

### Phase 1 Deliverables:

- ✅ **PROJECT_SPEC.md** (this document)
- ✅ **FEATURE_LIST.md** (detailed feature specifications)
- ✅ **TECH_STACK.md** (technology justifications)
- ⬜ **ARCHITECTURE_DIAGRAM.md** (system architecture visual)
- ⬜ **USER_PERSONAS.md** (detailed user profiles)

---

## 10. NEXT STEPS (Phase 2: Design)

1. **Architecture Design:**
   - Component diagram (CLI → Agent → Browser → LM Arena)
   - Data flow diagram (User → Prompt → Execution → Feedback)
   - File system structure

2. **API Specification:**
   - Internal module interfaces
   - Configuration file schema
   - Session data schema

3. **UI/UX Design:**
   - CLI command structure
   - Output formatting standards
   - Error message templates

4. **Database Schema:**
   - Session JSON structure
   - File index format
   - Execution log format

---

## APPROVAL CHECKLIST

**Before proceeding to Phase 2, verify:**

- ✅ Problem is clearly defined and validated
- ✅ Target users are specific and reachable
- ✅ Features are minimal but sufficient (5 core features)
- ✅ Technology stack is justified and practical
- ✅ Success metrics are measurable
- ✅ Risks are identified with mitigations
- ✅ Timeline is realistic

**Phase 1 Status:** ✅ **COMPLETE - Ready for Phase 2**

---

*Document Version: 1.0*  
*Last Updated: 2026-02-17*  
*Status: Approved for Phase 2*