"""
Test script to verify database and time tracking functionality
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.time_tracker import (
    init_db,
    start_timer,
    stop_timer,
    get_active_entry
)

async def test_time_tracking():
    print("=" * 60)
    print("Testing Time Tracking & Database")
    print("=" * 60)
    
    # Test 1: Initialize database
    print("\n[Test 1] Initializing database...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return
    
    # Test 2: Check for active entries
    print("\n[Test 2] Checking for active time entries...")
    try:
        active = await get_active_entry()
        if active:
            print(f"⚠️  Active entry found: {active}")
        else:
            print("✅ No active entries (good for testing)")
    except Exception as e:
        print(f"❌ Error checking active entry: {e}")
        return
    
    # Test 3: Start a timer
    print("\n[Test 3] Starting a test timer...")
    try:
        entry_id = await start_timer(
            task_id=1,
            billable=True,
            notes="Test task - automated testing"
        )
        print(f"✅ Timer started with entry ID: {entry_id}")
    except Exception as e:
        print(f"❌ Error starting timer: {e}")
        return
    
    # Test 4: Check active entry again
    print("\n[Test 4] Verifying active entry...")
    try:
        active = await get_active_entry()
        if active:
            print(f"✅ Active entry confirmed:")
            print(f"   ID: {active['id']}")
            print(f"   Task ID: {active['task_id']}")
            print(f"   Start: {active['start_time']}")
            print(f"   Notes: {active['notes']}")
            print(f"   Billable: {active['billable']}")
        else:
            print("❌ No active entry found (unexpected)")
    except Exception as e:
        print(f"❌ Error checking active entry: {e}")
        return
    
    # Test 5: Stop the timer
    print("\n[Test 5] Stopping the timer...")
    try:
        await stop_timer(entry_id)
        print(f"✅ Timer stopped successfully")
    except Exception as e:
        print(f"❌ Error stopping timer: {e}")
        return
    
    # Test 6: Verify no active entry
    print("\n[Test 6] Verifying timer was stopped...")
    try:
        active = await get_active_entry()
        if active:
            print(f"⚠️  Active entry still exists: {active}")
        else:
            print("✅ No active entries (timer successfully stopped)")
    except Exception as e:
        print(f"❌ Error checking active entry: {e}")
    
    print("\n" + "=" * 60)
    print("Time tracking tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_time_tracking())
