"""
基礎驗證器類別

提供資料驗證的統一介面與報告生成功能
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ValidationIssue:
    """驗證問題"""
    level: str  # PASS, WARN, FAIL
    category: str  # structure, completeness, reasonableness
    item: str  # 驗證項目
    message: str  # 問題描述
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """驗證結果"""
    data_type: str
    date: str
    file_path: str
    validation_time: str

    # 驗證統計
    total_checks: int = 0
    passed_checks: int = 0
    warned_checks: int = 0
    failed_checks: int = 0

    # 資料統計
    total_records: int = 0
    twse_records: int = 0
    tpex_records: int = 0
    file_size: int = 0

    # 問題清單
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """計算準確率"""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    @property
    def grade(self) -> str:
        """評分等級"""
        acc = self.accuracy
        if acc >= 99.5:
            return "A+"
        elif acc >= 95.0:
            return "A"
        elif acc >= 90.0:
            return "B"
        elif acc >= 85.0:
            return "C"
        elif acc >= 80.0:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        """驗證狀態"""
        if self.failed_checks > 0:
            return "FAIL"
        elif self.warned_checks > 0:
            return "WARN"
        else:
            return "PASS"

    def add_issue(self, level: str, category: str, item: str, message: str,
                  details: Optional[Dict] = None):
        """新增驗證問題"""
        self.issues.append(ValidationIssue(
            level=level,
            category=category,
            item=item,
            message=message,
            details=details
        ))

        # 更新統計
        self.total_checks += 1
        if level == "PASS":
            self.passed_checks += 1
        elif level == "WARN":
            self.warned_checks += 1
        elif level == "FAIL":
            self.failed_checks += 1


class BaseValidator(ABC):
    """基礎驗證器"""

    # 資料類型相關配置（子類別需要覆寫）
    DATA_TYPE = ""
    DATA_TYPE_NAME = ""
    MIN_RECORDS = 0
    EXPECTED_RECORDS = 0
    MAX_RECORDS = 0

    # 必要欄位（子類別需要覆寫）
    REQUIRED_FIELDS = []

    def __init__(self, file_path: str):
        """
        Args:
            file_path: 資料檔案路徑
        """
        self.file_path = Path(file_path)
        self.result = None
        self.data = None
        self.metadata = None

    def validate(self) -> ValidationResult:
        """
        執行完整驗證流程

        Returns:
            ValidationResult: 驗證結果
        """
        # 初始化驗證結果
        date_str = self.file_path.stem  # 檔名即為日期
        self.result = ValidationResult(
            data_type=self.DATA_TYPE,
            date=date_str,
            file_path=str(self.file_path),
            validation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        try:
            # 1. 結構驗證
            self._validate_structure()

            # 2. 完整性驗證
            self._validate_completeness()

            # 3. 合理性驗證
            self._validate_reasonableness()

            logger.info(f"驗證完成: {self.file_path.name} - {self.result.status} ({self.result.grade})")

        except Exception as e:
            logger.error(f"驗證失敗: {e}", exc_info=True)
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="驗證執行",
                message=f"驗證過程發生錯誤: {str(e)}"
            )

        return self.result

    def _validate_structure(self):
        """結構驗證"""
        # 1.1 檔案存在性檢查
        if not self.file_path.exists():
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="檔案存在性",
                message="檔案不存在"
            )
            return
        else:
            self.result.add_issue(
                level="PASS",
                category="structure",
                item="檔案存在性",
                message="檔案存在"
            )

        # 1.2 JSON 格式檢查
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            self.result.add_issue(
                level="PASS",
                category="structure",
                item="JSON 格式",
                message="JSON 格式有效"
            )
        except json.JSONDecodeError as e:
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="JSON 格式",
                message=f"JSON 格式錯誤: {str(e)}"
            )
            return

        # 1.3 Metadata 檢查
        if 'metadata' not in raw_data:
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="Metadata 存在",
                message="缺少 metadata 欄位"
            )
            return

        self.metadata = raw_data['metadata']

        # 檢查 metadata 必要欄位
        required_meta_fields = ['date', 'total_count', 'source']
        missing_fields = [f for f in required_meta_fields if f not in self.metadata]

        if missing_fields:
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="Metadata 欄位",
                message=f"Metadata 缺少欄位: {', '.join(missing_fields)}"
            )
        else:
            self.result.add_issue(
                level="PASS",
                category="structure",
                item="Metadata 欄位",
                message="Metadata 欄位完整"
            )

        # 1.4 Data 檢查
        if 'data' not in raw_data:
            self.result.add_issue(
                level="FAIL",
                category="structure",
                item="Data 存在",
                message="缺少 data 欄位"
            )
            return

        self.data = pd.DataFrame(raw_data['data'])

        # 更新資料統計
        self.result.total_records = len(self.data)
        self.result.file_size = self.file_path.stat().st_size

        if 'type' in self.data.columns:
            self.result.twse_records = len(self.data[self.data['type'] == 'twse'])
            self.result.tpex_records = len(self.data[self.data['type'] == 'tpex'])

    def _validate_completeness(self):
        """完整性驗證"""
        if self.data is None:
            return

        # 2.1 資料筆數檢查
        record_count = len(self.data)

        if record_count < self.MIN_RECORDS:
            self.result.add_issue(
                level="FAIL",
                category="completeness",
                item="資料筆數",
                message=f"資料筆數過少: {record_count} < {self.MIN_RECORDS}",
                details={'count': record_count, 'min': self.MIN_RECORDS}
            )
        elif record_count > self.MAX_RECORDS:
            self.result.add_issue(
                level="FAIL",
                category="completeness",
                item="資料筆數",
                message=f"資料筆數過多: {record_count} > {self.MAX_RECORDS}",
                details={'count': record_count, 'max': self.MAX_RECORDS}
            )
        else:
            # 檢查是否偏離預期值 ±20%
            expected = self.EXPECTED_RECORDS
            lower_bound = expected * 0.8
            upper_bound = expected * 1.2

            if record_count < lower_bound or record_count > upper_bound:
                deviation = abs(record_count - expected) / expected * 100
                self.result.add_issue(
                    level="WARN",
                    category="completeness",
                    item="資料筆數",
                    message=f"資料筆數偏離預期值 {deviation:.1f}%: {record_count} (預期: {expected})",
                    details={'count': record_count, 'expected': expected, 'deviation': deviation}
                )
            else:
                self.result.add_issue(
                    level="PASS",
                    category="completeness",
                    item="資料筆數",
                    message=f"資料筆數正常: {record_count}",
                    details={'count': record_count}
                )

        # 2.2 必要欄位檢查
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in self.data.columns]

        if missing_fields:
            self.result.add_issue(
                level="FAIL",
                category="completeness",
                item="必要欄位",
                message=f"缺少必要欄位: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields}
            )
        else:
            # 檢查每個欄位的完整性
            field_completeness = {}
            all_complete = True

            for field in self.REQUIRED_FIELDS:
                non_null_count = self.data[field].notna().sum()
                completeness = non_null_count / len(self.data) * 100
                field_completeness[field] = completeness

                if completeness < 100:
                    all_complete = False

            if all_complete:
                self.result.add_issue(
                    level="PASS",
                    category="completeness",
                    item="必要欄位",
                    message="所有必要欄位完整",
                    details={'fields': field_completeness}
                )
            else:
                incomplete_fields = {k: v for k, v in field_completeness.items() if v < 100}
                self.result.add_issue(
                    level="WARN",
                    category="completeness",
                    item="必要欄位",
                    message=f"部分欄位有缺值: {incomplete_fields}",
                    details={'fields': field_completeness}
                )

    @abstractmethod
    def _validate_reasonableness(self):
        """合理性驗證（子類別實作）"""
        pass

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        生成驗證報告

        Args:
            output_path: 報告輸出路徑，若為 None 則自動生成

        Returns:
            str: 報告檔案路徑
        """
        if self.result is None:
            raise ValueError("尚未執行驗證，請先呼叫 validate()")

        # 決定輸出路徑
        if output_path is None:
            # 與資料檔案同目錄，檔名為 {date}-report.md
            output_path = self.file_path.parent / f"{self.result.date}-report.md"
        else:
            output_path = Path(output_path)

        # 生成報告內容
        report_content = self._generate_report_content()

        # 寫入檔案
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"驗證報告已生成: {output_path}")
        return str(output_path)

    def _generate_report_content(self) -> str:
        """生成報告內容"""
        r = self.result

        # 狀態圖示
        status_icon = {
            'PASS': '✅',
            'WARN': '⚠️',
            'FAIL': '❌'
        }

        report = f"""# 資料驗證報告

**資料類型**: {self.DATA_TYPE_NAME}
**日期**: {r.date}
**驗證時間**: {r.validation_time}
**資料檔案**: {r.file_path}

---

## 📊 驗證摘要

| 驗證項目 | 結果 | 備註 |
|---------|------|------|
"""

        # 按類別分組問題
        structure_issues = [i for i in r.issues if i.category == 'structure']
        completeness_issues = [i for i in r.issues if i.category == 'completeness']
        reasonableness_issues = [i for i in r.issues if i.category == 'reasonableness']

        # 生成摘要表格
        for issue in r.issues[:6]:  # 只顯示前6個主要項目
            icon = status_icon.get(issue.level, '')
            report += f"| {issue.item} | {icon} {issue.level} | {issue.message} |\n"

        report += f"""
**總體評分**: {r.grade} ({r.accuracy:.1f}%)

---

## 📈 資料統計

- **總筆數**: {r.total_records:,}
- **上市股票**: {r.twse_records:,} ({r.twse_records/r.total_records*100:.1f}%)
- **上櫃股票**: {r.tpex_records:,} ({r.tpex_records/r.total_records*100:.1f}%)
- **資料大小**: {r.file_size/1024:.0f} KB

---

## 🔍 詳細驗證結果

### 1. 結構驗證

"""

        for issue in structure_issues:
            icon = status_icon.get(issue.level, '')
            report += f"#### {issue.item}\n"
            report += f"- {icon} {issue.message}\n\n"

        report += """### 2. 完整性驗證

"""

        for issue in completeness_issues:
            icon = status_icon.get(issue.level, '')
            report += f"#### {issue.item}\n"
            report += f"- {icon} {issue.message}\n"
            if issue.details:
                report += f"- 詳細資訊: {issue.details}\n"
            report += "\n"

        report += """### 3. 合理性驗證

"""

        for issue in reasonableness_issues:
            icon = status_icon.get(issue.level, '')
            report += f"#### {issue.item}\n"
            report += f"- {icon} {issue.message}\n"
            if issue.details:
                report += f"- 詳細資訊: {issue.details}\n"
            report += "\n"

        # 警告與異常
        warnings = [i for i in r.issues if i.level == 'WARN']
        failures = [i for i in r.issues if i.level == 'FAIL']

        if warnings or failures:
            report += """---

## ⚠️ 警告與異常

"""
            if failures:
                report += f"### 嚴重問題 ({len(failures)} 筆)\n\n"
                for idx, issue in enumerate(failures, 1):
                    report += f"#### {idx}. {issue.item}\n"
                    report += f"- **層級**: ❌ FAIL\n"
                    report += f"- **訊息**: {issue.message}\n"
                    if issue.details:
                        report += f"- **詳細**: {issue.details}\n"
                    report += "\n"

            if warnings:
                report += f"### 警告事項 ({len(warnings)} 筆)\n\n"
                for idx, issue in enumerate(warnings, 1):
                    report += f"#### {idx}. {issue.item}\n"
                    report += f"- **層級**: ⚠️ WARN\n"
                    report += f"- **訊息**: {issue.message}\n"
                    if issue.details:
                        report += f"- **詳細**: {issue.details}\n"
                    report += "\n"

        # 結論
        conclusion_icon = status_icon.get(r.status, '')
        report += f"""---

## ✅ 驗證結論

**最終評分**: {r.grade} ({r.accuracy:.1f}%)
**驗證狀態**: {conclusion_icon} {r.status}
**資料品質**: {'優良' if r.grade in ['A+', 'A'] else '良好' if r.grade == 'B' else '合格' if r.grade in ['C', 'D'] else '不合格'}

"""

        if r.status == 'PASS':
            report += "資料通過所有驗證項目，可安全使用。\n"
        elif r.status == 'WARN':
            report += f"資料通過基本驗證，但有 {r.warned_checks} 個警告項目，建議檢視後使用。\n"
        else:
            report += f"資料驗證失敗，有 {r.failed_checks} 個嚴重問題，請修正後再使用。\n"

        report += """
---

**驗證程式版本**: 1.0.0
**驗證者**: tw-stock-collector automated validation
"""

        return report
