#!/usr/bin/env python3.11
"""
批次 MP3 轉逐字稿工具

功能：
1. 批次掃描指定目錄下所有 2026-* 子目錄的 mp3 檔案
2. 使用 whisper-cpp 將 mp3 轉換為中文逐字稿
3. 逐字稿保存在各自的原始目錄下
4. 轉換前檢查是否已存在逐字稿，避免重複轉換
5. 顯示進度並記錄錯誤

使用方式：
    python3.11 scripts/media-tools/batch_mp3_to_transcript.py <目錄路徑>

範例：
    # 批次轉換所有 2026 年的 mp3 檔案
    python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline

    # 使用不同的 Whisper 模型
    python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline --model small

    # 強制重新轉換（忽略已存在的逐字稿）
    python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline --force

依賴套件：
    - whisper-cpp（需預先安裝：brew install whisper-cpp）
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil


class BatchMP3ToTranscript:
    """批次 MP3 轉逐字稿處理器"""

    def __init__(self, base_dir: str, model: str = "base", force: bool = False, auto_confirm: bool = False):
        """
        初始化處理器

        Args:
            base_dir: 基礎目錄路徑
            model: Whisper 模型（tiny, base, small, medium, large）
            force: 是否強制重新轉換（忽略已存在的逐字稿）
            auto_confirm: 是否自動確認，跳過互動式提示
        """
        self.base_dir = Path(base_dir)
        self.model = model
        self.force = force
        self.auto_confirm = auto_confirm

        # 檢查目錄是否存在
        if not self.base_dir.exists():
            raise FileNotFoundError(f"目錄不存在: {base_dir}")

        # 統計資訊
        self.total_files = 0
        self.processed_files = 0
        self.skipped_files = 0
        self.failed_files = []

    def check_dependencies(self) -> bool:
        """檢查必要的依賴套件"""
        print("🔍 檢查依賴套件...")

        # 檢查 whisper-cli
        if not shutil.which("whisper-cli"):
            print("❌ 找不到 whisper-cli，請先安裝：brew install whisper-cpp")
            return False
        print("✅ whisper-cpp 已安裝")

        # 檢查模型檔案是否存在
        model_path = f"/opt/homebrew/share/whisper-cpp/models/ggml-{self.model}.bin"
        if not os.path.exists(model_path):
            print(f"❌ 找不到模型檔案: {model_path}")
            print(f"請確認模型已安裝，或選擇其他模型")
            return False
        print(f"✅ 模型檔案存在: {model_path}")

        return True

    def find_mp3_files(self) -> list:
        """
        搜尋所有 2026-* 目錄下的 mp3 檔案

        Returns:
            list: mp3 檔案路徑列表
        """
        print(f"\n📂 搜尋 {self.base_dir} 下的 2026-* 目錄...")

        mp3_files = []

        # 搜尋所有 2026-* 目錄
        for year_dir in sorted(self.base_dir.glob("2026-*")):
            if year_dir.is_dir():
                # 搜尋該目錄下的所有 mp3 檔案
                for mp3_file in sorted(year_dir.glob("*.mp3")):
                    # 過濾 macOS 的資源分支檔案（以 ._ 開頭）
                    if not mp3_file.name.startswith("._"):
                        mp3_files.append(mp3_file)

        self.total_files = len(mp3_files)
        print(f"✅ 找到 {self.total_files} 個 mp3 檔案")

        return mp3_files

    def check_transcript_exists(self, mp3_path: Path) -> bool:
        """
        檢查逐字稿是否已存在

        Args:
            mp3_path: mp3 檔案路徑

        Returns:
            bool: 是否已存在逐字稿
        """
        txt_path = mp3_path.with_suffix(".txt")
        return txt_path.exists()

    def transcribe_audio(self, mp3_path: Path) -> bool:
        """
        使用 whisper-cpp 將 mp3 轉換為中文逐字稿

        Args:
            mp3_path: mp3 檔案路徑

        Returns:
            bool: 是否成功
        """
        try:
            # whisper-cli 指令
            model_path = f"/opt/homebrew/share/whisper-cpp/models/ggml-{self.model}.bin"
            cmd = [
                "whisper-cli",
                "-m", model_path,  # 模型路徑
                "-l", "zh",  # 中文
                "-f", str(mp3_path),  # 輸入檔案
                "-otxt",  # 輸出文字格式
            ]

            # 執行轉換
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd=mp3_path.parent  # 在 mp3 所在目錄執行，讓輸出檔案在同目錄
            )

            # 檢查是否產生逐字稿檔案
            txt_path = mp3_path.with_suffix(".txt")
            if txt_path.exists():
                return True
            else:
                print(f"    ⚠️  未產生逐字稿檔案: {txt_path}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"    ❌ 轉換失敗: {e.stderr}")
            return False
        except Exception as e:
            print(f"    ❌ 發生錯誤: {str(e)}")
            return False

    def process_file(self, mp3_path: Path, index: int) -> bool:
        """
        處理單一 mp3 檔案

        Args:
            mp3_path: mp3 檔案路徑
            index: 檔案索引（用於顯示進度）

        Returns:
            bool: 是否成功
        """
        # 顯示進度
        print(f"\n[{index}/{self.total_files}] 處理中: {mp3_path.name}")
        print(f"  目錄: {mp3_path.parent}")

        # 檢查逐字稿是否已存在
        if not self.force and self.check_transcript_exists(mp3_path):
            print(f"  ⏭️  逐字稿已存在，跳過")
            self.skipped_files += 1
            return True

        # 轉換為逐字稿
        print(f"  🎤 開始轉換（模型: {self.model}）...")
        success = self.transcribe_audio(mp3_path)

        if success:
            print(f"  ✅ 轉換完成")
            self.processed_files += 1
            return True
        else:
            print(f"  ❌ 轉換失敗")
            self.failed_files.append(str(mp3_path))
            return False

    def process_all(self):
        """批次處理所有 mp3 檔案"""
        print("=" * 80)
        print("🎬 批次 MP3 轉逐字稿工具")
        print("=" * 80)

        # 檢查依賴
        if not self.check_dependencies():
            sys.exit(1)

        # 搜尋 mp3 檔案
        mp3_files = self.find_mp3_files()

        if not mp3_files:
            print("\n⚠️  沒有找到任何 mp3 檔案")
            return

        # 確認是否繼續
        print(f"\n準備處理 {self.total_files} 個 mp3 檔案")
        print(f"模型: {self.model}")
        print(f"強制重新轉換: {'是' if self.force else '否'}")

        if not self.auto_confirm:
            print("\n按 Enter 繼續，或 Ctrl+C 取消...")
            input()
        else:
            print("\n自動確認模式，開始處理...")

        # 記錄開始時間
        start_time = datetime.now()

        # 批次處理
        print("\n" + "=" * 80)
        print("開始批次處理")
        print("=" * 80)

        for index, mp3_path in enumerate(mp3_files, start=1):
            try:
                self.process_file(mp3_path, index)
            except KeyboardInterrupt:
                print("\n\n⚠️  使用者中斷")
                break
            except Exception as e:
                print(f"\n❌ 處理失敗: {str(e)}")
                self.failed_files.append(str(mp3_path))

        # 記錄結束時間
        end_time = datetime.now()
        duration = end_time - start_time

        # 顯示統計結果
        self.print_summary(duration)

    def print_summary(self, duration):
        """顯示處理結果統計"""
        print("\n" + "=" * 80)
        print("📊 處理結果統計")
        print("=" * 80)
        print(f"總檔案數: {self.total_files}")
        print(f"成功轉換: {self.processed_files}")
        print(f"跳過檔案: {self.skipped_files}")
        print(f"失敗檔案: {len(self.failed_files)}")
        print(f"總耗時: {duration}")

        if self.failed_files:
            print("\n❌ 失敗的檔案:")
            for failed_file in self.failed_files:
                print(f"  - {failed_file}")

        print("\n" + "=" * 80)
        if self.failed_files:
            print("⚠️  部分檔案處理失敗")
        else:
            print("✅ 全部處理完成！")
        print("=" * 80)


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="批次 MP3 轉逐字稿工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 批次轉換所有 2026 年的 mp3 檔案
  %(prog)s /Users/jasonhuang/yt-video/yt-moneyline

  # 使用不同的 Whisper 模型
  %(prog)s /Users/jasonhuang/yt-video/yt-moneyline --model small

  # 強制重新轉換（忽略已存在的逐字稿）
  %(prog)s /Users/jasonhuang/yt-video/yt-moneyline --force

可用的 Whisper 模型：
  - tiny: 最快，準確度較低
  - base: 平衡速度與準確度（預設）
  - small: 較慢，準確度較高
  - medium: 更慢，準確度更高
  - large: 最慢，最高準確度
        """
    )

    parser.add_argument(
        "base_dir",
        help="基礎目錄路徑（包含 2026-* 子目錄）"
    )

    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型（預設: base）"
    )

    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="強制重新轉換（忽略已存在的逐字稿）"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="自動確認，跳過互動式提示"
    )

    args = parser.parse_args()

    try:
        # 執行批次處理
        processor = BatchMP3ToTranscript(
            base_dir=args.base_dir,
            model=args.model,
            force=args.force,
            auto_confirm=args.yes
        )
        processor.process_all()

    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
