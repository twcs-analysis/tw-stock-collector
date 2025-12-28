"""
融資融券資料驗證器
"""

from .base_validator import BaseValidator


class MarginValidator(BaseValidator):
    """融資融券資料驗證器"""

    DATA_TYPE = "margin"
    DATA_TYPE_NAME = "融資融券"
    MIN_RECORDS = 1500
    EXPECTED_RECORDS = 1815
    MAX_RECORDS = 2500

    REQUIRED_FIELDS = [
        'date',
        'stock_id',
        'stock_name',
        'margin_balance',
        'margin_change',
        'short_balance',
        'short_change',
        'type'
    ]

    def _validate_reasonableness(self):
        """合理性驗證"""
        if self.data is None or len(self.data) == 0:
            return

        # 3.1 數值範圍檢查 - 餘額必須 >= 0
        balance_fields = ['margin_balance', 'short_balance']

        for field in balance_fields:
            if field not in self.data.columns:
                continue

            invalid_balances = self.data[
                (self.data[field] < 0) |
                (self.data[field].isna())
            ]

            if len(invalid_balances) > 0:
                self.result.add_issue(
                    level="WARN",
                    category="reasonableness",
                    item=f"{field} 範圍",
                    message=f"{len(invalid_balances)} 筆 {field} 資料異常 (< 0 或 null，可能為不允許融資融券的股票)",
                    details={'count': len(invalid_balances)}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="reasonableness",
                    item=f"{field} 範圍",
                    message=f"所有 {field} 資料正常"
                )

        # 3.2 變化量合理性檢查
        # 變化量的絕對值不應該過大（例如超過餘額的2倍）
        if 'margin_balance' in self.data.columns and 'margin_change' in self.data.columns:
            # 過濾掉餘額為0的情況
            non_zero_margin = self.data[self.data['margin_balance'] > 0]
            if len(non_zero_margin) > 0:
                large_changes = non_zero_margin[
                    abs(non_zero_margin['margin_change']) > (non_zero_margin['margin_balance'] * 2)
                ]

                if len(large_changes) > 0:
                    self.result.add_issue(
                        level="WARN",
                        category="reasonableness",
                        item="融資變化量",
                        message=f"{len(large_changes)} 筆融資變化量異常大 (超過餘額2倍)",
                        details={'count': len(large_changes)}
                    )
                else:
                    self.result.add_issue(
                        level="PASS",
                        category="reasonableness",
                        item="融資變化量",
                        message="融資變化量正常"
                    )

        if 'short_balance' in self.data.columns and 'short_change' in self.data.columns:
            non_zero_short = self.data[self.data['short_balance'] > 0]
            if len(non_zero_short) > 0:
                large_changes = non_zero_short[
                    abs(non_zero_short['short_change']) > (non_zero_short['short_balance'] * 2)
                ]

                if len(large_changes) > 0:
                    self.result.add_issue(
                        level="WARN",
                        category="reasonableness",
                        item="融券變化量",
                        message=f"{len(large_changes)} 筆融券變化量異常大 (超過餘額2倍)",
                        details={'count': len(large_changes)}
                    )
                else:
                    self.result.add_issue(
                        level="PASS",
                        category="reasonableness",
                        item="融券變化量",
                        message="融券變化量正常"
                    )
