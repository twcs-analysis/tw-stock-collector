#!/usr/bin/env python3
"""
GAS Web App 呼叫測試腳本

功能：
- 讀取指定股票的技術分析資料
- 發送 POST 請求到 Google Apps Script Web App
- 驗證回應狀態並顯示結果

使用方式：
    python scripts/gas/gas_caller.py --stock-id 3167
    python scripts/gas/gas_caller.py --stock-id 2330 --date 2026-02-04
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# GAS Web App URL
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwUP0ejovcEml4TwoErQgF8G6gYaHE1_hNkMn9XZaaGU-0wuKj_RPzZ6C4KyoLyCktBxQ/exec"


def load_stock_data(stock_id: str, date: str) -> dict:
    """
    載入指定股票的技術分析資料

    Args:
        stock_id: 股票代號（如：3167）
        date: 日期（如：2026-02-04）

    Returns:
        股票完整資料（包含價格與技術指標）
    """
    # 建立檔案路徑
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")

    # 嘗試從 transformed/technical 讀取（包含年月子目錄）
    technical_file = project_root / f"data/transformed/technical/{year}/{month}/{date}.json"

    if not technical_file.exists():
        raise FileNotFoundError(f"找不到技術分析資料: {technical_file}")

    # 讀取資料
    with open(technical_file, 'r', encoding='utf-8') as f:
        all_stocks = json.load(f)

    # 尋找指定股票
    stock_data = next((s for s in all_stocks if s['stock_id'] == stock_id), None)

    if not stock_data:
        raise ValueError(f"找不到股票 {stock_id} 的資料")

    # 從原始資料中取得股票名稱
    raw_file = project_root / f"data/raw/price/{year}/{month}/{date}.json"
    if raw_file.exists():
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            raw_stock = next((s for s in raw_data['data'] if s['stock_id'] == stock_id), None)
            if raw_stock:
                stock_data['stock_name'] = raw_stock.get('stock_name', stock_id)

    return stock_data


def build_report_data(stock_data: dict) -> dict:
    """
    建立符合 GAS 預期格式的報告資料

    Args:
        stock_data: 股票完整資料

    Returns:
        格式化的報告資料
    """
    return {
        "stock_info": {
            "stock_id": stock_data['stock_id'],
            "stock_name": stock_data.get('stock_name', stock_data['stock_id']),
            "trade_date": stock_data['trade_date']
        },
        "price_data": {
            "open": float(stock_data['open']),
            "high": float(stock_data['high']),
            "low": float(stock_data['low']),
            "close": float(stock_data['close']),
            "volume": int(stock_data['volume']),
            "amount": int(stock_data['amount'])
        },
        "technical_indicators": {
            "ma": {
                "ma_5": float(stock_data['ma_5']) if stock_data['ma_5'] else None,
                "ma_10": float(stock_data['ma_10']) if stock_data['ma_10'] else None,
                "ma_20": float(stock_data['ma_20']) if stock_data['ma_20'] else None,
                "ma_60": float(stock_data['ma_60']) if stock_data['ma_60'] else None,
                "ma_120": float(stock_data['ma_120']) if stock_data['ma_120'] else None,
                "ma_240": float(stock_data['ma_240']) if stock_data['ma_240'] else None
            },
            "rsi": {
                "rsi_6": float(stock_data['rsi_6']) if stock_data['rsi_6'] else None,
                "rsi_14": float(stock_data['rsi_14']) if stock_data['rsi_14'] else None
            },
            "macd": {
                "dif": float(stock_data['macd_dif']) if stock_data['macd_dif'] else None,
                "dea": float(stock_data['macd_dea']) if stock_data['macd_dea'] else None,
                "histogram": float(stock_data['macd_hist']) if stock_data['macd_hist'] else None
            },
            "dmi": {
                "pdi": float(stock_data['dmi_pdi']) if stock_data['dmi_pdi'] else None,
                "mdi": float(stock_data['dmi_mdi']) if stock_data['dmi_mdi'] else None,
                "adx": float(stock_data['dmi_adx']) if stock_data['dmi_adx'] else None,
                "adxr": float(stock_data['dmi_adxr']) if stock_data['dmi_adxr'] else None
            },
            "bollinger": {
                "upper": float(stock_data['bb_upper']) if stock_data['bb_upper'] else None,
                "mid": float(stock_data['bb_mid']) if stock_data['bb_mid'] else None,
                "lower": float(stock_data['bb_lower']) if stock_data['bb_lower'] else None
            },
            "volume": {
                "vol_ma5": float(stock_data['vol_ma5']) if stock_data['vol_ma5'] else None,
                "vol_ma20": float(stock_data['vol_ma20']) if stock_data['vol_ma20'] else None,
                "vol_ratio": float(stock_data['vol_ratio']) if stock_data['vol_ratio'] else None,
                "vwap": float(stock_data['vwap']) if stock_data['vwap'] else None
            }
        }
    }


def call_gas_web_app(report_data: dict, callback_url: str = None) -> dict:
    """
    呼叫 GAS Web App

    Args:
        report_data: 報告資料
        callback_url: 回調 URL（選填）

    Returns:
        GAS 回應結果
    """
    # 建立 POST 請求資料
    payload = {
        "reportId": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "reportData": report_data,
        "callbackUrl": callback_url or "",
        "timestamp": datetime.now().isoformat()
    }

    print("\n📤 發送請求到 GAS Web App...")
    print(f"URL: {GAS_WEB_APP_URL}")
    print(f"Report ID: {payload['reportId']}")
    print(f"Stock: {report_data['stock_info']['stock_name']} ({report_data['stock_info']['stock_id']})")

    # 發送 POST 請求
    try:
        response = requests.post(
            GAS_WEB_APP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        print(f"\n✅ HTTP 狀態碼: {response.status_code}")

        # 檢查 HTTP 狀態碼
        if response.status_code == 401:
            print("\n❌ 授權失敗 (401 Unauthorized)")
            print("\n💡 可能原因：")
            print("   1. GAS Web App 部署設定錯誤")
            print("   2. 執行身分設定為「我」但未正確授權")
            print("   3. 存取權限設定為「僅自己」而非「所有人」")
            print("\n🔧 解決方式：")
            print("   1. 前往 GAS 編輯器 → 部署 → 管理部署作業")
            print("   2. 點擊「編輯」（鉛筆圖示）")
            print("   3. 確認設定：")
            print("      - 執行身分：我")
            print("      - 具有存取權的使用者：所有人")
            print("   4. 點擊「部署」更新")
            print(f"\n📄 回應內容: {response.text[:200]}")
            raise Exception("GAS Web App 授權失敗，請檢查部署設定")

        if response.status_code == 403:
            print("\n❌ 禁止存取 (403 Forbidden)")
            print("\n💡 可能原因：")
            print("   1. Google 帳號權限不足")
            print("   2. API 配額用盡")
            print(f"\n📄 回應內容: {response.text[:200]}")
            raise Exception("GAS Web App 存取被拒，請檢查權限設定")

        if response.status_code != 200:
            print(f"\n⚠️ 非預期的 HTTP 狀態碼: {response.status_code}")
            print(f"📄 回應內容: {response.text[:500]}")

        # 解析回應
        try:
            result = response.json()
        except ValueError as e:
            print(f"\n❌ 無法解析 JSON 回應")
            print(f"📄 原始回應內容: {response.text[:500]}")
            raise Exception(f"GAS 回應格式錯誤: {e}")

        return result

    except requests.exceptions.Timeout:
        print("\n❌ 請求逾時（GAS 可能需要較長時間處理）")
        print("💡 建議：稍後重試，或檢查 GAS 執行日誌")
        raise
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 請求失敗: {e}")
        print(f"💡 請檢查網路連線與 GAS Web App URL")
        raise


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="測試 GAS Web App 呼叫",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--stock-id",
        required=True,
        help="股票代號（如：3167、2330）"
    )

    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="交易日期（預設：今天，格式：YYYY-MM-DD）"
    )

    parser.add_argument(
        "--callback-url",
        help="回調 URL（選填）"
    )

    parser.add_argument(
        "--save-payload",
        action="store_true",
        help="儲存發送的 payload 到檔案"
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("📊 GAS Web App 測試腳本")
        print("=" * 60)

        # 1. 載入股票資料
        print(f"\n🔍 載入股票資料: {args.stock_id} ({args.date})")
        stock_data = load_stock_data(args.stock_id, args.date)
        print(f"✅ 成功載入: {stock_data.get('stock_name', args.stock_id)}")

        # 2. 建立報告資料
        print("\n📋 建立報告資料...")
        report_data = build_report_data(stock_data)

        # 3. 儲存 payload（選填）
        if args.save_payload:
            payload_file = project_root / f"scripts/gas/test_payload_{args.stock_id}_{args.date}.json"
            with open(payload_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "reportId": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "reportData": report_data,
                    "callbackUrl": args.callback_url or "",
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Payload 已儲存: {payload_file}")

        # 4. 呼叫 GAS Web App
        result = call_gas_web_app(report_data, args.callback_url)

        # 5. 顯示結果
        print("\n" + "=" * 60)
        print("📥 GAS 回應結果")
        print("=" * 60)

        # 顯示基本資訊（不含 Markdown 內容）
        result_summary = {k: v for k, v in result.items() if k != 'markdown_content'}
        print(json.dumps(result_summary, indent=2, ensure_ascii=False))

        if result.get('status') == 'success':
            print("\n✅ 測試成功！")

            # 顯示 Markdown 內容（如果有）
            if result.get('markdown_content'):
                print("\n" + "=" * 60)
                print("📄 AI 分析報告")
                print("=" * 60)
                print(result['markdown_content'])

            # Drive 連結（如果有）
            if result.get('drive_link'):
                print(f"\n🔗 Google Drive 連結: {result['drive_link']}")
            else:
                print("\n💡 此次測試未儲存到 Google Drive")

        else:
            print("\n⚠️ 測試完成，但狀態非 success")

    except FileNotFoundError as e:
        print(f"\n❌ 找不到資料檔案: {e}")
        print("\n💡 建議：")
        print(f"   1. 檢查日期是否正確（使用交易日）")
        print(f"   2. 執行資料轉換: python scripts/data-transformer/transform.py --date {args.date}")
        sys.exit(1)

    except ValueError as e:
        print(f"\n❌ 資料錯誤: {e}")
        print("\n💡 建議：")
        print(f"   1. 檢查股票代號是否正確")
        print(f"   2. 確認該股票有交易資料")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
