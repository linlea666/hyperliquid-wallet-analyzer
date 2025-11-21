"""验证工具模块"""
import re
from typing import Optional


def validate_address(address: str) -> bool:
    """验证钱包地址格式"""
    if not address:
        return False
    
    # HyperLiquid 地址格式：0x 开头，42 字符
    if not address.startswith('0x'):
        return False
    
    if len(address) != 42:
        return False
    
    # 检查是否为有效的十六进制
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def normalize_address(address: str) -> Optional[str]:
    """标准化钱包地址"""
    address = address.strip()
    
    # 移除可能的空格和换行
    address = re.sub(r'\s+', '', address)
    
    # 转换为小写
    address = address.lower()
    
    if validate_address(address):
        return address
    
    return None

