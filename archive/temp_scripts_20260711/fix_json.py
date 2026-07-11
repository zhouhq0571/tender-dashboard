import json, re

# Read index.html
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON data
match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if not match:
    print("ERROR: Could not find JSON data")
    exit(1)

json_str = match.group(1)

# The issue: JSON string values contain raw newlines (\n) instead of escaped newlines (\\n)
# We need to properly parse the HTML-embedded JSON which may have raw newlines in strings
# Strategy: Use json.loads with strict=False to allow control characters, then re-serialize

try:
    # strict=False allows control characters in strings
    data = json.loads(json_str, strict=False)
    print(f"JSON parsed with strict=False. Projects: {len(data.get('projects', []))}")
    
    # Now re-serialize properly (this will escape all control characters correctly)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    # Write back to index.html
    new_content = content.replace(json_str, new_json)
    
    with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("index.html has been fixed and saved.")
    
    # Verify by reading back
    with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r', encoding='utf-8') as f:
        verify_content = f.read()
    verify_match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', verify_content, re.DOTALL)
    verify_data = json.loads(verify_match.group(1))
    print(f"Verification passed! Projects: {len(verify_data.get('projects', []))}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
