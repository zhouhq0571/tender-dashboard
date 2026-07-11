#!/usr/bin/env python3
"""
招标看板 - 加密凭据管理工具
用途：安全存储和读取千里马招标网VIP账号等敏感凭据

安全机制：
1. 使用 Fernet 对称加密（基于系统唯一标识生成密钥）
2. 密钥不存储在代码中，而是基于机器指纹动态生成
3. 加密文件存储在 ~/.config/tender-dashboard/ 目录
4. 明文密码永远不会出现在代码或日志中

用法：
    from credential_store import get_credential, store_credential
    
    # 存储凭据（首次使用时）
    store_credential('qianlima', {
        'url': 'https://www.qianlima.com/',
        'username': 'your_username',
        'password': 'your_password'
    })
    
    # 读取凭据（日常使用）
    creds = get_credential('qianlima')
    print(creds['username'])  # 解密后的用户名
    print(creds['password'])  # 解密后的密码
"""

import os
import json
import base64
import hashlib
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("⚠️ 警告: cryptography 模块未安装，将使用简易加密。建议运行: pip install cryptography")

# ========== 配置 ==========
CONFIG_DIR = Path.home() / '.config' / 'tender-dashboard'
CREDENTIALS_FILE = CONFIG_DIR / 'credentials.enc'

# 基于机器指纹生成密钥（确定性但唯一）
def _get_machine_fingerprint():
    """生成机器唯一指纹（跨会话一致）"""
    # 组合多个系统标识符
    identifiers = []
    
    # 1. 主机名
    identifiers.append(os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'unknown'))
    
    # 2. 用户主目录路径
    identifiers.append(str(Path.home()))
    
    # 3. 系统用户名
    identifiers.append(os.environ.get('USER', os.environ.get('USERNAME', 'unknown')))
    
    # 4. 尝试获取系统序列号（macOS）
    try:
        import subprocess
        result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if 'Serial Number' in line:
                identifiers.append(line.split(':')[-1].strip())
                break
    except:
        pass
    
    # 组合并生成哈希
    combined = '|'.join(identifiers).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()[:32]

def _get_key():
    """生成加密密钥"""
    fingerprint = _get_machine_fingerprint()
    # 使用指纹生成32字节密钥，然后base64编码为Fernet格式
    key_bytes = hashlib.sha256(fingerprint.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

def _ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # 设置权限为仅用户可读写
    os.chmod(CONFIG_DIR, 0o700)

def _simple_encrypt(data: str, key: bytes) -> str:
    """简易加密（无cryptography时的fallback）"""
    import itertools
    key_cycle = itertools.cycle(key)
    encrypted = bytes(b ^ next(key_cycle) for b in data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('ascii')

def _simple_decrypt(data: str, key: bytes) -> str:
    """简易解密"""
    import itertools
    encrypted = base64.b64decode(data.encode('ascii'))
    key_cycle = itertools.cycle(key)
    decrypted = bytes(b ^ next(key_cycle) for b in encrypted)
    return decrypted.decode('utf-8')

def store_credential(service: str, credentials: dict):
    """
    存储加密凭据
    
    Args:
        service: 服务名称（如 'qianlima'）
        credentials: 凭据字典（如 {'username': 'xxx', 'password': 'yyy'}）
    """
    _ensure_config_dir()
    key = _get_key()
    
    # 读取现有凭据（如果有）
    all_creds = {}
    if CREDENTIALS_FILE.exists():
        try:
            all_creds = get_all_credentials()
        except:
            pass
    
    # 更新指定服务的凭据
    all_creds[service] = credentials
    
    # 加密并存储
    json_data = json.dumps(all_creds, ensure_ascii=False)
    
    if HAS_CRYPTO:
        f = Fernet(key)
        encrypted = f.encrypt(json_data.encode('utf-8'))
    else:
        encrypted = _simple_encrypt(json_data, key).encode('utf-8')
    
    # 写入文件并设置权限
    CREDENTIALS_FILE.write_bytes(encrypted)
    os.chmod(CREDENTIALS_FILE, 0o600)
    
    print(f"✅ 凭据已加密存储: {service}")
    print(f"   存储位置: {CREDENTIALS_FILE}")

def get_credential(service: str) -> dict:
    """
    读取指定服务的解密凭据
    
    Args:
        service: 服务名称
        
    Returns:
        凭据字典，如果服务不存在则返回 None
    """
    all_creds = get_all_credentials()
    return all_creds.get(service)

def get_all_credentials() -> dict:
    """读取所有解密凭据"""
    if not CREDENTIALS_FILE.exists():
        return {}
    
    key = _get_key()
    encrypted = CREDENTIALS_FILE.read_bytes()
    
    try:
        if HAS_CRYPTO:
            f = Fernet(key)
            decrypted = f.decrypt(encrypted).decode('utf-8')
        else:
            decrypted = _simple_decrypt(encrypted.decode('utf-8'), key)
        
        return json.loads(decrypted)
    except Exception as e:
        raise ValueError(f"无法解密凭据文件。可能原因：1) 机器指纹变更 2) 文件损坏。错误: {e}")

def list_services():
    """列出已存储的所有服务名称"""
    all_creds = get_all_credentials()
    return list(all_creds.keys())

def delete_credential(service: str):
    """删除指定服务的凭据"""
    all_creds = get_all_credentials()
    if service in all_creds:
        del all_creds[service]
        store_credential('_all', all_creds)  # 重新存储
        print(f"✅ 已删除凭据: {service}")
    else:
        print(f"⚠️ 凭据不存在: {service}")

# ========== CLI 接口 ==========
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 credential_store.py store <service>  # 交互式存储凭据")
        print("  python3 credential_store.py get <service>    # 读取凭据")
        print("  python3 credential_store.py list             # 列出所有服务")
        print("  python3 credential_store.py delete <service> # 删除凭据")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'store' and len(sys.argv) >= 3:
        service = sys.argv[2]
        print(f"存储凭据: {service}")
        url = input("URL: ").strip()
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
        store_credential(service, {'url': url, 'username': username, 'password': password})
    
    elif cmd == 'get' and len(sys.argv) >= 3:
        service = sys.argv[2]
        creds = get_credential(service)
        if creds:
            print(f"服务: {service}")
            print(f"URL: {creds.get('url', 'N/A')}")
            print(f"用户名: {creds.get('username', 'N/A')}")
            print(f"密码: {creds.get('password', 'N/A')}")
        else:
            print(f"❌ 未找到凭据: {service}")
            sys.exit(1)
    
    elif cmd == 'list':
        services = list_services()
        if services:
            print("已存储的服务:")
            for s in services:
                print(f"  - {s}")
        else:
            print("没有存储的凭据")
    
    elif cmd == 'delete' and len(sys.argv) >= 3:
        delete_credential(sys.argv[2])
    
    else:
        print("未知命令")
        sys.exit(1)
