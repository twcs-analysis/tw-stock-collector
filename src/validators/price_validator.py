"""
價格資料驗證器
"""

from .base_validator import BaseValidator


class PriceValidator(BaseValidator):
    """價格資料驗證器"""

    DATA_TYPE = "price"
    DATA_TYPE_NAME = "價格資料"
    MIN_RECORDS = 1500
    EXPECTED_RECORDS = 1946
    MAX_RECORDS = 2500

    REQUIRED_FIELDS = [
        'date',
        'stock_id',
        'stock_name',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'type'
    ]

    def _validate_reasonableness(self):
        """合理性驗證"""
        if self.data is None or len(self.data) == 0:
            return

        # 3.1 數值範圍檢查
        price_fields = ['open', 'high', 'low', 'close']
        out_of_range_records = []

        for field in price_fields:
            if field not in self.data.columns:
                continue

            # 檢查價格範圍 (0.01 ~ 20000)
            # 注意：台股有高價股(如台積電),上限設為 20000
            invalid_prices = self.data[
                (self.data[field] < 0.01) |
                (self.data[field] > 20000) |
                (self.data[field].isna())
            ]

            if len(invalid_prices) > 0:
                out_of_range_records.extend(
                    invalid_prices[['stock_id', 'stock_name', field]].to_dict('records')
                )

        if len(out_of_range_records) > 0:
            self.result.add_issue(
                level="WARN",
                category="reasonableness",
                item="價格範圍",
                message=f"{len(out_of_range_records)} 筆價格資料超出合理範圍 (0.01 ~ 20,000)",
                details={'records': out_of_range_records[:10]}  # 只記錄前10筆
            )
        else:
            self.result.add_issue(
                level="PASS",
                category="reasonableness",
                item="價格範圍",
                message="所有價格資料在合理範圍內"
            )

        # 檢查成交量範圍 (>= 0)
        if 'volume' in self.data.columns:
            invalid_volumes = self.data[
                (self.data['volume'] < 0) |
                (self.data['volume'].isna())
            ]

            if len(invalid_volumes) > 0:
                self.result.add_issue(
                    level="FAIL",
                    category="reasonableness",
                    item="成交量範圍",
                    message=f"{len(invalid_volumes)} 筆成交量資料異常 (< 0 或 null)",
                    details={'count': len(invalid_volumes)}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="reasonableness",
                    item="成交量範圍",
                    message="所有成交量資料正常"
                )

        # 3.2 邏輯一致性檢查
        logic_checks = [
            ('high >= low', self.data['high'] >= self.data['low']),
            ('high >= open', self.data['high'] >= self.data['open']),
            ('high >= close', self.data['high'] >= self.data['close']),
            ('low <= open', self.data['low'] <= self.data['open']),
            ('low <= close', self.data['low'] <= self.data['close']),
        ]

        for check_name, check_result in logic_checks:
            passed = check_result.sum()
            total = len(self.data)
            failed = total - passed

            if failed > 0:
                self.result.add_issue(
                    level="FAIL",
                    category="reasonableness",
                    item=f"邏輯檢查: {check_name}",
                    message=f"{failed} 筆資料不符合邏輯 {check_name}",
                    details={'passed': passed, 'failed': failed, 'total': total}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="reasonableness",
                    item=f"邏輯檢查: {check_name}",
                    message=f"所有資料符合邏輯 {check_name}"
                )
