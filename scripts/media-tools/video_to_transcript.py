#!/usr/bin/env python3.11
"""
影音轉文字腳本工具

功能：
1. 使用 yt-dlp 下載影音網址，轉換為 mp3 格式
2. 使用 whisper-cpp 將 mp3 轉換為中文逐字稿
3. 儲存逐字稿到 data/transcripts/{日期}/{檔名}.txt

使用方式：
    python3.11 scripts/media-tools/video_to_transcript.py <影音網址> [選項]

範例：
    # 基本使用
    python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx"

    # 指定輸出檔名
    python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx" --output "meeting_notes"

    # 使用不同的 Whisper 模型
    python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx" --model large

依賴套件：
    - yt-dlp（需預先安裝）
    - whisper-cpp（需預先安裝）
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil


class VideoToTranscriptConverter:
    """影音轉文字轉換器"""

    def __init__(self, url: str, output_name: str = None, model: str = "base"):
        """
        初始化轉換器

        Args:
            url: 影音網址
            output_name: 輸出檔名（不含副檔名），預設使用影片標題
            model: Whisper 模型（tiny, base, small, medium, large）
        """
        self.url = url
        self.output_name = output_name
        self.model = model

        # 取得專案根目錄
        self.project_root = Path(__file__).parent.parent.parent

        # 建立日期目錄
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.transcript_dir = self.project_root / "data" / "transcripts" / self.today
        self.transcript_dir.mkdir(parents=True, exist_ok=True)

        # 暫存目錄
        self.temp_dir = self.project_root / "data" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def check_dependencies(self):
        """檢查必要的依賴套件"""
        print("🔍 檢查依賴套件...")

        # 檢查 yt-dlp
        if not shutil.which("yt-dlp"):
            print("❌ 找不到 yt-dlp，請先安裝：brew install yt-dlp")
            return False
        print("✅ yt-dlp 已安裝")

        # 檢查 whisper-cli
        if not shutil.which("whisper-cli"):
            print("❌ 找不到 whisper-cli，請先安裝：brew install whisper-cpp")
            return False
        print("✅ whisper-cpp 已安裝")

        return True

    def download_audio(self) -> str:
        """
        使用 yt-dlp 下載影音並轉換為 mp3

        Returns:
            str: mp3 檔案路徑
        """
        print(f"\n📥 下載影音: {self.url}")

        # 如果有指定輸出名稱，使用指定名稱；否則使用影片標題
        if self.output_name:
            output_template = str(self.temp_dir / f"{self.output_name}.%(ext)s")
        else:
            output_template = str(self.temp_dir / "%(title)s.%(ext)s")

        try:
            # yt-dlp 指令
            cmd = [
                "yt-dlp",
                "-x",  # 只下載音訊
                "--audio-format", "mp3",  # 轉換為 mp3
                "--audio-quality", "0",  # 最高音質
                "-o", output_template,  # 輸出路徑模板
                self.url
            ]

            print(f"執行指令: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)

            # 找到下載的 mp3 檔案
            mp3_files = list(self.temp_dir.glob("*.mp3"))
            if not mp3_files:
                raise FileNotFoundError("找不到下載的 mp3 檔案")

            mp3_path = str(mp3_files[-1])  # 取最新的檔案
            print(f"✅ 下載完成: {mp3_path}")

            return mp3_path

        except subprocess.CalledProcessError as e:
            print(f"❌ 下載失敗: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ 發生錯誤: {str(e)}")
            raise

    def transcribe_audio(self, mp3_path: str) -> str:
        """
        使用 whisper-cpp 將 mp3 轉換為中文逐字稿

        Args:
            mp3_path: mp3 檔案路徑

        Returns:
            str: 逐字稿文字內容
        """
        print(f"\n🎤 轉換為逐字稿 (模型: {self.model})...")

        try:
            # whisper-cli 指令
            cmd = [
                "whisper-cli",
                "-m", f"/opt/homebrew/share/whisper-cpp/models/ggml-{self.model}.bin",  # 模型路徑
                "-l", "zh",  # 中文
                "-f", mp3_path,  # 輸入檔案
                "-otxt",  # 輸出文字格式
            ]

            print(f"執行指令: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # whisper-cli 會輸出到同目錄的 .txt 檔案
            txt_path = mp3_path.replace(".mp3", ".txt")

            if not os.path.exists(txt_path):
                # 如果沒有產生 txt 檔案，嘗試從 stdout 取得
                transcript = result.stdout
            else:
                with open(txt_path, "r", encoding="utf-8") as f:
                    transcript = f.read()
                # 清理暫存的 txt 檔案
                os.remove(txt_path)

            print("✅ 轉換完成")

            return transcript

        except subprocess.CalledProcessError as e:
            print(f"❌ 轉換失敗: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ 發生錯誤: {str(e)}")
            raise

    def save_transcript(self, transcript: str, mp3_path: str):
        """
        儲存逐字稿到檔案

        Args:
            transcript: 逐字稿內容
            mp3_path: mp3 檔案路徑（用於取得檔名）
        """
        # 取得檔名（不含副檔名）
        base_name = Path(mp3_path).stem

        # 輸出檔案路徑
        output_path = self.transcript_dir / f"{base_name}.txt"

        print(f"\n💾 儲存逐字稿: {output_path}")

        # 寫入檔案
        with open(output_path, "w", encoding="utf-8") as f:
            # 加入 metadata
            f.write(f"# 逐字稿 - {base_name}\n")
            f.write(f"# 來源網址: {self.url}\n")
            f.write(f"# 轉換日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Whisper 模型: {self.model}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            f.write(transcript)

        print(f"✅ 逐字稿已儲存")
        print(f"📄 檔案位置: {output_path}")

    def cleanup(self, mp3_path: str):
        """清理暫存檔案"""
        print("\n🧹 清理暫存檔案...")
        try:
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
                print(f"✅ 已刪除: {mp3_path}")
        except Exception as e:
            print(f"⚠️  清理失敗: {str(e)}")

    def convert(self):
        """執行完整的轉換流程"""
        print("=" * 80)
        print("🎬 影音轉文字腳本工具")
        print("=" * 80)

        # 檢查依賴
        if not self.check_dependencies():
            sys.exit(1)

        mp3_path = None
        try:
            # 1. 下載音訊
            mp3_path = self.download_audio()

            # 2. 轉換為逐字稿
            transcript = self.transcribe_audio(mp3_path)

            # 3. 儲存逐字稿
            self.save_transcript(transcript, mp3_path)

            print("\n" + "=" * 80)
            print("✅ 轉換完成！")
            print("=" * 80)

        except Exception as e:
            print("\n" + "=" * 80)
            print(f"❌ 轉換失敗: {str(e)}")
            print("=" * 80)
            sys.exit(1)

        finally:
            # 清理暫存檔案
            if mp3_path:
                self.cleanup(mp3_path)


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="影音轉文字腳本工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 基本使用
  %(prog)s "https://www.youtube.com/watch?v=xxx"

  # 指定輸出檔名
  %(prog)s "https://www.youtube.com/watch?v=xxx" --output "meeting_notes"

  # 使用不同的 Whisper 模型
  %(prog)s "https://www.youtube.com/watch?v=xxx" --model large

可用的 Whisper 模型：
  - tiny: 最快，準確度較低
  - base: 平衡速度與準確度（預設）
  - small: 較慢，準確度較高
  - medium: 更慢，準確度更高
  - large: 最慢，最高準確度
        """
    )

    parser.add_argument(
        "url",
        help="影音網址（支援 YouTube、Vimeo 等 yt-dlp 支援的網站）"
    )

    parser.add_argument(
        "-o", "--output",
        help="輸出檔名（不含副檔名），預設使用影片標題"
    )

    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型（預設: base）"
    )

    args = parser.parse_args()

    # 執行轉換
    converter = VideoToTranscriptConverter(
        url=args.url,
        output_name=args.output,
        model=args.model
    )
    converter.convert()


if __name__ == "__main__":
    main()
