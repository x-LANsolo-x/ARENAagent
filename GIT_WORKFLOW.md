# ArenaAgent - Git Workflow Strategy

## 🌳 Branching Strategy

This project follows a **strict three-tier branching model** to ensure code quality and stability:

```
master (production)
   ↑
   │ (merge only after full QA)
   │
testing (QA/staging)
   ↑
   │ (merge after feature completion)
   │
develop (integration)
   ↑
   │ (merge feature branches here)
   │
feature/* (development)
```

---

## 📋 Branch Descriptions

### 1. **master** (Production Branch)
- **Purpose:** Production-ready code only
- **Protection:** HIGHEST - No direct commits allowed
- **Updates:** Only from `testing` branch after full QA approval
- **Stability:** 110% tested and verified
- **Who can merge:** Project lead only
- **When to merge:** Major releases, critical hotfixes

**Rules:**
- ❌ NO direct commits
- ❌ NO direct pushes
- ❌ NO feature branches merge directly
- ✅ Only merge from `testing` via Pull Request
- ✅ Requires all tests passing
- ✅ Requires code review approval
- ✅ Must be tagged with version number

---

### 2. **testing** (QA/Staging Branch)
- **Purpose:** Quality assurance and final testing
- **Protection:** HIGH - Limited direct commits
- **Updates:** From `develop` branch after feature integration
- **Stability:** Fully functional, undergoing final verification
- **Who can merge:** Team leads, QA approved
- **When to merge:** After successful integration testing

**Rules:**
- ❌ NO direct commits (except hotfixes)
- ❌ NO feature branches merge directly
- ✅ Merge from `develop` via Pull Request
- ✅ Run full test suite before accepting
- ✅ Manual QA testing required
- ✅ Performance testing required
- ✅ Integration tests must pass

---

### 3. **develop** (Integration Branch)
- **Purpose:** Integration of completed features
- **Protection:** MEDIUM - Feature integration point
- **Updates:** From `feature/*` branches
- **Stability:** Should be stable, but may have minor issues
- **Who can merge:** Developers with approval
- **When to merge:** After feature completion and unit tests pass

**Rules:**
- ❌ NO direct commits for features
- ✅ Merge feature branches via Pull Request
- ✅ Unit tests must pass
- ✅ Code review required
- ✅ Continuous integration checks must pass
- ⚠️ May contain experimental features

---

### 4. **feature/*** (Feature Branches)
- **Purpose:** Development of new features
- **Protection:** LOW - Active development
- **Naming:** `feature/descriptive-name` (e.g., `feature/config-system`)
- **Lifetime:** Created from `develop`, deleted after merge
- **Who commits:** Individual developers
- **When to create:** For each new feature or module

**Rules:**
- ✅ Branch from `develop`
- ✅ Commit frequently with clear messages
- ✅ Write tests alongside code
- ✅ Keep branch focused on single feature
- ✅ Merge back to `develop` when complete
- ✅ Delete after successful merge

---

## 🔄 Workflow Process

### Step 1: Create Feature Branch

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Step 2: Develop Feature

```bash
# Make changes, commit frequently
git add .
git commit -m "feat: description of changes"

# Push to remote
git push -u origin feature/your-feature-name
```

### Step 3: Merge to Develop

```bash
# Update from develop
git checkout develop
git pull origin develop

# Merge feature (via Pull Request on GitHub)
# After PR approval and tests pass:
git checkout develop
git merge feature/your-feature-name
git push origin develop

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### Step 4: Merge to Testing

```bash
# After multiple features integrated in develop
git checkout testing
git pull origin testing

# Merge develop to testing (via Pull Request)
# After integration tests pass:
git checkout testing
git merge develop
git push origin testing

# Run full QA test suite
# Manual testing
# Performance testing
```

### Step 5: Merge to Master (Production)

```bash
# After complete QA approval in testing
git checkout master
git pull origin master

