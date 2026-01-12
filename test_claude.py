"""
Test script to verify Claude/Anthropic integration works
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.planner import brainstorm, focus_check

async def test_claude():
    print("=" * 60)
    print("Testing Claude/Anthropic Integration")
    print("=" * 60)
    
    # Test 1: Brainstorm
    print("\n[Test 1] Testing brainstorm function...")
    context = "I run a CNC machining and manufacturing business. I'm interested in AI automation."
    question = "What are 3 quick wins I could implement with AI in my business?"
    
    try:
        result = await brainstorm(context, question)
        print(f"✅ Brainstorm response received:")
        print(f"\n{result}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Focus check
    print("\n[Test 2] Testing focus check function...")
    priorities = """Weekly Priorities:
  1. Meghan's Panel
  2. AI Assistant
  3. Stratos Pro upgraded"""
    
    calendar = "Today's Calendar:\n  • 10:00-11:00: Team meeting\n  • 14:00-15:00: Client call"
    current_task = "Working on AI Assistant"
    billable_hours = 2.5
    
    try:
        result = await focus_check(priorities, calendar, current_task, billable_hours)
        print(f"✅ Focus check response received:")
        print(f"\n{result}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Claude integration working! 🎉")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_claude())
