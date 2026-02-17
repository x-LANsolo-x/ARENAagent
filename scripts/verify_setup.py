#!/usr/bin/env python3
"""
Verify ArenaAgent development environment setup.

Run this script after initial setup to ensure everything is configured correctly.
"""

import sys
from pathlib import Path


def check_directory_structure():
    """Check if all required directories exist."""
    print("Checking directory structure...")
    
    required_dirs = [
        "arenaagent",
        "arenaagent/cli",
        "arenaagent/core",
        "arenaagent/browser",
        "arenaagent/session",
        "arenaagent/executor",
        "arenaagent/files",
        "arenaagent/config",
        "arenaagent/models",
        "arenaagent/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "examples",
        "scripts",
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
            print(f"  ✗ Missing: {dir_path}")
        else:
            print(f"  ✓ {dir_path}")
    
    if missing:
        print(f"\n❌ {len(missing)} directories missing!")
        return False
    else:
        print("\n✅ All directories present!")
        return True


def check_config_files():
    """Check if all configuration files exist."""
    print("\nChecking configuration files...")
    
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        ".gitignore",
        ".pre-commit-config.yaml",
        "Makefile",
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ Missing: {file_path}")
        else:
            print(f"  ✓ {file_path}")
    
    if missing:
        print(f"\n❌ {len(missing)} configuration files missing!")
        return False
    else:
        print("\n✅ All configuration files present!")
        return True


def check_git_repo():
    """Check if Git repository is initialized."""
    print("\nChecking Git repository...")
    
    if not Path(".git").exists():
        print("  ✗ Git repository not initialized")
        return False
    else:
        print("  ✓ Git repository initialized")
        return True


def check_package_files():
    """Check if all package __init__.py files exist."""
    print("\nChecking package initialization files...")
    
    required_init_files = [
        "arenaagent/__init__.py",
        "arenaagent/cli/__init__.py",
        "arenaagent/core/__init__.py",
        "arenaagent/browser/__init__.py",
        "arenaagent/session/__init__.py",
        "arenaagent/executor/__init__.py",
        "arenaagent/files/__init__.py",
        "arenaagent/config/__init__.py",
        "arenaagent/models/__init__.py",
        "arenaagent/utils/__init__.py",
    ]
    
    missing = []
    for file_path in required_init_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ Missing: {file_path}")
        else:
            print(f"  ✓ {file_path}")
    
    if missing:
        print(f"\n❌ {len(missing)} __init__.py files missing!")
        return False
    else:
        print("\n✅ All package files present!")
        return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("ArenaAgent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_directory_structure(),
        check_config_files(),
        check_git_repo(),
        check_package_files(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed! Setup is complete.")
        print("\nNext steps:")
        print("  1. Create a virtual environment: python -m venv venv")
        print("  2. Activate it: source venv/bin/activate")
        print("  3. Install dependencies: make install-dev")
        print("  4. Run tests: make test")
        print("  5. Start coding!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
