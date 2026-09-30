import csv, glob, os

os.chdir('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/search_20260717')
for f in sorted(glob.glob('tyc_*.csv')):
    with open(f, encoding='utf-8-sig') as fp:
        rows = list(csv.reader(fp))
    print(f'{f}: {len(rows)-1} rows | {len(rows[0])} cols')
    print('  header:', rows[0])
    if len(rows) > 1:
        print('  sample row1:', [c[:40] for c in rows[1]])
