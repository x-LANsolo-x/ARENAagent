# GitHub Branch Protection Setup Guide

## 🛡️ How to Configure Branch Protection Rules

Follow these steps to protect your branches on GitHub.

---

## Step-by-Step Instructions

### 1. Access Branch Protection Settings

1. Go to your repository: https://github.com/x-LANsolo-x/ARENAagent
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar
4. Click **Add rule** button

---

## 🔒 Protection Rule for `master` Branch

### Branch name pattern
```
master
```

### Settings to Enable

#### Protect matching branches
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **2**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if you add a CODEOWNERS file)

#### Status checks
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Status checks (once CI/CD is set up):
    - ✅ `ci-tests` (GitHub Actions workflow)
    - ✅ `pytest-unit-tests`
    - ✅ `code-quality-checks`

#### Additional settings
- ✅ **Require conversation resolution before merging**
- ✅ **Require signed commits** (optional, recommended)
- ✅ **Require linear history**
- ✅ **Include administrators** (even admins must follow the rules)
- ✅ **Restrict who can push to matching branches**
  - Add only: Project lead/owner
- ✅ **Allow force pushes** → ❌ Disabled
- ✅ **Allow deletions** → ❌ Disabled

Click **Create** or **Save changes**

---

## 🔐 Protection Rule for `testing` Branch

### Branch name pattern
```
testing
```

### Settings to Enable

#### Protect matching branches
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed

#### Status checks
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Status checks:
    - ✅ `integration-tests`
    - ✅ `qa-checks`

#### Additional settings
- ✅ **Require conversation resolution before merging**
- ✅ **Include administrators**
- ✅ **Allow force pushes** → ❌ Disabled
- ✅ **Allow deletions** → ❌ Disabled

Click **Create** or **Save changes**

---

## 🔓 Protection Rule for `develop` Branch

### Branch name pattern
```
develop
```

### Settings to Enable

#### Protect matching branches
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**

#### Status checks
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Status checks:
    - ✅ `unit-tests`
    - ✅ `code-coverage` (minimum 80%)
    - ✅ `linting`

#### Additional settings
- ✅ **Require conversation resolution before merging**
- ✅ **Allow force pushes** → ❌ Disabled

Click **Create** or **Save changes**

---

## 🏷️ Default Branch Setting

### Set `develop` as Default Branch (for active development)

1. Go to **Settings** → **Branches**
2. Under **Default branch**, click the switch icon
3. Select `develop` from the dropdown
4. Click **Update**
5. Confirm the change

**Why?** New pull requests and clones will use `develop` by default, which is your active integration branch.

---

## 📋 Summary of Protection Levels

| Branch | Approvals | Status Checks | Force Push | Delete | Who Can Merge |
|--------|-----------|---------------|------------|--------|---------------|
| **master** | 2 required | ALL must pass | ❌ Blocked | ❌ Blocked | Project lead only |
| **testing** | 1 required | Integration tests | ❌ Blocked | ❌ Blocked | Team leads + QA |
| **develop** | 1 required | Unit tests + coverage | ❌ Blocked | ✅ Allowed | Developers |
| **feature/** | 0 required | None required | ✅ Allowed | ✅ Allowed | Individual devs |

---

## 🔐 Additional Security Recommendations

### 1. Enable Two-Factor Authentication (2FA)
- Go to **Settings** (your profile) → **Password and authentication**
- Enable 2FA for all contributors

### 2. Add CODEOWNERS File
Create `.github/CODEOWNERS` file:

```
# Default owners for everything
*       @x-LANsolo-x

# Specific ownership
/arenaagent/config/     @x-LANsolo-x
/arenaagent/session/    @x-LANsolo-x
/tests/                 @x-LANsolo-x
```

### 3. Set Up Required Workflows

Create `.github/workflows/branch-protection.yml`:

```yaml
name: Branch Protection Checks

on:
  pull_request:
    branches:
      - master
      - testing
      - develop

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/ -v --cov=arenaagent --cov-report=term-missing
      - name: Check coverage
        run: |
          coverage report --fail-under=80
```

### 4. Repository Settings

Go to **Settings** → **General**:

- ✅ **Disable** "Allow merge commits" (optional - enforce squash/rebase)
- ✅ **Enable** "Automatically delete head branches" (cleans up merged feature branches)
- ✅ **Enable** "Always suggest updating pull request branches"

---

## 🚨 Emergency Override (Break Glass Procedure)

In case of critical emergency where rules must be bypassed:

1. **Document the reason** in an issue
2. **Temporarily disable** branch protection
3. **Make the emergency fix**
4. **Re-enable** branch protection immediately
5. **Create a post-mortem** document

**Note:** This should be extremely rare (less than once per year).

---

## ✅ Verification Checklist

After setting up branch protection:

- [ ] Try to push directly to `master` (should fail)
- [ ] Try to push directly to `testing` (should fail)
- [ ] Try to push directly to `develop` (should fail if protected)
- [ ] Create a test PR from feature branch to `develop`
- [ ] Verify status checks run on PR
- [ ] Verify approval is required before merge
- [ ] Test that PR cannot be merged without approvals

---

## 📞 Support

If you encounter issues:
1. Check GitHub's branch protection documentation
2. Verify you have admin access to the repository
3. Ensure GitHub Actions are enabled
4. Check that status checks are properly configured

---

## 🔄 Updating These Rules

Branch protection rules can be modified anytime:
1. Go to **Settings** → **Branches**
2. Click **Edit** next to the rule
3. Make changes
4. Click **Save changes**

---

**Current Status:**
- ✅ `master` branch created
- ✅ `develop` branch created and pushed
- ✅ `testing` branch created and pushed
- ⏳ Branch protection rules (awaiting setup)
- ⏳ Required status checks (awaiting CI/CD configuration)

**Next Steps:**
1. Apply branch protection rules using this guide
2. Set up GitHub Actions for automated testing
3. Configure required status checks
4. Test the workflow with a sample PR

---

*Last updated: February 17, 2026*
*Repository: https://github.com/x-LANsolo-x/ARENAagent*
