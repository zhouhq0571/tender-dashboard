import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if match:
    json_str = match.group(1)
    print(f'JSON length: {len(json_str)}')
    
    # Find bad control characters
    bad_chars = []
    for i in range(len(json_str)):
        ch = json_str[i]
        if ord(ch) < 32 and ch not in '\n\r\t':
            bad_chars.append((i, repr(ch), ord(ch)))
    
    print(f'Bad chars count: {len(bad_chars)}')
    print(f'Bad chars (first 10): {bad_chars[:10]}')
    
    # Also check around position 4562
    if len(json_str) > 4570:
        start = max(0, 4562 - 20)
        end = min(len(json_str), 4562 + 20)
        print(f'Context around pos 4562: {repr(json_str[start:end])}')
else:
    print('No JSON match found')
