"""
Simple test script to verify Obsidian integration works
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.obsidian_tasks import (
    get_priorities_from_obsidian,
    get_tasks_from_note,
    read_obsidian_note
)
from app.config import settings

async def test_obsidian_integration():
    print("=" * 60)
    print("Testing Obsidian Integration")
    print("=" * 60)
    print(f"\nVault path: {settings.obsidian_local_path}")
    print(f"Vault ID: {settings.obsidian_vault_id}")
    
    # Test 1: Check if vault directory exists
    print("\n[Test 1] Checking vault directory...")
    if os.path.exists(settings.obsidian_local_path):
        print(f"✅ Vault directory exists")
        files = os.listdir(settings.obsidian_local_path)
        print(f"   Found {len(files)} items in vault:")
        for f in files[:10]:  # Show first 10 items
            print(f"   - {f}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more")
    else:
        print(f"❌ Vault directory does not exist!")
        print("   Please check the path in config.py or your .env file")
        return
    
    # Test 2: Try to read WeeklyPlan.md
    print("\n[Test 2] Reading WeeklyPlan.md...")
    try:
        priorities = await get_priorities_from_obsidian("WeeklyPlan.md")
        print(f"✅ Successfully read priorities:")
        print(priorities)
    except FileNotFoundError:
        print("⚠️  WeeklyPlan.md not found in vault root")
        print("   You can specify a different file, e.g., 'Tasks/WeeklyPlan.md'")
    except Exception as e:
        print(f"❌ Error reading priorities: {e}")
    
    # Test 3: List markdown files
    print("\n[Test 3] Finding markdown files in vault...")
    md_files = []
    for root, dirs, files in os.walk(settings.obsidian_local_path):
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), settings.obsidian_local_path)
                md_files.append(rel_path)
    
    if md_files:
        print(f"✅ Found {len(md_files)} markdown files:")
        for f in md_files[:20]:  # Show first 20
            print(f"   - {f}")
        if len(md_files) > 20:
            print(f"   ... and {len(md_files) - 20} more")
    else:
        print("❌ No markdown files found!")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_obsidian_integration())
