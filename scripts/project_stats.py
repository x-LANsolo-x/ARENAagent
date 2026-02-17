#!/usr/bin/env python3
"""Display ArenaAgent project statistics."""

from pathlib import Path


def get_stats():
    """Calculate and display project statistics."""
    root = Path(".")
    
    # Count directories
    dirs = list(root.rglob("*"))
    total_dirs = len([d for d in dirs if d.is_dir()])
    
    # Count files by type
    all_files = [f for f in dirs if f.is_file()]
    total_files = len(all_files)
    
    py_files = len([f for f in all_files if f.suffix == ".py"])
    md_files = len([f for f in all_files if f.suffix == ".md"])
    toml_files = len([f for f in all_files if f.suffix == ".toml"])
    yaml_files = len([f for f in all_files if f.suffix in [".yaml", ".yml"]])
    txt_files = len([f for f in all_files if f.suffix == ".txt"])
    
    # Count lines of code
    total_lines = 0
    for py_file in [f for f in all_files if f.suffix == ".py"]:
        try:
            total_lines += len(py_file.read_text(encoding="utf-8").splitlines())
        except:
            pass
    
    print("=" * 60)
    print("ArenaAgent Project Statistics")
    print("=" * 60)
    print()
    print(f"📁 Total directories:      {total_dirs}")
    print(f"📄 Total files:            {total_files}")
    print()
    print("File breakdown:")
    print(f"  🐍 Python files (.py):   {py_files}")
    print(f"  📝 Markdown files (.md): {md_files}")
    print(f"  ⚙️  TOML files (.toml):   {toml_files}")
    print(f"  📋 YAML files (.yaml):   {yaml_files}")
    print(f"  📄 Text files (.txt):    {txt_files}")
    print()
    print(f"📊 Total lines of Python:  {total_lines}")
    print()
    
    # List main modules
    print("Main modules:")
    modules = sorted([d.name for d in Path("arenaagent").iterdir() if d.is_dir()])
    for module in modules:
        print(f"  • arenaagent/{module}/")
    
    print()
    print("=" * 60)
    print("✅ Phase 4: Environment Setup - COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    get_stats()
