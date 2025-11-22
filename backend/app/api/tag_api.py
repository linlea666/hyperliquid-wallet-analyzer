"""
标签管理 API
支持标签的增删改查、搜索、统计
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from loguru import logger

from app.services.tag_manager import tag_manager, TagCategory

router = APIRouter()


class AddTagRequest(BaseModel):
    """添加标签请求"""
    address: str = Field(..., description="钱包地址")
    tag_name: str = Field(..., description="标签名称")
    category: str = Field("special", description="标签分类")


class RemoveTagRequest(BaseModel):
    """移除标签请求"""
    address: str = Field(..., description="钱包地址")
    tag_name: str = Field(..., description="标签名称")


class SearchByTagsRequest(BaseModel):
    """按标签搜索请求"""
    tags: List[str] = Field(..., description="标签列表")
    match_all: bool = Field(False, description="是否匹配所有标签")


@router.post("/add")
async def add_tag(request: AddTagRequest):
    """
    添加用户自定义标签
    
    - 为钱包添加自定义标签
    - 支持分类
    """
    try:
        # 验证分类
        try:
            category = TagCategory(request.category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的标签分类: {request.category}")
        
        # 添加标签
        success = tag_manager.add_user_tag(
            address=request.address,
            tag_name=request.tag_name,
            category=category
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="添加标签失败（钱包不存在或标签已存在）")
        
        return {
            "success": True,
            "message": "标签添加成功",
            "data": {
                "address": request.address,
                "tag_name": request.tag_name,
                "category": request.category
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加标签失败: {str(e)}")


@router.post("/remove")
async def remove_tag(request: RemoveTagRequest):
    """
    移除标签
    
    - 从钱包移除指定标签
    """
    try:
        success = tag_manager.remove_tag(
            address=request.address,
            tag_name=request.tag_name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="移除标签失败（钱包不存在或标签不存在）")
        
        return {
            "success": True,
            "message": "标签移除成功",
            "data": {
                "address": request.address,
                "tag_name": request.tag_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除标签失败: {str(e)}")


@router.get("/{address}")
async def get_wallet_tags(address: str):
    """
    获取钱包的所有标签
    
    - 返回标签列表
    - 包含标签来源、分类、权重等信息
    """
    try:
        tags = tag_manager.get_tags(address)
        
        return {
            "success": True,
            "data": {
                "address": address,
                "tags": tags,
                "count": len(tags)
            }
        }
        
    except Exception as e:
        logger.error(f"获取标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")


@router.get("/popular/list")
async def get_popular_tags(limit: int = 20):
    """
    获取热门标签
    
    - 按使用频率排序
    - 返回标签统计
    """
    try:
        popular = tag_manager.get_popular_tags(limit=limit)
        
        return {
            "success": True,
            "data": {
                "tags": popular,
                "count": len(popular)
            }
        }
        
    except Exception as e:
        logger.error(f"获取热门标签失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门标签失败: {str(e)}")


@router.post("/search")
async def search_by_tags(request: SearchByTagsRequest):
    """
    根据标签搜索钱包
    
    - 支持单个或多个标签
    - 支持 AND/OR 逻辑
    """
    try:
        if not request.tags:
            raise HTTPException(status_code=400, detail="标签列表不能为空")
        
        addresses = tag_manager.search_by_tags(
            tags=request.tags,
            match_all=request.match_all
        )
        
        return {
            "success": True,
            "data": {
                "addresses": addresses,
                "count": len(addresses),
                "query": {
                    "tags": request.tags,
                    "match_all": request.match_all
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标签搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/categories/list")
async def get_tag_categories():
    """
    获取所有标签分类
    
    - 返回可用的标签分类列表
    """
    try:
        categories = [
            {
                "value": cat.value,
                "label": {
                    "performance": "表现类",
                    "risk": "风险类",
                    "skill": "技能类",
                    "experience": "经验类",
                    "style": "风格类",
                    "capital": "资金类",
                    "special": "特殊类"
                }.get(cat.value, cat.value)
            }
            for cat in TagCategory
        ]
        
        return {
            "success": True,
            "data": {
                "categories": categories
            }
        }
        
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")


@router.get("/rules/system")
async def get_system_tag_rules():
    """
    获取系统标签规则
    
    - 返回所有预定义的系统标签规则
    - 用于前端展示和理解
    """
    try:
        rules = []
        
        for tag_name, rule in tag_manager.SYSTEM_TAG_RULES.items():
            rules.append({
                "name": tag_name,
                "category": rule["category"].value,
                "weight": rule["weight"],
                "conditions": rule["conditions"],
                "description": f"自动生成条件: {rule['conditions']}"
            })
        
        return {
            "success": True,
            "data": {
                "rules": rules,
                "count": len(rules)
            }
        }
        
    except Exception as e:
        logger.error(f"获取标签规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取规则失败: {str(e)}")

