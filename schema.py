#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時計市場分析システム - データスキーマ定義
全ブランド共通のデータ構造とバリデーションルール
"""
from dataclasses import dataclass, field
from typing import Optional, List
import pandas as pd


@dataclass
class WatchData:
    """時計データの基本スキーマ"""

    # 必須フィールド（全ブランド共通）
    brand: str  # ブランド名
    title: str  # タイトル
    price: float  # 価格（USD）
    sales: int  # 販売数
    condition: str  # 商品状態（"完品"など）

    # 抽出・分類フィールド
    model_number: str = "N/A"  # 型番（抽出失敗時はN/A）
    line: str = "不明"  # ライン（分類失敗時は不明）
    category: str = "腕時計"  # カテゴリ

    # ブランド固有フィールド（Optional）
    drive_type: Optional[str] = None  # 駆動方式（SEIKO, CITIZEN）
    character_collab: Optional[str] = None  # キャラクター/コラボ名
    limited_edition: bool = False  # 限定モデル（Orient）
    anniversary_model: bool = False  # 記念モデル（Orient）

    # メタデータ
    jdm: bool = False  # JDM（Japanese Domestic Market）かどうか
    raw_title_upper: str = ""  # 大文字化されたタイトル（検索用）

    def __post_init__(self):
        """バリデーション"""
        # 価格の検証
        if self.price < 0:
            raise ValueError(f"価格は0以上である必要があります: {self.price}")

        # 販売数の検証
        if self.sales < 0:
            raise ValueError(f"販売数は0以上である必要があります: {self.sales}")

        # ラインの正規化
        if not self.line or self.line.strip() == "":
            self.line = "不明"

        # 型番の正規化
        if not self.model_number or self.model_number.strip() == "":
            self.model_number = "N/A"

        # タイトル大文字化
        if not self.raw_title_upper:
            self.raw_title_upper = self.title.upper()


@dataclass
class BrandStatistics:
    """ブランド統計データ"""

    brand: str
    total_sales: int
    total_items: int  # ユニーク商品数
    average_price: float
    median_price: float
    cv_value: float  # 変動係数

    # 価格帯別データ
    price_ranges: dict = field(default_factory=dict)

    # ライン別データ
    line_stats: pd.DataFrame = field(default_factory=pd.DataFrame)

    # Top30データ
    top30: List[WatchData] = field(default_factory=list)

    # キャラクター/コラボデータ
    character_stats: Optional[pd.DataFrame] = None

    # 駆動方式別データ（SEIKO, CITIZEN）
    drive_type_stats: Optional[pd.DataFrame] = None

    # 限定モデルデータ（Orient）
    limited_edition_stats: Optional[pd.DataFrame] = None


def validate_dataframe(df: pd.DataFrame, brand: str) -> pd.DataFrame:
    """
    DataFrameのバリデーションと正規化

    Args:
        df: 入力DataFrame
        brand: ブランド名

    Returns:
        バリデーション済みDataFrame
    """
    # 必須カラムの確認
    required_columns = ['タイトル', '価格', '販売数', '商品状態']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"必須カラムが不足しています: {missing_columns}")

    # 完品データのみ抽出
    df_clean = df[df['商品状態'] == '完品'].copy()

    # 価格と販売数の型変換と検証
    df_clean['価格'] = pd.to_numeric(df_clean['価格'], errors='coerce')
    df_clean['販売数'] = pd.to_numeric(df_clean['販売数'], errors='coerce')

    # 欠損値を削除
    df_clean = df_clean.dropna(subset=['価格', '販売数'])

    # 負の値を除外
    df_clean = df_clean[(df_clean['価格'] >= 0) & (df_clean['販売数'] >= 0)]

    # タイトル大文字化
    df_clean['TITLE_UPPER'] = df_clean['タイトル'].str.upper()

    print(f"✓ {brand} バリデーション完了: {len(df_clean)}件（元データ: {len(df)}件）")

    return df_clean


def calculate_cv(values):
    """
    変動係数（Coefficient of Variation）を計算

    Args:
        values: 数値のリストまたはSeries

    Returns:
        CV値（標準偏差 / 平均）
    """
    if len(values) == 0:
        return 0.0

    mean_val = values.mean()
    if mean_val == 0:
        return 0.0

    std_val = values.std()
    cv = std_val / mean_val

    return cv


def cv_to_stability(cv_value):
    """
    CV値を安定度表示に変換

    Args:
        cv_value: CV値

    Returns:
        安定度（☆の数）
    """
    if cv_value < 0.5:
        return "☆☆☆"
    elif cv_value < 1.0:
        return "☆☆☆"
    elif cv_value < 2.0:
        return "☆☆"
    else:
        return "☆"


if __name__ == '__main__':
    print("✅ スキーマ定義完了")
    print(f"   - WatchData: 時計データの基本構造")
    print(f"   - BrandStatistics: ブランド統計データ")
    print(f"   - validate_dataframe: データ検証関数")
    print(f"   - calculate_cv: CV値計算関数")
    print(f"   - cv_to_stability: 安定度変換関数")
