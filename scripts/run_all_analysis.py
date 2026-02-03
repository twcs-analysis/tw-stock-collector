#!/usr/bin/env python3
"""
執行所有分析腳本並將結果儲存到指定目錄

用法:
    # 執行今天的所有分析
    python scripts/run_all_analysis.py

    # 指定日期執行分析
    python scripts/run_all_analysis.py --date 2026-02-03

    # 指定輸出目錄
    python scripts/run_all_analysis.py --output results/2026-02-03
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
import logging
import shutil

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AnalysisRunner:
    """分析執行器"""

    def __init__(self, date: str, output_dir: Path):
        self.date = date
        self.output_dir = output_dir
        self.project_root = project_root
        self.results = []

    def setup_output_dir(self):
        """建立輸出目錄"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"輸出目錄: {self.output_dir}")

    def run_analysis(self, name: str, script_path: Path, args: list = None, output_file: str = None):
        """執行單一分析腳本"""
        logger.info(f"\n{'='*70}")
        logger.info(f"執行分析: {name}")
        logger.info(f"{'='*70}")

        if not script_path.exists():
            logger.error(f"找不到腳本: {script_path}")
            self.results.append({
                'name': name,
                'status': 'failed',
                'error': '腳本不存在'
            })
            return False

        try:
            # 建立命令
            cmd = ['python', str(script_path)]
            if args:
                cmd.extend(args)

            # 執行腳本
            logger.info(f"執行命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 分鐘超時
            )

            # 儲存輸出
            if output_file:
                output_path = self.output_dir / output_file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                logger.info(f"輸出已儲存: {output_path}")

            if result.returncode == 0:
                logger.info(f"✅ {name} 執行成功")
                self.results.append({
                    'name': name,
                    'status': 'success',
                    'output_file': output_file
                })
                return True
            else:
                logger.error(f"❌ {name} 執行失敗")
                logger.error(f"錯誤訊息: {result.stderr}")
                self.results.append({
                    'name': name,
                    'status': 'failed',
                    'error': result.stderr
                })
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"❌ {name} 執行超時")
            self.results.append({
                'name': name,
                'status': 'timeout',
                'error': '執行超時'
            })
            return False
        except Exception as e:
            logger.error(f"❌ {name} 執行錯誤: {e}")
            self.results.append({
                'name': name,
                'status': 'error',
                'error': str(e)
            })
            return False

    def run_all(self):
        """執行所有分析"""
        logger.info(f"\n{'='*70}")
        logger.info(f"開始執行所有分析 - {self.date}")
        logger.info(f"{'='*70}\n")

        # 1. 趨勢追蹤 - 多頭選股
        self.run_analysis(
            name='趨勢追蹤 - 多頭選股',
            script_path=self.project_root / 'analysis/趨勢追蹤/find_bullish_stocks.py',
            output_file='01_趨勢追蹤_多頭選股.txt'
        )

        # 2. 回檔買進 - 回後買上漲型態
        self.run_analysis(
            name='回檔買進 - 回後買上漲型態',
            script_path=self.project_root / 'analysis/回檔買進/filter_recovery_stocks.py',
            args=['--date', self.date, '--min-conditions', '3'],
            output_file='02_回檔買進_回後買上漲型態.txt'
        )

        # 檢查是否有生成 CSV 檔案並複製到輸出目錄
        recovery_csv = self.project_root / f'analysis/results/recovery_stocks_{self.date}.csv'
        if recovery_csv.exists():
            target_csv = self.output_dir / f'02_回檔買進_回後買上漲型態_{self.date}.csv'
            shutil.copy(recovery_csv, target_csv)
            logger.info(f"CSV 檔案已複製: {target_csv}")

        # 3. 回檔買進 - 回檔買進選股器
        self.run_analysis(
            name='回檔買進 - 回檔買進選股器',
            script_path=self.project_root / 'analysis/回檔買進/pullback_buy_selector.py',
            output_file='03_回檔買進_回檔買進選股器.txt'
        )

        # 4. 多策略綜合 - 完整推薦報告
        logger.info(f"\n{'='*70}")
        logger.info(f"執行分析: 多策略綜合 - 完整推薦報告")
        logger.info(f"{'='*70}")

        recommend_script = self.project_root / 'analysis/多策略綜合/recommend_stocks_with_names.py'
        if recommend_script.exists():
            try:
                # 執行推薦腳本（它會自動生成到 ~/Downloads/股票推薦/）
                result = subprocess.run(
                    ['python', str(recommend_script)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    # 複製生成的檔案到輸出目錄
                    downloads_dir = Path.home() / 'Downloads' / '股票推薦'
                    if downloads_dir.exists():
                        for ext in ['.md', '.txt', '.csv']:
                            source_file = downloads_dir / f'股票推薦報告_{self.date}{ext}' if ext != '.csv' else downloads_dir / f'股票推薦清單_{self.date}.csv'
                            if source_file.exists():
                                target_name = f'04_多策略綜合_股票推薦{"清單" if ext == ".csv" else "報告"}{ext}'
                                target_file = self.output_dir / target_name
                                shutil.copy(source_file, target_file)
                                logger.info(f"檔案已複製: {target_file}")

                    logger.info(f"✅ 多策略綜合 - 完整推薦報告 執行成功")
                    self.results.append({
                        'name': '多策略綜合 - 完整推薦報告',
                        'status': 'success'
                    })
                else:
                    logger.error(f"❌ 多策略綜合 - 完整推薦報告 執行失敗")
                    self.results.append({
                        'name': '多策略綜合 - 完整推薦報告',
                        'status': 'failed',
                        'error': result.stderr
                    })
            except Exception as e:
                logger.error(f"❌ 多策略綜合 - 完整推薦報告 執行錯誤: {e}")
                self.results.append({
                    'name': '多策略綜合 - 完整推薦報告',
                    'status': 'error',
                    'error': str(e)
                })

    def generate_summary(self):
        """生成執行摘要"""
        summary_file = self.output_dir / '00_執行摘要.txt'

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"分析執行摘要 - {self.date}\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"輸出目錄: {self.output_dir}\n\n")

            # 統計
            total = len(self.results)
            success = sum(1 for r in self.results if r['status'] == 'success')
            failed = total - success

            f.write(f"執行統計:\n")
            f.write(f"  總數: {total}\n")
            f.write(f"  成功: {success}\n")
            f.write(f"  失敗: {failed}\n\n")

            # 詳細結果
            f.write(f"詳細結果:\n")
            f.write(f"{'-'*70}\n")

            for i, result in enumerate(self.results, 1):
                status_icon = '✅' if result['status'] == 'success' else '❌'
                f.write(f"{i}. {status_icon} {result['name']}\n")
                f.write(f"   狀態: {result['status']}\n")

                if result['status'] == 'success' and result.get('output_file'):
                    f.write(f"   輸出: {result['output_file']}\n")
                elif result['status'] != 'success' and result.get('error'):
                    error_msg = result['error'][:100] + '...' if len(result['error']) > 100 else result['error']
                    f.write(f"   錯誤: {error_msg}\n")

                f.write('\n')

        logger.info(f"\n執行摘要已儲存: {summary_file}")

        # 顯示摘要
        logger.info(f"\n{'='*70}")
        logger.info(f"執行完成摘要")
        logger.info(f"{'='*70}")
        logger.info(f"成功: {success}/{total}")
        logger.info(f"輸出目錄: {self.output_dir}")
        logger.info(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='執行所有分析腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--date',
        default=None,
        help='分析日期 (YYYY-MM-DD)，預設為今天'
    )

    parser.add_argument(
        '--output',
        default=None,
        help='輸出目錄，預設為 analysis/results/YYYY-MM-DD'
    )

    args = parser.parse_args()

    # 設定日期
    if args.date:
        date = args.date
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    # 設定輸出目錄
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = project_root / 'analysis' / 'results' / date

    # 執行分析
    runner = AnalysisRunner(date, output_dir)
    runner.setup_output_dir()
    runner.run_all()
    runner.generate_summary()


if __name__ == '__main__':
    main()
