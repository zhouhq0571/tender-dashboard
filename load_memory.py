#!/usr/bin/env python3
"""
关键记忆自动加载脚本
用法: 在每次涉及招标看板任务时，先运行此脚本读取关键凭据和配置
"""

import json

def load_critical_memory():
    """加载关键记忆"""
    memory_file = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/CRITICAL_MEMORY.md'
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取千里马账号
    qianlima_account = None
    qianlima_password = None
    
    for line in content.split('\n'):
        if '**账号**' in line:
            qianlima_account = line.split(':')[1].strip()
        if '**密码**' in line:
            qianlima_password = line.split(':')[1].strip()
    
    return {
        'qianlima_account': qianlima_account,
        'qianlima_password': qianlima_password,
        'raw_content': content
    }

if __name__ == '__main__':
    memory = load_critical_memory()
    print("=" * 60)
    print("关键记忆已加载")
    print("=" * 60)
    print(f"千里马VIP账号: {memory['qianlima_account']}")
    print(f"千里马VIP密码: {memory['qianlima_password']}")
    print("=" * 60)
