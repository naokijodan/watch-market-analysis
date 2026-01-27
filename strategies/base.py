#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategy Pattern - 抽象基底クラス
各ブランド戦略クラスが継承する基底クラス
"""
from abc import ABC, abstractmethod
import pandas as pd
import sys
import os

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.common import (
    format_price, calculate_cv, cv_to_stability,
    aggregate_top_lines, generate_search_link_html
)


class AbstractBrandStrategy(ABC):
    """
    ブランド戦略の抽象基底クラス

    各ブランドで共通の処理フローを定義し、
    ブランド固有の処理は子クラスでオーバーライド
    """

    def __init__(self, brand_name, df_brand, brand_color, brand_color_light):
        """
        初期化

        Args:
            brand_name: ブランド名（例: "SEIKO"）
            df_brand: ブランドのDataFrame
            brand_color: ブランドカラー（濃）
            brand_color_light: ブランドカラー（淡）
        """
        self.brand_name = brand_name
        self.df = df_brand.copy()
        self.brand_color = brand_color
        self.brand_color_light = brand_color_light

        # 統計情報を初期化
        self.stats = {}

    @abstractmethod
    def extract_model_number(self, title_upper):
        """
        タイトルから型番を抽出（ブランド固有）

        Args:
            title_upper: 大文字化されたタイトル

        Returns:
            型番（抽出失敗時は"N/A"）
        """
        pass

    @abstractmethod
    def classify_line(self, row):
        """
        商品をラインに分類（ブランド固有）

        Args:
            row: DataFrameの行

        Returns:
            ライン名
        """
        pass

    def process_data(self):
        """
        データ処理の共通フロー
        """
        print(f"\n{'='*60}")
        print(f"🔵 {self.brand_name}タブ生成開始")
        print(f"{'='*60}")

        # 1. 型番抽出
        print(f"\n📋 型番抽出中...")
        self.df['型番'] = self.df['TITLE_UPPER'].apply(self.extract_model_number)
        print(f"  ✓ 型番抽出完了: {(self.df['型番'] != 'N/A').sum()}件")

        # 2. ライン分類
        print(f"\n📁 ライン分類中...")
        self.df['ライン'] = self.df.apply(self.classify_line, axis=1)
        line_counts = self.df['ライン'].value_counts()
        print(f"  ✓ ライン分類完了: {len(line_counts)}ライン")

        # 3. 統計計算
        print(f"\n📊 統計計算中...")
        self.calculate_statistics()
        print(f"  ✓ 統計計算完了")

        print(f"\n✅ {self.brand_name}データ処理完了")

    def calculate_statistics(self):
        """
        統計情報を計算
        """
        self.stats['total_sales'] = len(self.df)
        self.stats['average_price'] = self.df['価格'].mean()
        self.stats['median_price'] = self.df['価格'].median()
        self.stats['cv_value'] = calculate_cv(self.df['価格'])

        # 価格帯別集計
        self.stats['price_ranges'] = self._calculate_price_ranges()

        # ライン別統計
        self.stats['line_stats'] = self._calculate_line_stats()

        # Top30
        self.stats['top30'] = self._calculate_top30()

    def _calculate_price_ranges(self):
        """価格帯別集計"""
        bins = [0, 100, 300, 500, 1000, float('inf')]
        labels = ['~$100', '$100-300', '$300-500', '$500-1000', '$1000~']

        self.df['価格帯'] = pd.cut(self.df['価格'], bins=bins, labels=labels)
        price_range_counts = self.df['価格帯'].value_counts().sort_index()

        return price_range_counts

    def _calculate_line_stats(self):
        """ライン別統計"""
        line_groups = self.df.groupby('ライン')

        line_stats = pd.DataFrame({
            '販売数': line_groups.size(),
            '中央値': line_groups['価格'].median(),
            'CV値': line_groups['価格'].apply(calculate_cv)
        }).sort_values('販売数', ascending=False)

        # 比率計算
        line_stats['比率'] = line_stats['販売数'] / line_stats['販売数'].sum()

        # 安定度
        line_stats['安定度'] = line_stats['CV値'].apply(cv_to_stability)

        return line_stats

    def _calculate_top30(self):
        """Top30人気モデル"""
        model_stats = self.df.groupby('型番').agg({
            '販売数': 'sum',
            '価格': 'median'
        }).sort_values('販売数', ascending=False).head(30)

        return model_stats

    @abstractmethod
    def generate_html(self):
        """
        HTMLを生成（ブランド固有）

        Returns:
            HTML文字列
        """
        pass

    def generate_base_stats_html(self):
        """
        基本統計HTMLを生成（共通）

        Returns:
            HTML文字列
        """
        html = f'''
        <div class="stats-grid" style="margin-bottom: 30px;">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value" style="color: {self.brand_color};">{self.stats['total_sales']:,}個</div>
            </div>
            <div class="stat-card">
                <div class="label">平均価格</div>
                <div class="value">{format_price(self.stats['average_price'])}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">{format_price(self.stats['median_price'])}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV値（価格安定度）</div>
                <div class="value" style="color: {self.brand_color};">{self.stats['cv_value']:.3f}</div>
            </div>
        </div>
        '''
        return html


if __name__ == '__main__':
    print("✅ 基底クラス定義完了")
    print("   - AbstractBrandStrategy: 各ブランド戦略の基底クラス")
    print("   - 共通処理フロー: process_data() → calculate_statistics()")
    print("   - 抽象メソッド: extract_model_number(), classify_line(), generate_html()")
