"""
SQLAlchemy ORM Models for Taiwan Stock Database

對應 database/schemas/common/01-tables.sql 中的資料表定義
支援 PostgreSQL 和 SQLite
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, Date, DECIMAL, BigInteger, Integer,
    TIMESTAMP, ForeignKey, UniqueConstraint, Index, text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Stock(Base):
    """股票基本資訊表"""
    __tablename__ = 'stocks'

    stock_id = Column(String(10), primary_key=True, comment='股票代碼')
    stock_name = Column(String(100), nullable=False, comment='股票名稱')
    market_type = Column(String(10), nullable=False, comment='市場類型: twse 或 tpex')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<Stock(stock_id={self.stock_id}, name={self.stock_name})>"


class StockPriceDaily(Base):
    """每日價格資料表"""
    __tablename__ = 'stock_prices'
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_id', name='uq_price_date_stock'),
        Index('idx_price_date', 'trade_date'),
        Index('idx_price_stock', 'stock_id'),
        Index('idx_price_date_stock', 'trade_date', 'stock_id'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(Date, nullable=False, comment='交易日期')
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)

    open_price = Column(DECIMAL(10, 2), comment='開盤價')
    high_price = Column(DECIMAL(10, 2), comment='最高價')
    low_price = Column(DECIMAL(10, 2), comment='最低價')
    close_price = Column(DECIMAL(10, 2), comment='收盤價 (建議使用還原股價)')
    volume = Column(BigInteger, comment='成交量 (股)')
    amount = Column(DECIMAL(18, 2), comment='成交金額 (元)')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # Relationship
    stock = relationship("Stock", backref="price_data")

    def __repr__(self):
        return f"<StockPriceDaily(date={self.trade_date}, stock={self.stock_id}, close={self.close_price})>"


class StockInstitutionalDaily(Base):
    """三大法人買賣超資料表"""
    __tablename__ = 'institutional_investors'
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_id', name='uq_institutional_date_stock'),
        Index('idx_institutional_date', 'trade_date'),
        Index('idx_institutional_stock', 'stock_id'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    trade_date = Column(Date, nullable=False)

    # 外資 (Foreign Investors)
    foreign_buy = Column(BigInteger, comment='外資買進 (股)')
    foreign_sell = Column(BigInteger, comment='外資賣出 (股)')
    foreign_net = Column(BigInteger, comment='外資買賣超 (股)')

    # 外資細分
    foreign_main_buy = Column(BigInteger, comment='外陸資買進 (不含外資自營商)')
    foreign_main_sell = Column(BigInteger, comment='外陸資賣出')
    foreign_main_net = Column(BigInteger, comment='外陸資買賣超')
    foreign_dealer_buy = Column(BigInteger, comment='外資自營商買進')
    foreign_dealer_sell = Column(BigInteger, comment='外資自營商賣出')
    foreign_dealer_net = Column(BigInteger, comment='外資自營商買賣超')

    # 投信 (Investment Trust)
    trust_buy = Column(BigInteger, comment='投信買進 (股)')
    trust_sell = Column(BigInteger, comment='投信賣出 (股)')
    trust_net = Column(BigInteger, comment='投信買賣超 (股)')

    # 自營商 (Dealers)
    dealer_buy = Column(BigInteger, comment='自營商買進 (股)')
    dealer_sell = Column(BigInteger, comment='自營商賣出 (股)')
    dealer_net = Column(BigInteger, comment='自營商買賣超 (股)')

    # 自營商細分
    dealer_self_buy = Column(BigInteger, comment='自營商買進 (自行買賣)')
    dealer_self_sell = Column(BigInteger, comment='自營商賣出 (自行買賣)')
    dealer_self_net = Column(BigInteger, comment='自營商買賣超 (自行買賣)')
    dealer_hedge_buy = Column(BigInteger, comment='自營商買進 (避險)')
    dealer_hedge_sell = Column(BigInteger, comment='自營商賣出 (避險)')
    dealer_hedge_net = Column(BigInteger, comment='自營商買賣超 (避險)')

    # 合計
    total_net = Column(BigInteger, comment='三大法人買賣超合計 (股)')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="institutional_data")

    def __repr__(self):
        return f"<StockInstitutionalDaily(date={self.trade_date}, stock={self.stock_id})>"


class StockMarginDaily(Base):
    """融資融券資料表"""
    __tablename__ = 'margin_trading'
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_id', name='uq_margin_date_stock'),
        Index('idx_margin_date', 'trade_date'),
        Index('idx_margin_stock', 'stock_id'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    trade_date = Column(Date, nullable=False)

    # 融資 (Margin Trading)
    margin_balance = Column(DECIMAL(15, 2), comment='融資餘額 (千元)')
    margin_change = Column(DECIMAL(15, 2), comment='融資增減 (千元)')

    # 融券 (Short Selling)
    short_balance = Column(BigInteger, comment='融券餘額 (股)')
    short_change = Column(BigInteger, comment='融券增減 (股)')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="margin_data")

    def __repr__(self):
        return f"<StockMarginDaily(date={self.trade_date}, stock={self.stock_id})>"


class StockLendingDaily(Base):
    """借券賣出資料表"""
    __tablename__ = 'securities_lending'
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_id', name='uq_lending_date_stock'),
        Index('idx_lending_date', 'trade_date'),
        Index('idx_lending_stock', 'stock_id'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    trade_date = Column(Date, nullable=False)

    # 借券資料
    lending_balance = Column(BigInteger, comment='借券餘額 (股)')
    lending_change = Column(BigInteger, comment='借券增減 (股)')
    prev_balance = Column(BigInteger, comment='前日餘額 (股)')
    daily_sell = Column(BigInteger, comment='當日賣出 (股)')
    daily_return = Column(BigInteger, comment='當日還券 (股)')
    daily_adjust = Column(BigInteger, comment='當日調整 (股)')
    next_day_available = Column(BigInteger, comment='次一營業日可限額 (股)')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="lending_data")

    def __repr__(self):
        return f"<StockLendingDaily(date={self.trade_date}, stock={self.stock_id})>"


class StockTop20VolumeDaily(Base):
    """成交量前20名資料表"""
    __tablename__ = 'top20_volume'
    __table_args__ = (
        UniqueConstraint('trade_date', 'rank', name='uq_top20_date_rank'),
        Index('idx_top20_date', 'trade_date'),
        Index('idx_top20_rank', 'trade_date', 'rank'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    trade_date = Column(Date, nullable=False)

    rank = Column(Integer, nullable=False, comment='成交量排名')
    volume = Column(BigInteger, comment='成交量 (股)')
    amount = Column(DECIMAL(18, 2), comment='成交金額 (元)')
    transaction_count = Column(Integer, comment='成交筆數')

    # 價格資料
    open_price = Column(DECIMAL(10, 2), comment='開盤價')
    high_price = Column(DECIMAL(10, 2), comment='最高價')
    low_price = Column(DECIMAL(10, 2), comment='最低價')
    close_price = Column(DECIMAL(10, 2), comment='收盤價')
    change_price = Column(DECIMAL(10, 2), comment='漲跌價差')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="top20_data")

    def __repr__(self):
        return f"<StockTop20VolumeDaily(date={self.trade_date}, rank={self.rank}, stock={self.stock_id})>"


# NOTE: DataCollectionLog 暫時註解掉，因為 SQL schema 中沒有定義此表
# 若未來需要此功能，請先在 database/schemas/common/01-tables.sql 中新增表定義
# class DataCollectionLog(Base):
#     """資料收集記錄表"""
#     __tablename__ = 'data_collection_log'
#     __table_args__ = (
#         Index('idx_collection_date_type', 'collection_date', 'data_type'),
#     )
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     collection_date = Column(Date, nullable=False, comment='收集日期')
#     data_type = Column(String(50), nullable=False, comment='資料類型')
#     status = Column(String(20), nullable=False, comment='狀態 (success/failed/partial)')
#     record_count = Column(Integer, comment='記錄筆數')
#     error_message = Column(String(500), comment='錯誤訊息')
#     started_at = Column(TIMESTAMP, comment='開始時間')
#     completed_at = Column(TIMESTAMP, comment='完成時間')
#     created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
#
#     def __repr__(self):
#         return f"<DataCollectionLog(date={self.collection_date}, type={self.data_type}, status={self.status})>"


class DataImportLog(Base):
    """資料匯入記錄表"""
    __tablename__ = 'import_logs'
    __table_args__ = (
        Index('idx_import_date_type', 'import_date', 'data_type'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    import_date = Column(Date, nullable=False, comment='匯入日期')
    data_type = Column(String(50), nullable=False, comment='資料類型')
    start_time = Column(TIMESTAMP, nullable=False, comment='匯入開始時間')
    end_time = Column(TIMESTAMP, comment='匯入結束時間')
    status = Column(String(20), nullable=False, comment='狀態: running, completed, failed')
    records_count = Column(Integer, comment='匯入的記錄數')
    error_message = Column(String, comment='錯誤訊息')  # TEXT in SQL
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<DataImportLog(date={self.import_date}, type={self.data_type}, status={self.status})>"


class ETF(Base):
    """ETF 基本資訊表"""
    __tablename__ = 'etfs'

    etf_id = Column(String(10), primary_key=True, comment='ETF 代碼')
    etf_name = Column(String(100), nullable=False, comment='ETF 名稱')
    description = Column(String(500), comment='ETF 說明')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<ETF(etf_id={self.etf_id}, name={self.etf_name})>"


class ETFHolding(Base):
    """ETF 持股明細表"""
    __tablename__ = 'etf_holdings'
    __table_args__ = (
        UniqueConstraint('etf_id', 'stock_id', 'snapshot_date', name='uq_etf_stock_date'),
        Index('idx_etf_holdings_etf', 'etf_id'),
        Index('idx_etf_holdings_stock', 'stock_id'),
        Index('idx_etf_holdings_date', 'snapshot_date'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    etf_id = Column(String(10), ForeignKey('etfs.etf_id', ondelete='CASCADE'), nullable=False)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    snapshot_date = Column(Date, nullable=False, comment='持股快照日期')

    weight = Column(DECIMAL(10, 2), comment='持股權重 (%)')
    shares = Column(BigInteger, comment='持有股數')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    etf = relationship("ETF", backref="holdings")
    stock = relationship("Stock", backref="etf_holdings")

    def __repr__(self):
        return f"<ETFHolding(etf={self.etf_id}, stock={self.stock_id}, weight={self.weight})>"


class ETFStockUnion(Base):
    """ETF 持股去重清單表 - 包含所有 ETF 的成分股（去重）"""
    __tablename__ = 'etf_stock_union'
    __table_args__ = (
        Index('idx_etf_union_stock', 'stock_id'),
    )

    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), primary_key=True)
    etf_count = Column(Integer, nullable=False, comment='被幾個 ETF 持有')
    total_weight = Column(DECIMAL(10, 2), comment='所有 ETF 中的權重總和 (%)')
    latest_update = Column(Date, nullable=False, comment='最後更新日期')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    # Relationship
    stock = relationship("Stock", backref="etf_union")

    def __repr__(self):
        return f"<ETFStockUnion(stock={self.stock_id}, etf_count={self.etf_count})>"


class StockAnalysisDaily(Base):
    """技術分析寬表 - 30+ 技術指標"""
    __tablename__ = 'stock_analysis_daily'
    __table_args__ = (
        UniqueConstraint('trade_date', 'stock_id', name='uq_analysis_date_stock'),
        Index('idx_analysis_date', 'trade_date'),
        Index('idx_analysis_stock', 'stock_id'),
        # 選股策略用索引
        Index('idx_analysis_trend_vol', 'trade_date', 'close_price', 'ma_5', 'vol_ratio'),
        Index('idx_analysis_rsi_macd', 'trade_date', 'rsi_14', 'macd_hist'),
        Index('idx_analysis_dmi', 'trade_date', 'dmi_pdi', 'dmi_mdi', 'dmi_adx'),
    )

    trade_date = Column(Date, primary_key=True, nullable=False)
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), primary_key=True, nullable=False)

    # 基本價量
    open_price = Column(DECIMAL(10, 2))
    high_price = Column(DECIMAL(10, 2))
    low_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    volume = Column(BigInteger)
    amount = Column(DECIMAL(18, 2))

    # 移動平均線 (6條)
    ma_5 = Column(DECIMAL(10, 2), comment='5日均線')
    ma_10 = Column(DECIMAL(10, 2), comment='10日均線')
    ma_20 = Column(DECIMAL(10, 2), comment='20日均線')
    ma_60 = Column(DECIMAL(10, 2), comment='60日均線')
    ma_120 = Column(DECIMAL(10, 2), comment='120日均線')
    ma_240 = Column(DECIMAL(10, 2), comment='240日均線')

    # RSI 指標 (2個週期)
    rsi_6 = Column(DECIMAL(10, 2), comment='6日RSI')
    rsi_14 = Column(DECIMAL(10, 2), comment='14日RSI')

    # MACD 指標
    macd_dif = Column(DECIMAL(10, 2), comment='MACD DIF')
    macd_dea = Column(DECIMAL(10, 2), comment='MACD DEA (訊號線)')
    macd_hist = Column(DECIMAL(10, 2), comment='MACD 柱狀圖')

    # DMI 指標
    dmi_pdi = Column(DECIMAL(10, 2), comment='DMI +DI')
    dmi_mdi = Column(DECIMAL(10, 2), comment='DMI -DI')
    dmi_adx = Column(DECIMAL(10, 2), comment='DMI ADX')
    dmi_adxr = Column(DECIMAL(10, 2), comment='DMI ADXR')

    # 布林通道
    bb_upper = Column(DECIMAL(10, 2), comment='布林通道上軌')
    bb_mid = Column(DECIMAL(10, 2), comment='布林通道中軌')
    bb_lower = Column(DECIMAL(10, 2), comment='布林通道下軌')

    # 成交量分析
    vol_ma5 = Column(BigInteger, comment='5日均量')
    vol_ma20 = Column(BigInteger, comment='20日均量')
    vol_ratio = Column(DECIMAL(10, 2), comment='量比 (當日量/5日均量)')
    vwap = Column(DECIMAL(10, 2), comment='成交量加權平均價')

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="analysis_data")

    def __repr__(self):
        return f"<StockAnalysisDaily(date={self.trade_date}, stock={self.stock_id})>"


class StockRevenue(Base):
    """月營收資料表"""
    __tablename__ = 'stock_revenues'
    __table_args__ = (
        UniqueConstraint('year_month', 'stock_id', name='uq_revenue_yearmonth_stock'),
        Index('idx_revenue_yearmonth', 'year_month'),
        Index('idx_revenue_stock', 'stock_id'),
        Index('idx_revenue_yearmonth_stock', 'year_month', 'stock_id'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    year_month = Column(String(7), nullable=False, comment='資料年月 (YYYY-MM)')
    stock_id = Column(String(10), ForeignKey('stocks.stock_id', ondelete='CASCADE'), nullable=False)
    stock_name = Column(String(100), comment='股票名稱')
    market_type = Column(String(10), comment='市場類型: twse 或 tpex')

    # 當月營收
    current_month_revenue = Column(DECIMAL(20, 2), comment='當月營收（千元）')
    last_month_revenue = Column(DECIMAL(20, 2), comment='上月營收（千元）')
    last_year_revenue = Column(DECIMAL(20, 2), comment='去年同月營收（千元）')

    # 營收變化
    revenue_change = Column(DECIMAL(20, 2), comment='營收變化金額（千元）')
    mom_change_pct = Column(DECIMAL(10, 4), comment='月增率 (%)')
    yoy_change_pct = Column(DECIMAL(10, 4), comment='年增率 (%)')

    # 累計營收
    ytd_revenue = Column(DECIMAL(20, 2), comment='年初至今累計營收（千元）')
    ytd_last_year_revenue = Column(DECIMAL(20, 2), comment='去年同期累計營收（千元）')
    ytd_yoy_change_pct = Column(DECIMAL(10, 4), comment='累計年增率 (%)')

    # 備註
    note = Column(String(500), comment='營收變動說明')

    # 資料來源與時間
    data_source = Column(String(20), comment='資料來源: daily, monthly, mops')
    collection_date = Column(Date, comment='收集日期')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    stock = relationship("Stock", backref="revenues")

    def __repr__(self):
        return f"<StockRevenue(year_month={self.year_month}, stock={self.stock_id}, revenue={self.current_month_revenue})>"
