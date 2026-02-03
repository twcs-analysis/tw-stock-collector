"""
證交所交易日曆服務

從證交所官方 API 取得交易日曆資訊，包含：
- 休市日期
- 特殊交易日（春節前最後交易日、春節後開始交易日等）
- 交易日判斷
- 交易日區間查詢

API: https://openapi.twse.com.tw/v1/news/holidaySchedule
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Set, List, Dict, Optional, Tuple
from pathlib import Path
import logging
import urllib3

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TradingCalendarService:
    """證交所交易日曆服務"""

    API_URL = "https://openapi.twse.com.tw/v1/news/holidaySchedule"
    CACHE_FILE = Path(__file__).parent / "calendar_cache.json"

    def __init__(self, use_cache: bool = True, timeout: int = 10):
        """
        初始化交易日曆服務

        Args:
            use_cache: 是否使用快取（預設 True）
            timeout: API 請求超時時間（秒）
        """
        self.use_cache = use_cache
        self.timeout = timeout
        self._holidays: Optional[Set[str]] = None
        self._special_days: Optional[Dict[str, List[Dict]]] = None
        self._cache_year: Optional[int] = None

    def fetch_from_api(self) -> Tuple[Set[str], Dict[str, List[Dict]]]:
        """
        從證交所 API 取得交易日曆資料

        Returns:
            tuple: (休市日集合, 特殊交易日字典)

        Raises:
            requests.RequestException: API 請求失敗
        """
        logger.info(f"從證交所 API 取得交易日曆: {self.API_URL}")

        try:
            response = requests.get(self.API_URL, timeout=self.timeout, verify=False)
            response.raise_for_status()
            data = response.json()

            holidays = set()
            special_days = {
                'start_trading': [],      # 開始交易日
                'last_trading': [],       # 最後交易日
                'settlement_only': []     # 僅結算交割日
            }

            for item in data:
                date_roc = item['Date']  # 民國年格式 "1150101"
                name = item['Name']
                weekday = item['Weekday']
                description = item.get('Description', '')

                # 轉換為西元年
                date_ad = self._convert_roc_to_ad(date_roc)

                # 分類處理
                if "開始交易" in name:
                    special_days['start_trading'].append({
                        'date': date_ad,
                        'name': name,
                        'weekday': weekday,
                        'description': description
                    })
                elif "最後交易" in name:
                    special_days['last_trading'].append({
                        'date': date_ad,
                        'name': name,
                        'weekday': weekday,
                        'description': description
                    })
                elif "無交易" in name:
                    holidays.add(date_ad)
                    special_days['settlement_only'].append({
                        'date': date_ad,
                        'name': name,
                        'weekday': weekday,
                        'description': description
                    })
                elif any(keyword in name for keyword in ['除夕', '春節', '紀念日', '節', '日']):
                    # 一般假日
                    holidays.add(date_ad)

            logger.info(f"✅ 成功取得 {len(holidays)} 個休市日")
            return holidays, special_days

        except requests.RequestException as e:
            logger.error(f"❌ 無法從證交所 API 取得交易日曆: {e}")
            raise

    def _convert_roc_to_ad(self, date_roc: str) -> str:
        """
        轉換民國年為西元年

        Args:
            date_roc: 民國年日期字串 "1150101"

        Returns:
            str: 西元年日期 "2026-01-01"
        """
        roc_year = int(date_roc[:3])
        month = date_roc[3:5]
        day = date_roc[5:7]
        year = roc_year + 1911
        return f"{year}-{month}-{day}"

    def load_from_cache(self) -> bool:
        """
        從快取檔案載入交易日曆

        Returns:
            bool: 是否成功載入
        """
        if not self.CACHE_FILE.exists():
            logger.debug("快取檔案不存在")
            return False

        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 檢查快取年份
            cache_year = cache_data.get('year')
            current_year = datetime.now().year

            if cache_year != current_year:
                logger.info(f"快取年份 ({cache_year}) 與當前年份 ({current_year}) 不符，需更新")
                return False

            # 載入資料
            self._holidays = set(cache_data.get('holidays', []))
            self._special_days = cache_data.get('special_days', {})
            self._cache_year = cache_year

            logger.info(f"✅ 從快取載入 {len(self._holidays)} 個休市日")
            return True

        except Exception as e:
            logger.warning(f"載入快取失敗: {e}")
            return False

    def save_to_cache(self) -> bool:
        """
        儲存交易日曆到快取檔案

        Returns:
            bool: 是否成功儲存
        """
        try:
            cache_data = {
                'year': datetime.now().year,
                'updated_at': datetime.now().isoformat(),
                'holidays': list(self._holidays) if self._holidays else [],
                'special_days': self._special_days if self._special_days else {}
            }

            # 確保目錄存在
            self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 交易日曆已儲存到快取: {self.CACHE_FILE}")
            return True

        except Exception as e:
            logger.warning(f"儲存快取失敗: {e}")
            return False

    def get_fallback_holidays(self) -> Set[str]:
        """
        取得備援休市日清單（當 API 和快取都無法使用時）

        Returns:
            set: 休市日期集合
        """
        logger.warning("使用備援休市日清單")

        # 2026 年休市日（需手動維護）
        fallback_2026 = {
            '2026-01-01',  # 元旦
            '2026-02-12', '2026-02-13',  # 春節調整（結算交割日）
            '2026-02-15', '2026-02-16', '2026-02-17',  # 春節
            '2026-02-18', '2026-02-19', '2026-02-20',
            '2026-02-27', '2026-02-28',  # 和平紀念日
            '2026-04-03', '2026-04-04', '2026-04-05', '2026-04-06',  # 清明
            '2026-05-01',  # 勞動節
            '2026-06-19',  # 端午
            '2026-09-25',  # 中秋
            '2026-09-28',  # 教師節
            '2026-10-09', '2026-10-10',  # 國慶
            '2026-10-25', '2026-10-26',  # 光復節
            '2026-12-25',  # 行憲紀念日
        }

        # TODO: 可以加入更多年份的備援資料

        current_year = datetime.now().year
        if current_year == 2026:
            return fallback_2026
        else:
            logger.warning(f"無 {current_year} 年的備援資料，僅返回空集合")
            return set()

    def refresh(self, force: bool = False) -> bool:
        """
        重新整理交易日曆資料

        Args:
            force: 是否強制從 API 更新（忽略快取）

        Returns:
            bool: 是否成功更新
        """
        current_year = datetime.now().year

        # 檢查是否需要更新
        if not force and self._cache_year == current_year and self._holidays is not None:
            logger.debug("使用記憶體中的交易日曆資料")
            return True

        # 1. 嘗試使用快取
        if self.use_cache and not force:
            if self.load_from_cache():
                return True

        # 2. 從 API 取得
        try:
            self._holidays, self._special_days = self.fetch_from_api()
            self._cache_year = current_year

            # 儲存到快取
            if self.use_cache:
                self.save_to_cache()

            return True

        except Exception as e:
            logger.error(f"從 API 取得交易日曆失敗: {e}")

            # 3. 使用備援清單
            self._holidays = self.get_fallback_holidays()
            self._special_days = {}

            return False

    def get_holidays(self) -> Set[str]:
        """
        取得休市日期集合

        Returns:
            set: 休市日期集合 {"2026-01-01", "2026-02-16", ...}
        """
        if self._holidays is None:
            self.refresh()

        return self._holidays or set()

    def get_special_days(self) -> Dict[str, List[Dict]]:
        """
        取得特殊交易日資訊

        Returns:
            dict: 特殊交易日字典
                {
                    'start_trading': [...],  # 開始交易日
                    'last_trading': [...],   # 最後交易日
                    'settlement_only': [...]  # 僅結算交割日
                }
        """
        if self._special_days is None:
            self.refresh()

        return self._special_days or {}

    def is_trading_day(self, date: str) -> bool:
        """
        判斷是否為交易日

        Args:
            date: 日期字串 "YYYY-MM-DD"

        Returns:
            bool: 是否為交易日
        """
        # 確保資料已載入
        if self._holidays is None:
            self.refresh()

        # 1. 解析日期
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"日期格式錯誤: {date}")
            return False

        # 2. 排除週末
        if dt.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False

        # 3. 排除休市日
        if date in self._holidays:
            return False

        return True

    def get_trading_days_in_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[str]:
        """
        取得指定日期範圍內的所有交易日

        Args:
            start_date: 起始日期 "YYYY-MM-DD"
            end_date: 結束日期 "YYYY-MM-DD"

        Returns:
            list: 交易日列表 ["2026-01-02", "2026-01-03", ...]
        """
        # 確保資料已載入
        if self._holidays is None:
            self.refresh()

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        trading_days = []
        current = start

        while current <= end:
            date_str = current.strftime('%Y-%m-%d')

            # 排除週末
            if current.weekday() < 5:
                # 排除休市日
                if date_str not in self._holidays:
                    trading_days.append(date_str)

            current += timedelta(days=1)

        return trading_days

    def get_latest_trading_day(self, from_date: Optional[str] = None) -> str:
        """
        取得最近的交易日（往前找）

        Args:
            from_date: 起始日期 "YYYY-MM-DD"（預設: 今天）

        Returns:
            str: 最近的交易日 "YYYY-MM-DD"
        """
        if from_date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(from_date, '%Y-%m-%d')

        # 往前找最近的交易日（最多找 14 天）
        for i in range(14):
            check_date = date - timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')

            if self.is_trading_day(date_str):
                return date_str

        # 如果 14 天內都沒有交易日（不太可能），回傳今天
        logger.warning("14 天內找不到交易日，回傳今天")
        return datetime.now().strftime('%Y-%m-%d')

    def get_next_trading_day(self, from_date: Optional[str] = None) -> str:
        """
        取得下一個交易日（往後找）

        Args:
            from_date: 起始日期 "YYYY-MM-DD"（預設: 今天）

        Returns:
            str: 下一個交易日 "YYYY-MM-DD"
        """
        if from_date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(from_date, '%Y-%m-%d')

        # 往後找下一個交易日（最多找 14 天）
        for i in range(1, 15):
            check_date = date + timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')

            if self.is_trading_day(date_str):
                return date_str

        # 如果 14 天內都沒有交易日（不太可能），回傳 14 天後
        logger.warning("14 天內找不到交易日")
        return (date + timedelta(days=14)).strftime('%Y-%m-%d')

    def get_trading_days_count(self, year: int) -> int:
        """
        取得指定年度的交易日數量

        Args:
            year: 年度

        Returns:
            int: 交易日數量
        """
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        trading_days = self.get_trading_days_in_range(start_date, end_date)
        return len(trading_days)

    def is_special_day(self, date: str) -> Optional[Dict]:
        """
        檢查是否為特殊交易日

        Args:
            date: 日期字串 "YYYY-MM-DD"

        Returns:
            dict or None: 如果是特殊日，返回資訊；否則返回 None
        """
        # 確保資料已載入
        if self._special_days is None:
            self.refresh()

        # 檢查所有類型的特殊日
        for day_type, days in self._special_days.items():
            for day_info in days:
                if day_info['date'] == date:
                    return {
                        'type': day_type,
                        **day_info
                    }

        return None

    def get_summary(self, year: Optional[int] = None) -> Dict:
        """
        取得交易日曆摘要資訊

        Args:
            year: 年度（預設: 當年度）

        Returns:
            dict: 摘要資訊
        """
        if year is None:
            year = datetime.now().year

        # 確保資料已載入
        if self._holidays is None:
            self.refresh()

        # 取得該年度的交易日
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        trading_days = self.get_trading_days_in_range(start_date, end_date)

        # 統計該年度的休市日
        year_holidays = [h for h in self._holidays if h.startswith(str(year))]

        # 統計特殊交易日
        special_count = {
            'start_trading': 0,
            'last_trading': 0,
            'settlement_only': 0
        }

        if self._special_days:
            for day_type, days in self._special_days.items():
                for day_info in days:
                    if day_info['date'].startswith(str(year)):
                        special_count[day_type] += 1

        return {
            'year': year,
            'trading_days_count': len(trading_days),
            'holidays_count': len(year_holidays),
            'weekdays_count': 260,  # 估算（52週 * 5天）
            'weekend_days': 104,    # 估算（52週 * 2天）
            'special_days': special_count,
            'first_trading_day': trading_days[0] if trading_days else None,
            'last_trading_day': trading_days[-1] if trading_days else None,
            'data_source': 'TWSE OpenAPI' if self._cache_year == year else 'Fallback'
        }