# Merge testing to master (via Pull Request)
# After final approval:
git checkout master
git merge testing
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin master
git push origin v1.0.0
```

---

## 📊 Current Branch Status

| Branch | Status | Purpose | Protection |
|--------|--------|---------|------------|
| **master** | 🔒 Protected | Production releases | HIGHEST |
| **testing** | 🔐 Protected | QA and staging | HIGH |
| **develop** | 🔓 Active | Feature integration | MEDIUM |
| **feature/config-and-session-management** | 🚀 Active | Config & Session development | LOW |
| **feature/core-data-models** | ✅ Merged | Data models (completed) | LOW |

---

## 🚦 Merge Requirements

### Feature → Develop
- ✅ All unit tests pass
- ✅ Code review approved
- ✅ No merge conflicts
- ✅ Feature complete and documented
- ✅ Test coverage ≥ 80%

### Develop → Testing
- ✅ All integration tests pass
- ✅ Multiple features tested together
- ✅ No critical bugs
- ✅ Code review approved
- ✅ Documentation updated

### Testing → Master
- ✅ Full QA test suite passes
- ✅ Manual testing complete
- ✅ Performance benchmarks met
- ✅ Security review complete
- ✅ All known bugs resolved
- ✅ Release notes prepared
- ✅ Version tagged

---

## 🏷️ Commit Message Convention

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes (formatting)
- `chore:` Maintenance tasks
- `perf:` Performance improvements

**Examples:**
```bash
feat(config): implement ConfigManager with atomic writes
fix(session): resolve session persistence race condition
docs(readme): update installation instructions
test(config): add validation test cases
```

---

## 🛡️ Branch Protection Rules (GitHub Settings)

### Master Branch Protection

**Settings → Branches → Add rule → Branch name pattern: `master`**

Required settings:
- ✅ Require pull request reviews before merging (2 approvals)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - ✅ CI/CD pipeline
  - ✅ All tests passing
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ Restrict who can push to matching branches
- ✅ Require linear history

### Testing Branch Protection

**Settings → Branches → Add rule → Branch name pattern: `testing`**

Required settings:
- ✅ Require pull request reviews before merging (1 approval)
- ✅ Require status checks to pass before merging
  - ✅ Integration tests
  - ✅ QA approval
- ✅ Require branches to be up to date before merging

### Develop Branch Protection

**Settings → Branches → Add rule → Branch name pattern: `develop`**

Required settings:
- ✅ Require pull request reviews before merging (1 approval)
- ✅ Require status checks to pass before merging
  - ✅ Unit tests
  - ✅ Code coverage ≥ 80%

---

## 🔥 Hotfix Process

For critical production bugs:

```bash
# Create hotfix from master
git checkout master
git checkout -b hotfix/critical-bug-name

# Fix the issue
git add .
git commit -m "fix: critical bug description"

# Merge to master (emergency PR)
git checkout master
git merge hotfix/critical-bug-name
git tag -a v1.0.1 -m "Hotfix: critical bug"
git push origin master
git push origin v1.0.1

# Also merge to develop and testing
git checkout develop
git merge hotfix/critical-bug-name
git push origin develop

git checkout testing
git merge hotfix/critical-bug-name
git push origin testing

# Delete hotfix branch
git branch -d hotfix/critical-bug-name
```

---

## 📈 Example Workflow Timeline

```
Week 1:
  feature/config-system → develop (PR #1)
  feature/session-mgmt → develop (PR #2)

Week 2:
  feature/file-ops → develop (PR #3)
  develop → testing (PR #4) [Integration testing]

Week 3:
  QA testing in testing branch
  Bug fixes merged to develop, then to testing

Week 4:
  testing → master (PR #5) [Release v0.2.0]
  Tag v0.2.0 created
```

---

## 🎯 Current Feature Development

**Active Feature:** `feature/config-and-session-management`

**Next Steps:**
1. Complete code review
2. Ensure all tests pass (155+ unit tests)
3. Create PR to merge into `develop`
4. After approval, merge to `develop`
5. Continue with next feature branches
6. When ready, merge `develop` → `testing`
7. After QA, merge `testing` → `master`

---

## 📝 Pull Request Template

When creating PRs, use this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality
- [ ] All tests passing locally
- [ ] Dependent changes merged

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Closes #issue_number
```

---

## 🔍 Verification Commands

Before merging, run these checks:

```bash
# Run all tests
pytest tests/ -v --cov=arenaagent

# Check code style
black --check arenaagent/
isort --check arenaagent/
pylint arenaagent/

# Type checking
mypy arenaagent/

# Run pre-commit hooks
pre-commit run --all-files
```

---

## 📞 Questions?

- **Feature branch naming:** Use `feature/descriptive-name`
- **Bug fix branches:** Use `bugfix/issue-description`
- **Hotfix branches:** Use `hotfix/critical-issue`
- **When in doubt:** Create a PR and ask for review

---

**Remember:** Master branch is sacred! It should only contain production-ready, 110% tested code.

*Last updated: February 17, 2026*
