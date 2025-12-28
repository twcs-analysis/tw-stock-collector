"""
三大法人資料驗證器
"""

from .base_validator import BaseValidator


class InstitutionalValidator(BaseValidator):
    """三大法人資料驗證器"""

    DATA_TYPE = "institutional"
    DATA_TYPE_NAME = "三大法人"
    MIN_RECORDS = 800
    EXPECTED_RECORDS = 1027
    MAX_RECORDS = 1500

    REQUIRED_FIELDS = [
        'date',
        'stock_id',
        'stock_name',
        'foreign_buy',
        'foreign_sell',
        'foreign_net',
        'trust_buy',
        'trust_sell',
        'trust_net',
        'dealer_buy',
        'dealer_sell',
        'dealer_net',
        'type'
    ]

    def _validate_reasonableness(self):
        """合理性驗證"""
        if self.data is None or len(self.data) == 0:
            return

        # 3.1 數值非負檢查 - 買賣金額必須 >= 0
        amount_fields = [
            'foreign_buy', 'foreign_sell',
            'trust_buy', 'trust_sell',
            'dealer_buy', 'dealer_sell'
        ]

        for field in amount_fields:
            if field not in self.data.columns:
                continue

            invalid_amounts = self.data[
                (self.data[field] < 0) |
                (self.data[field].isna())
            ]

            if len(invalid_amounts) > 0:
                self.result.add_issue(
                    level="FAIL",
                    category="reasonableness",
                    item=f"{field} 範圍",
                    message=f"{len(invalid_amounts)} 筆 {field} 資料異常 (< 0 或 null)",
                    details={'count': len(invalid_amounts)}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="reasonableness",
                    item=f"{field} 範圍",
                    message=f"所有 {field} 資料正常"
                )

        # 3.2 邏輯一致性檢查 - 淨額 = 買入 - 賣出
        tolerance = 1000  # 允許 1000 元誤差

        institutional_types = [
            ('foreign', '外資'),
            ('trust', '投信'),
            ('dealer', '自營商')
        ]

        for inst_type, inst_name in institutional_types:
            buy_col = f'{inst_type}_buy'
            sell_col = f'{inst_type}_sell'
            net_col = f'{inst_type}_net'

            if all(col in self.data.columns for col in [buy_col, sell_col, net_col]):
                calculated_net = self.data[buy_col] - self.data[sell_col]
                diff = abs(self.data[net_col] - calculated_net)

                inconsistent = diff > tolerance

                if inconsistent.sum() > 0:
                    self.result.add_issue(
                        level="WARN",
                        category="reasonableness",
                        item=f"{inst_name}淨額計算",
                        message=f"{inconsistent.sum()} 筆 {inst_name}淨額計算不一致 (誤差 > {tolerance})",
                        details={'count': inconsistent.sum()}
                    )
                else:
                    self.result.add_issue(
                        level="PASS",
                        category="reasonableness",
                        item=f"{inst_name}淨額計算",
                        message=f"所有 {inst_name}淨額計算正確"
                    )
