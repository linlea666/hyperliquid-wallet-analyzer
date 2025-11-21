"""数据存储服务"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from app.config import config, WALLETS_DIR, DATA_DIR


class StorageService:
    """数据存储服务"""
    
    def __init__(self):
        self.wallets_dir = WALLETS_DIR
        self.index_file = WALLETS_DIR / "index.json"
        self.notifications_file = DATA_DIR / "notifications.json"
        self._ensure_directories()
        self._load_index()
    
    def _ensure_directories(self):
        """确保目录存在"""
        self.wallets_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self):
        """加载钱包索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.error(f"加载索引失败: {e}")
                self.index = {"wallets": []}
        else:
            self.index = {"wallets": []}
            self._save_index()
    
    def _save_index(self):
        """保存钱包索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
    
    def wallet_exists(self, address: str) -> bool:
        """检查钱包是否存在"""
        wallet_file = self.wallets_dir / f"{address.lower()}.json"
        return wallet_file.exists()
    
    def save_wallet(self, address: str, wallet_data: Dict[str, Any]):
        """保存钱包数据"""
        try:
            wallet_file = self.wallets_dir / f"{address.lower()}.json"
            
            # 更新最后更新时间
            wallet_data["last_updated"] = datetime.now().isoformat()
            
            # 保存钱包文件
            with open(wallet_file, 'w', encoding='utf-8') as f:
                json.dump(wallet_data, f, indent=2, ensure_ascii=False)
            
            # 更新索引
            self._update_index(address, wallet_data)
            
            logger.info(f"✅ 保存钱包成功: {address}")
            
        except Exception as e:
            logger.error(f"保存钱包失败: {e}")
            raise
    
    def _update_index(self, address: str, wallet_data: Dict[str, Any]):
        """更新钱包索引"""
        metrics = wallet_data.get("metrics", {})
        metadata = wallet_data.get("metadata", {})
        
        wallet_info = {
            "address": address.lower(),
            "imported_at": wallet_data.get("imported_at", ""),
            "last_updated": wallet_data.get("last_updated", ""),
            "roi": metrics.get("roi", 0),
            "win_rate": metrics.get("win_rate", 0),
            "total_pnl": metrics.get("total_pnl", 0),
            "smart_money_score": metrics.get("smart_money_score", 0),
            "wallet_age_days": metadata.get("wallet_age_days", 0),
            "tags": metadata.get("tags", [])
        }
        
        # 查找是否已存在
        existing = None
        for i, w in enumerate(self.index["wallets"]):
            if w["address"].lower() == address.lower():
                existing = i
                break
        
        if existing is not None:
            self.index["wallets"][existing] = wallet_info
        else:
            self.index["wallets"].append(wallet_info)
        
        self._save_index()
    
    def get_wallet(self, address: str) -> Optional[Dict[str, Any]]:
        """获取钱包数据"""
        try:
            wallet_file = self.wallets_dir / f"{address.lower()}.json"
            if not wallet_file.exists():
                return None
            
            with open(wallet_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"获取钱包失败: {e}")
            return None
    
    def get_wallet_list(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "score",
        order: str = "desc",
        search: Optional[str] = None,
        tag: str = "all"
    ) -> Dict[str, Any]:
        """获取钱包列表"""
        try:
            wallets = self.index["wallets"].copy()
            
            # 搜索过滤
            if search:
                search_lower = search.lower()
                wallets = [w for w in wallets if search_lower in w["address"].lower()]
            
            # 标签过滤
            if tag == "recommended":
                # TODO: 实现推荐逻辑
                wallets = [w for w in wallets if w.get("smart_money_score", 0) >= 70]
            
            # 排序
            reverse = order == "desc"
            if sort_by == "roi":
                wallets.sort(key=lambda x: x.get("roi", 0), reverse=reverse)
            elif sort_by == "win_rate":
                wallets.sort(key=lambda x: x.get("win_rate", 0), reverse=reverse)
            elif sort_by == "score":
                wallets.sort(key=lambda x: x.get("smart_money_score", 0), reverse=reverse)
            else:
                wallets.sort(key=lambda x: x.get("total_pnl", 0), reverse=reverse)
            
            # 分页
            total = len(wallets)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_wallets = wallets[start:end]
            
            # 加载完整数据
            result_wallets = []
            for w in paginated_wallets:
                wallet_data = self.get_wallet(w["address"])
                if wallet_data:
                    result_wallets.append(wallet_data)
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "wallets": result_wallets
            }
            
        except Exception as e:
            logger.error(f"获取钱包列表失败: {e}")
            return {"total": 0, "page": page, "page_size": page_size, "wallets": []}
    
    def get_all_wallets(self) -> List[Dict[str, Any]]:
        """获取所有钱包"""
        wallets = []
        for wallet_info in self.index["wallets"]:
            wallet_data = self.get_wallet(wallet_info["address"])
            if wallet_data:
                wallets.append(wallet_data)
        return wallets
    
    def delete_wallet(self, address: str):
        """删除钱包"""
        try:
            wallet_file = self.wallets_dir / f"{address.lower()}.json"
            if wallet_file.exists():
                wallet_file.unlink()
            
            # 从索引中删除
            self.index["wallets"] = [
                w for w in self.index["wallets"]
                if w["address"].lower() != address.lower()
            ]
            self._save_index()
            
            logger.info(f"✅ 删除钱包成功: {address}")
            
        except Exception as e:
            logger.error(f"删除钱包失败: {e}")
            raise
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """获取通知列表"""
        if not self.notifications_file.exists():
            return []
        
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("notifications", [])
        except Exception as e:
            logger.error(f"获取通知列表失败: {e}")
            return []
    
    def save_notification(self, notification: Dict[str, Any]):
        """保存通知"""
        try:
            notifications = self.get_notifications()
            notifications.insert(0, notification)
            
            # 只保留最近 1000 条
            notifications = notifications[:1000]
            
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump({"notifications": notifications}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存通知失败: {e}")
    
    def mark_notification_read(self, notification_id: str):
        """标记通知已读"""
        notifications = self.get_notifications()
        for n in notifications:
            if n.get("id") == notification_id:
                n["read"] = True
                break
        
        try:
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump({"notifications": notifications}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"标记通知已读失败: {e}")
    
    def delete_notification(self, notification_id: str):
        """删除通知"""
        notifications = self.get_notifications()
        notifications = [n for n in notifications if n.get("id") != notification_id]
        
        try:
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump({"notifications": notifications}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"删除通知失败: {e}")

