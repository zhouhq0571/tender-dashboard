import json
import re

# Read merged data
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/merged_data.json', 'r') as f:
    data = json.load(f)

projects = data['projects']

# Read existing index.html
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

# Update version in title
old_title = '恒生银信招标资讯每日速递 | 2026年06月30日（更新）v52'
new_title = '恒生银信招标资讯每日速递 | 2026年07月01日（更新）v53'
html = html.replace(old_title, new_title)

# Also update any other version references
html = html.replace('v52', 'v53')
html = html.replace('2026年06月30日', '2026年07月01日')
html = html.replace('下午', '上午')

# Update tender-data JSON
new_json = json.dumps({"version": "v53", "date": "2026年07月01日", "timePeriod": "上午", "projects": projects}, ensure_ascii=False, indent=2)

# Find and replace tender-data content
pattern = r'(<script type="application/json" id="tender-data">)\{.*?\}(</script>)'
replacement = r'\1' + new_json + r'\2'
html = re.sub(pattern, replacement, html, flags=re.DOTALL)

# Write updated index.html
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'w') as f:
    f.write(html)

print("Updated index.html:")
print(f"  Version: v52 → v53")
print(f"  Date: 2026年06月30日 → 2026年07月01日")
print(f"  Time period: 下午 → 上午")
print(f"  Projects: 55 → {len(projects)}")
print(f"  HTML size: {len(html)} bytes")
