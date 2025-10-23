#!/usr/bin/env python3
"""
Backend Cleanup Script
Safely moves old/redundant files to archive folder
"""

import os
import shutil
from pathlib import Path

# Backend directory
BACKEND_DIR = Path(__file__).parent
ARCHIVE_DIR = BACKEND_DIR / "archive"

# Files to keep in root
KEEP_FILES = {
    "main.py",
    "requirements.txt",
    "run_server.py",
    "test_integration.py",
    "test_modular_solver.py",
    ".env",
    ".gitignore",
    "CLEANUP_PLAN.md",
    "cleanup.py"
}

# Directories to keep
KEEP_DIRS = {"routes", "models", "app", "archive", "tests", "docs"}

# Documentation files to keep
KEEP_DOCS = {
    "START_HERE.md",
    "INTEGRATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "README_REFACTORED.md"
}

def create_archive_structure():
    """Create archive folder structure"""
    subdirs = [
        "documentation",
        "old_tests",
        "example_data",
        "cache"
    ]
    
    for subdir in subdirs:
        (ARCHIVE_DIR / subdir).mkdir(parents=True, exist_ok=True)
    
    print("✅ Archive structure created")

def move_documentation():
    """Move old documentation files to archive"""
    count = 0
    for file in BACKEND_DIR.glob("*.md"):
        if file.name not in KEEP_DOCS and file.name != "CLEANUP_PLAN.md":
            try:
                dest = ARCHIVE_DIR / "documentation" / file.name
                shutil.move(str(file), str(dest))
                print(f"  📦 Moved: {file.name}")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to move {file.name}: {e}")
    
    print(f"✅ Moved {count} documentation files")
    return count

def move_test_files():
    """Move old test files to archive"""
    test_files = [
        "example_usage.py",
        "feasible_test.py",
        "full_test.py",
        "quick_test.py",
        "test_constraints.py",
        "test_example.py",
        "test_generate_route.py"
    ]
    
    count = 0
    for filename in test_files:
        file = BACKEND_DIR / filename
        if file.exists():
            try:
                dest = ARCHIVE_DIR / "old_tests" / filename
                shutil.move(str(file), str(dest))
                print(f"  📦 Moved: {filename}")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to move {filename}: {e}")
    
    print(f"✅ Moved {count} test files")
    return count

def move_test_outputs():
    """Move test output files to archive"""
    output_files = [
        "feasible_test_output.txt",
        "full_test_output.txt",
        "test_output.txt"
    ]
    
    count = 0
    for filename in output_files:
        file = BACKEND_DIR / filename
        if file.exists():
            try:
                dest = ARCHIVE_DIR / "old_tests" / filename
                shutil.move(str(file), str(dest))
                print(f"  📦 Moved: {filename}")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to move {filename}: {e}")
    
    print(f"✅ Moved {count} test output files")
    return count

def move_example_data():
    """Move example data files to archive"""
    example_files = [
        "example_generate_request.json",
        "example_request.json"
    ]
    
    count = 0
    for filename in example_files:
        file = BACKEND_DIR / filename
        if file.exists():
            try:
                dest = ARCHIVE_DIR / "example_data" / filename
                shutil.move(str(file), str(dest))
                print(f"  📦 Moved: {filename}")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to move {filename}: {e}")
    
    print(f"✅ Moved {count} example data files")
    return count

def move_cache():
    """Move __pycache__ to archive"""
    pycache_src = BACKEND_DIR / "app" / "__pycache__"
    
    if pycache_src.exists():
        try:
            pycache_dest = ARCHIVE_DIR / "cache" / "app__pycache__"
            shutil.move(str(pycache_src), str(pycache_dest))
            print(f"  📦 Moved: app/__pycache__")
            print(f"✅ Moved cache files")
            return 1
        except Exception as e:
            print(f"  ⚠️  Failed to move cache: {e}")
            print(f"✅ Skipped cache (may be in use)")
            return 0
    
    print(f"✅ No cache to move")
    return 0

def create_tests_folder():
    """Move current tests to tests/ folder"""
    tests_dir = BACKEND_DIR / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    test_files = ["test_integration.py", "test_modular_solver.py"]
    count = 0
    
    for filename in test_files:
        src = BACKEND_DIR / filename
        dest = tests_dir / filename
        
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(str(src), str(dest))
                print(f"  📋 Copied: {filename} → tests/")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to copy {filename}: {e}")
    
    if count > 0:
        print(f"✅ Created tests/ folder with {count} files")
    else:
        print(f"✅ tests/ folder ready")

def create_docs_folder():
    """Move essential docs to docs/ folder"""
    docs_dir = BACKEND_DIR / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    doc_files = [
        "START_HERE.md",
        "INTEGRATION_GUIDE.md",
        "QUICK_REFERENCE.md",
        "README_REFACTORED.md"
    ]
    count = 0
    
    for filename in doc_files:
        src = BACKEND_DIR / filename
        dest = docs_dir / filename
        
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(str(src), str(dest))
                print(f"  📄 Copied: {filename} → docs/")
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to copy {filename}: {e}")
    
    if count > 0:
        print(f"✅ Created docs/ folder with {count} files")
    else:
        print(f"✅ docs/ folder ready")

def print_summary():
    """Print cleanup summary"""
    print("\n" + "="*70)
    print("CLEANUP COMPLETE ✅")
    print("="*70)
    
    print("\n📁 KEPT IN ROOT:")
    kept_files = [f for f in BACKEND_DIR.glob("*") if f.is_file() and f.name in KEEP_FILES]
    for f in sorted(kept_files):
        print(f"  ✅ {f.name}")
    
    print("\n📁 KEPT DIRECTORIES:")
    for d in sorted(KEEP_DIRS):
        dir_path = BACKEND_DIR / d
        if dir_path.exists():
            print(f"  ✅ {d}/")
    
    print("\n📦 ARCHIVED:")
    archive_items = list((ARCHIVE_DIR).glob("**/*"))
    if archive_items:
        for item in sorted(archive_items):
            if item.is_file():
                rel_path = item.relative_to(ARCHIVE_DIR)
                print(f"  📦 {rel_path}")
    
    print("\n" + "="*70)
    print("✨ Backend is now clean and organized!")
    print("="*70)

def main():
    """Execute cleanup"""
    print("\n🧹 BACKEND CLEANUP STARTED\n")
    
    try:
        # Create archive structure
        create_archive_structure()
        
        # Move files
        print("\n📚 Moving documentation...")
        move_documentation()
        
        print("\n🧪 Moving old tests...")
        move_test_files()
        move_test_outputs()
        
        print("\n📊 Moving example data...")
        move_example_data()
        
        print("\n💾 Moving cache...")
        move_cache()
        
        # Create organized folders
        print("\n📂 Organizing folders...")
        create_tests_folder()
        create_docs_folder()
        
        # Print summary
        print_summary()
        
        print("\n✅ Cleanup successful!")
        print("🚀 Your backend is ready to use!\n")
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}\n")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
