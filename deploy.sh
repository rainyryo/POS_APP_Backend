#!/bin/bash

# Azure Web App デプロイスクリプト

# 変数設定（適宜変更してください）
RESOURCE_GROUP="pos-rg"
APP_NAME="pos-api-backend"
LOCATION="japaneast"
RUNTIME="PYTHON:3.11"

echo "=== Azure Web App デプロイ開始 ==="

# リソースグループの作成
echo "1. リソースグループを作成中..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# App Service Planの作成
echo "2. App Service Planを作成中..."
az appservice plan create \
  --name ${APP_NAME}-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Web Appの作成
echo "3. Web Appを作成中..."
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan ${APP_NAME}-plan \
  --runtime $RUNTIME

# 起動コマンドの設定
echo "4. 起動コマンドを設定中..."
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "startup.txt"

# 環境変数の設定
echo "5. 環境変数を設定中..."
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DB_HOST="rdbs-002-gen10-step3-2-oshima8.mysql.database.azure.com" \
    DB_PORT="3306" \
    DB_USER="tech0gen10student" \
    DB_PASSWORD="vY7JZNfU" \
    DB_NAME="pos_db"

# デプロイ
echo "6. アプリケーションをデプロイ中..."
az webapp up \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --runtime $RUNTIME

echo "=== デプロイ完了 ==="
echo "URL: https://${APP_NAME}.azurewebsites.net"