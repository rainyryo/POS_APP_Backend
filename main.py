"""FastAPI POSシステム バックエンド"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection, get_cursor
from models import ProductSearchResponse, PurchaseRequest, PurchaseResponse
from datetime import datetime

app = FastAPI(title="POS System API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "POS System API is running"}

@app.get("/api/product/{code}", response_model=ProductSearchResponse)
async def search_product(code: str):
    """
    商品マスタ検索API

    パラメータ:
        code: 商品コード

    リターン:
        商品情報（商品一意キー/商品コード/商品名称/商品単価）
        または NULL情報
    """
    try:
        with get_db_connection() as conn:
            with get_cursor(conn) as cursor:
                query = """
                SELECT PRD_ID, CODE, NAME, PRICE
                FROM product_master
                WHERE CODE = %s
                """
                cursor.execute(query, (code,))
                result = cursor.fetchone()

                if result:
                    return ProductSearchResponse(
                        PRD_ID=result['PRD_ID'],
                        CODE=result['CODE'],
                        NAME=result['NAME'],
                        PRICE=result['PRICE']
                    )
                else:
                    # 商品が見つからない場合はNULL情報を返す
                    return ProductSearchResponse(
                        PRD_ID=None,
                        CODE=None,
                        NAME=None,
                        PRICE=None
                    )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/purchase", response_model=PurchaseResponse)
async def purchase(request: PurchaseRequest):
    """
    購入API

    パラメータ:
        EMP_CD: レジ担当者コード（デフォルト: '9999999999'）
        STORE_CD: 店舗コード（デフォルト: '30'）
        POS_NO: POS機ID（デフォルト: '90'）
        items: 商品リスト

    リターン:
        success: 成否（True/False）
        total_amount: 合計金額
    """
    try:
        with get_db_connection() as conn:
            with get_cursor(conn) as cursor:
                # 1. 取引テーブルへ登録
                insert_transaction_query = """
                INSERT INTO transaction (DATETIME, EMP_CD, STORE_CD, POS_NO, TOTAL_AMT)
                VALUES (%s, %s, %s, %s, %s)
                """
                current_datetime = datetime.now()
                cursor.execute(
                    insert_transaction_query,
                    (current_datetime, request.EMP_CD, request.STORE_CD, request.POS_NO, 0)
                )

                # 取引一意キーを取得
                transaction_id = cursor.lastrowid

                # 2. 取引明細へ登録 & 3. 合計を計算
                total_amount = 0
                for idx, item in enumerate(request.items, start=1):
                    insert_detail_query = """
                    INSERT INTO transaction_detail
                    (TRD_ID, DTL_ID, PRD_ID, PRD_CODE, PRD_NAME, PRD_PRICE)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_detail_query,
                        (transaction_id, idx, item.PRD_ID, item.PRD_CODE,
                         item.PRD_NAME, item.PRD_PRICE)
                    )
                    total_amount += item.PRD_PRICE

                # 4. 取引テーブルを更新（合計金額）
                update_transaction_query = """
                UPDATE transaction
                SET TOTAL_AMT = %s
                WHERE TRD_ID = %s
                """
                cursor.execute(update_transaction_query, (total_amount, transaction_id))

                conn.commit()

                # 5. 合計金額をフロントへ返す
                return PurchaseResponse(
                    success=True,
                    total_amount=total_amount,
                    transaction_id=transaction_id
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@app.get("/api/transactions")
async def get_transactions(limit: int = 10):
    """取引履歴取得（デバッグ用）"""
    try:
        with get_db_connection() as conn:
            with get_cursor(conn) as cursor:
                query = """
                SELECT * FROM transaction
                ORDER BY DATETIME DESC
                LIMIT %s
                """
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                return {"transactions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)