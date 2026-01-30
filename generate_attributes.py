#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時計データ属性生成スクリプト
新規CSVデータに必須属性を自動生成します
"""

import pandas as pd
import re
from typing import Dict, Tuple

class WatchAttributeGenerator:
    """時計データの属性を生成するクラス"""

    # 商品状態判定キーワード（明確なパーツ）
    PARTS_EXCLUSIVE_KEYWORDS = [
        'NO WATCH', 'EMPTY BOX', 'BOX ONLY', 'CASE ONLY',
        'BAND ONLY', 'STRAP ONLY', 'BRACELET ONLY',
        'BEZEL ONLY', 'BUCKLE ONLY'
    ]

    # パーツの可能性があるキーワード（WATCH が含まれる場合は完品扱い）
    PARTS_MAYBE_KEYWORDS = [
        'GENUINE BAND', 'GENUINE STRAP', 'GENUINE BRACELET',
        'GENUINE LINK', 'GENUINE BEZEL', 'GENUINE BUCKLE',
        'REPLACEMENT BAND', 'REPLACEMENT STRAP',
        'LEATHER BAND', 'LEATHER STRAP', 'METAL BAND',
        'RUBBER BAND', 'RUBBER STRAP', 'SILICONE BAND',
        'BOOKLET ONLY', 'MANUAL ONLY', 'CARD ONLY'
    ]

    JUNK_KEYWORDS = [
        'JUNK', 'NOT WORKING', 'NON-WORKING', 'NON WORKING',
        'FOR PARTS', 'BROKEN', 'REPAIR'
    ]

    # 駆動方式判定キーワード
    MOVEMENT_KEYWORDS = {
        '自動巻': ['AUTOMATIC', 'AUTO ', ' AUTO', 'SELF-WINDING', 'SELF WINDING'],
        'クオーツ': ['QUARTZ', ' QZ', 'QZ ', ' QZ '],
        'ソーラー': ['SOLAR', 'TOUGH SOLAR', 'ECO-DRIVE', 'ECO DRIVE'],
        '手巻き': ['MANUAL', 'HAND WIND', 'HAND-WIND', 'MANUAL WIND'],
        'スマートウォッチ': ['SMARTWATCH', 'SMART WATCH', 'SMART-WATCH'],
        'デジタル': ['DIGITAL']
    }

    # デパートメント判定キーワード
    DEPARTMENT_KEYWORDS = {
        'メンズ': ["MEN'S", 'MENS', ' MEN ', 'MAN'],
        'レディース': ["WOMEN'S", 'WOMENS', 'LADIES', "LADY'S", 'LADY', ' WOMEN '],
        'ユニセックス': ['UNISEX'],
        'ボーイズ/キッズ': ['BOYS', 'KIDS', 'CHILDREN']
    }

    # その他のキーワード
    JDM_KEYWORDS = ['JDM', 'KANJI', '漢字']
    VINTAGE_KEYWORDS = ['VINTAGE', '1960', '1961', '1962', '1963', '1964', '1965',
                       '1966', '1967', '1968', '1969', '1970', '1971', '1972',
                       '1973', '1974', '1975', '1976', '1977', '1978', '1979',
                       '1980', '1981', '1982', '1983', '1984', '1985', '1986',
                       '1987', '1988', '1989', '1990', '1991', '1992', '1993',
                       '1994', '1995', '1996', '1997', '1998', '1999']
    BOX_KEYWORDS = ['BOX', 'W/ BOX', 'W/BOX', 'WITH BOX', 'NEW IN BOX', 'BOXED']
    WARRANTY_KEYWORDS = ['PAPER', 'PAPERS', 'WARRANTY', 'CERTIFICATE',
                        'W/ PAPER', 'W/PAPER', 'WITH PAPER', 'GUARANTEE', 'CERT']

    @staticmethod
    def classify_product_state(title: str) -> str:
        """商品状態を判定（完品/パーツ/ジャンク/まとめ売り）"""
        if pd.isna(title):
            return '完品'

        title_upper = str(title).upper()

        # ジャンク判定
        for keyword in WatchAttributeGenerator.JUNK_KEYWORDS:
            if keyword in title_upper:
                return 'ジャンク'

        # 明確なパーツ判定（WATCH の有無に関わらず）
        for keyword in WatchAttributeGenerator.PARTS_EXCLUSIVE_KEYWORDS:
            if keyword in title_upper:
                return 'パーツ'

        # WATCH が含まれている場合は完品と判定
        if 'WATCH' in title_upper or ' WA' in title_upper:
            # まとめ売り判定（複数ブランド or LOT）
            if 'LOT' in title_upper or title_upper.count('WATCH') > 2:
                return 'まとめ売り'
            return '完品'

        # WATCH が含まれていない場合、パーツの可能性が高い
        for keyword in WatchAttributeGenerator.PARTS_MAYBE_KEYWORDS:
            if keyword in title_upper:
                return 'パーツ'

        # どれにも該当しない場合は完品
        return '完品'

    @staticmethod
    def classify_movement_type(title: str) -> str:
        """駆動方式を判定"""
        if pd.isna(title):
            return '不明'

        title_upper = str(title).upper()

        # キーワードマッチング（優先順位順）
        for movement_type, keywords in WatchAttributeGenerator.MOVEMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_upper:
                    return movement_type

        return '不明'

    @staticmethod
    def classify_department(title: str) -> str:
        """デパートメントを判定（メンズ/レディース/ユニセックス/ボーイズ・キッズ）"""
        if pd.isna(title):
            return '不明'

        title_upper = str(title).upper()

        # キーワードマッチング
        for department, keywords in WatchAttributeGenerator.DEPARTMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_upper:
                    return department

        return '不明'

    @staticmethod
    def detect_jdm(title: str) -> bool:
        """JDM（Japan Domestic Market）を検出"""
        if pd.isna(title):
            return False

        title_upper = str(title).upper()

        for keyword in WatchAttributeGenerator.JDM_KEYWORDS:
            if keyword in title_upper:
                return True

        return False

    @staticmethod
    def detect_vintage(title: str) -> bool:
        """ヴィンテージを検出"""
        if pd.isna(title):
            return False

        title_upper = str(title).upper()

        for keyword in WatchAttributeGenerator.VINTAGE_KEYWORDS:
            if keyword in title_upper:
                return True

        return False

    @staticmethod
    def detect_box(title: str) -> bool:
        """箱付きを検出"""
        if pd.isna(title):
            return False

        title_upper = str(title).upper()

        # 除外: "NO BOX", "EMPTY BOX"
        if 'NO BOX' in title_upper or 'EMPTY BOX' in title_upper:
            return False

        for keyword in WatchAttributeGenerator.BOX_KEYWORDS:
            if keyword in title_upper:
                return True

        return False

    @staticmethod
    def detect_warranty(title: str) -> bool:
        """保証書付きを検出"""
        if pd.isna(title):
            return False

        title_upper = str(title).upper()

        for keyword in WatchAttributeGenerator.WARRANTY_KEYWORDS:
            if keyword in title_upper:
                return True

        return False

    @staticmethod
    def generate_all_attributes(df: pd.DataFrame) -> pd.DataFrame:
        """
        全属性を生成

        Args:
            df: 元のDataFrame（タイトル列が必須）

        Returns:
            属性が追加されたDataFrame
        """
        df_copy = df.copy()

        # タイトル_upper
        df_copy['タイトル_upper'] = df_copy['タイトル'].str.upper()

        # 商品状態
        df_copy['商品状態'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.classify_product_state
        )

        # 駆動方式
        df_copy['駆動方式'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.classify_movement_type
        )

        # JDM
        df_copy['JDM'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.detect_jdm
        )

        # ヴィンテージ
        df_copy['ヴィンテージ'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.detect_vintage
        )

        # 箱付き
        df_copy['箱付き'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.detect_box
        )

        # 保証書付き
        df_copy['保証書付き'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.detect_warranty
        )

        # デパートメント
        df_copy['デパートメント'] = df_copy['タイトル'].apply(
            WatchAttributeGenerator.classify_department
        )

        return df_copy

    @staticmethod
    def calculate_extraction_rates(df: pd.DataFrame) -> Dict[str, float]:
        """
        抽出率を計算（Dry Run用）

        Returns:
            各属性の抽出率
        """
        total = len(df)
        if total == 0:
            return {}

        return {
            '商品状態_完品率': (df['商品状態'] == '完品').sum() / total * 100,
            '駆動方式_判定率': (df['駆動方式'] != '不明').sum() / total * 100,
            'デパートメント_判定率': (df['デパートメント'] != '不明').sum() / total * 100,
            'JDM率': df['JDM'].sum() / total * 100,
            'ヴィンテージ率': df['ヴィンテージ'].sum() / total * 100,
            '箱付き率': df['箱付き'].sum() / total * 100,
            '保証書付き率': df['保証書付き'].sum() / total * 100,
        }


def main():
    """単体実行用メイン関数"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python3 generate_attributes.py <input_csv>")
        print("例: python3 generate_attributes.py ~/Desktop/new_watch_data.csv")
        sys.exit(1)

    input_csv = sys.argv[1]

    print(f"📂 CSVを読み込み中: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"✓ {len(df)}件のデータを読み込みました\n")

    print("🔧 属性を生成中...")
    df_with_attrs = WatchAttributeGenerator.generate_all_attributes(df)
    print("✓ 属性生成完了\n")

    print("📊 抽出率:")
    rates = WatchAttributeGenerator.calculate_extraction_rates(df_with_attrs)
    for attr, rate in rates.items():
        print(f"  {attr}: {rate:.1f}%")
    print()

    # 出力ファイル名
    output_csv = input_csv.replace('.csv', '_with_attributes.csv')
    df_with_attrs.to_csv(output_csv, index=False)
    print(f"✅ 保存完了: {output_csv}")


if __name__ == '__main__':
    main()
