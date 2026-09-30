import json, sys

text = open('index.html', 'r', encoding='utf-8').read()
start = text.find('<script type="application/json" id="tender-data">')
if start < 0:
    print("not found")
    sys.exit(1)
start = text.find('{', start)
# Find matching closing </script>
end_script = text.find('</script>', start)
json_text = text[start:end_script].strip()
data = json.loads(json_text)
projects = data.get('projects', [])
print(f"TOTAL_PROJECTS={len(projects)}")
for p in projects:
    print(f"{p.get('company','')}|{p.get('project','')}|{p.get('deadline','')}|{p.get('rec','')}")
