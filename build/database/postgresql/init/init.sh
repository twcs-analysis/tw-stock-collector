#!/bin/bash
# ====================================
# PostgreSQL 資料庫初始化腳本
# ====================================
#
# 此腳本會在 PostgreSQL 容器啟動時自動執行
# 用於初始化資料庫 schema

set -e

echo "開始初始化台股資料庫..."

# 執行 schema 檔案
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \echo '執行資料表定義...'
    \i /docker-entrypoint-initdb.d/01-tables.sql

    \echo '執行索引定義...'
    \i /docker-entrypoint-initdb.d/02-indexes.sql

    \echo '執行序列定義...'
    \i /docker-entrypoint-initdb.d/03-sequences.sql

    \echo '執行觸發器定義...'
    \i /docker-entrypoint-initdb.d/04-triggers.sql

    \echo '資料庫初始化完成！'
EOSQL

echo "台股資料庫初始化成功！"
