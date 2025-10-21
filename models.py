"""データモデル定義"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    """商品マスタモデル"""
    PRD_ID: Optional[int] = None
    CODE: str
    NAME: str
    PRICE: int

class ProductSearchResponse(BaseModel):
    """商品検索レスポンス"""
    PRD_ID: Optional[int] = None
    CODE: Optional[str] = None
    NAME: Optional[str] = None
    PRICE: Optional[int] = None

class PurchaseItem(BaseModel):
    """購入商品アイテム"""
    PRD_ID: int
    PRD_CODE: str
    PRD_NAME: str
    PRD_PRICE: int

class PurchaseRequest(BaseModel):
    """購入リクエスト"""
    EMP_CD: Optional[str] = '9999999999'
    STORE_CD: Optional[str] = '30'
    POS_NO: Optional[str] = '90'
    items: List[PurchaseItem]

class PurchaseResponse(BaseModel):
    """購入レスポンス"""
    success: bool
    total_amount: int
    transaction_id: Optional[int] = None