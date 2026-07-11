import sys
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from credential_store import store_credential

# Store qianlima credentials
store_credential('qianlima', {
    'url': 'https://www.qianlima.com/',
    'username': 'chaxun032322',
    'password': 'Chaxun!2026'
})

print("✅ 千里马招标网VIP账号已加密存储")
