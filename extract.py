import json, sys

def extract(file_path, keyword):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'projects' in data:
        items = [p for p in data['projects'] if keyword in p.get('company','') or keyword in p.get('title','') or keyword in p.get('overview','')]
    elif isinstance(data, list):
        items = [p for p in data if keyword in str(p.get('company','')) or keyword in str(p.get('title','')) or keyword in str(p.get('overview',''))]
    else:
        items = []
    for p in items:
        print(json.dumps(p, ensure_ascii=False, indent=2))
        print('---')

if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])
