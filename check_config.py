"""
Configuration checker - verifies your .env settings
"""
import os
from pathlib import Path

def check_config():
    print("=" * 60)
    print("Configuration Status Check")
    print("=" * 60)
    
    # Check .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        print("\n❌ .env file not found!")
        print("   Copy .env.example to .env and fill in your credentials")
        return
    
    print("\n✅ .env file exists")
    
    # Read .env
    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # Check each required variable
    required = {
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'MS_CLIENT_ID': 'Microsoft Azure Client ID',
        'MS_TENANT_ID': 'Microsoft Azure Tenant ID',
        'MS_CLIENT_SECRET': 'Microsoft Azure Client Secret',
    }
    
    optional = {
        'OPENAI_API_KEY': 'OpenAI API key (for LLM features)',
    }
    
    print("\n" + "=" * 60)
    print("Required Configuration")
    print("=" * 60)
    
    all_good = True
    for key, description in required.items():
        value = env_vars.get(key, '')
        if not value or value.startswith('your'):
            print(f"❌ {key}: Not configured")
            print(f"   ({description})")
            all_good = False
        else:
            # Show first/last few characters for security
            if len(value) > 20:
                masked = f"{value[:8]}...{value[-4:]}"
            else:
                masked = value[:4] + "..." if len(value) > 4 else "***"
            print(f"✅ {key}: {masked}")
    
    print("\n" + "=" * 60)
    print("Optional Configuration")
    print("=" * 60)
    
    for key, description in optional.items():
        value = env_vars.get(key, '')
        if not value or value.startswith('your') or value == 'sk-xxxxx':
            print(f"⚠️  {key}: Not configured (optional)")
            print(f"   ({description})")
        else:
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 20 else "***"
            print(f"✅ {key}: {masked}")
    
    # Check Obsidian vault
    print("\n" + "=" * 60)
    print("Obsidian Vault")
    print("=" * 60)
    
    vault_path = r"C:\Users\leebe\OneDrive - MOG Pattern & Machine Corp\Apps\obsidian\plan_25"
    if os.path.exists(vault_path):
        print(f"✅ Vault directory exists: {vault_path}")
        md_files = list(Path(vault_path).rglob("*.md"))
        print(f"   Found {len(md_files)} markdown files")
        
        # Check for WeeklyPlan.md
        weekly_plan = Path(vault_path) / "WeeklyPlan.md"
        if weekly_plan.exists():
            print(f"✅ WeeklyPlan.md exists")
        else:
            print(f"⚠️  WeeklyPlan.md not found (create it for /priorities command)")
    else:
        print(f"❌ Vault directory not found: {vault_path}")
    
    # Check database
    print("\n" + "=" * 60)
    print("Database")
    print("=" * 60)
    
    db_path = Path("data/time_tracking.db")
    if db_path.exists():
        print(f"✅ Database exists: {db_path}")
        size = db_path.stat().st_size
        print(f"   Size: {size} bytes")
    else:
        print(f"⚠️  Database not created yet (will be created on first run)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all_good:
        print("✅ All required configuration is set!")
        print("\nNext steps:")
        print("1. Run: python test_obsidian.py")
        print("2. Run: python test_timetracker.py")
        print("3. Run: uvicorn app.main:app --reload")
        print("4. Message your bot on Telegram")
    else:
        print("⚠️  Some configuration is missing")
        print("\nSee SETUP_CHECKLIST.md for detailed setup instructions")

if __name__ == "__main__":
    check_config()
