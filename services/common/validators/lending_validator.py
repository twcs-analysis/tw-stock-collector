"""
借券賣出資料驗證器
"""

from .base_validator import BaseValidator


class LendingValidator(BaseValidator):
    """借券賣出資料驗證器"""

    DATA_TYPE = "lending"
    DATA_TYPE_NAME = "借券賣出"
    MIN_RECORDS = 800
    EXPECTED_RECORDS = 1046
    MAX_RECORDS = 1500

    REQUIRED_FIELDS = [
        'date',
        'stock_id',
        'stock_name',
        'lending_balance',
        'lending_change',
        'type'
    ]

    def _validate_reasonableness(self):
        """合理性驗證"""
        if self.data is None or len(self.data) == 0:
            return

        # 3.1 數值範圍檢查 - 餘額必須 >= 0
        if 'lending_balance' in self.data.columns:
            invalid_balances = self.data[
                (self.data['lending_balance'] < 0) |
                (self.data['lending_balance'].isna())
            ]

            if len(invalid_balances) > 0:
                self.result.add_issue(
                    level="FAIL",
                    category="reasonableness",
                    item="借券餘額範圍",
                    message=f"{len(invalid_balances)} 筆借券餘額資料異常 (< 0 或 null)",
                    details={'count': len(invalid_balances)}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="reasonableness",
                    item="借券餘額範圍",
                    message="所有借券餘額資料正常"
                )

        # 3.2 變化量合理性檢查
        if 'lending_balance' in self.data.columns and 'lending_change' in self.data.columns:
            # 過濾掉餘額為0的情況
            non_zero_lending = self.data[self.data['lending_balance'] > 0]
            if len(non_zero_lending) > 0:
                large_changes = non_zero_lending[
                    abs(non_zero_lending['lending_change']) > (non_zero_lending['lending_balance'] * 2)
                ]

                if len(large_changes) > 0:
                    self.result.add_issue(
                        level="WARN",
                        category="reasonableness",
                        item="借券變化量",
                        message=f"{len(large_changes)} 筆借券變化量異常大 (超過餘額2倍)",
                        details={'count': len(large_changes)}
                    )
                else:
                    self.result.add_issue(
                        level="PASS",
                        category="reasonableness",
                        item="借券變化量",
                        message="借券變化量正常"
                    )
