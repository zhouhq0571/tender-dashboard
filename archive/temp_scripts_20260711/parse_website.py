import sys, json, re

html = sys.stdin.read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print(f"Version: {data.get('version')}")
    print(f"Date: {data.get('date')}")
    print(f"Period: {data.get('timePeriod')}")
    print(f"Projects: {len(data.get('projects', []))}")
else:
    print("No data found")
