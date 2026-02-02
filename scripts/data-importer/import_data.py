#!/usr/bin/env python3
"""
資料匯入腳本 - 將 JSON 資料匯入到資料庫

用法:
    # 匯入單一日期的資料
    python scripts/data-importer/import_data.py --date 2026-01-02

    # 匯入指定類型
    python scripts/data-importer/import_data.py --date 2026-01-02 --types price

    # 匯入日期區間
    python scripts/data-importer/import_data.py --start 2026-01-01 --end 2026-01-31

    # 匯入所有類型
    python scripts/data-importer/import_data.py --date 2026-01-02 --types price institutional margin lending top20_volume
"""

import sys
from pathlib import Path

# 添加專案根目錄和 services/data-importer 到 Python 路徑
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
services_importer = project_root / 'services' / 'data-importer'

sys.path.insert(0, str(services_importer))
sys.path.insert(0, str(project_root))

# 使用 services/data-importer 的 main 模組
from app.main import main

if __name__ == "__main__":
    main()
