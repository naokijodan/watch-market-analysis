#!/usr/bin/env python3
"""
分析シートをExcelに出力
"""

import pandas as pd
from collections import Counter
import re

# CSVファイル読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# Excelファイル作成
with pd.ExcelWriter('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', engine='openpyxl') as writer:

    # 1. 基本統計シート
    basic_stats = pd.DataFrame({
        '項目': [
            '総出品数',
            '総販売数',
            '平均価格',
            '中央値価格',
            '最低価格',
            '最高価格',
            'ブランド種類数',
            '駆動方式種類数'
        ],
        '値': [
            f"{len(df):,} 件",
            f"{df['販売数'].sum():,} 個",
            f"${df['価格'].mean():.2f}",
            f"${df['価格'].median():.2f}",
            f"${df['価格'].min():.2f}",
            f"${df['価格'].max():.2f}",
            df['ブランド'].nunique(),
            df['駆動方式'].nunique()
        ]
    })
    basic_stats.to_excel(writer, sheet_name='1_基本統計', index=False)

    # 2. ブランド別統計シート
    brand_stats = df.groupby('ブランド').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median', 'min', 'max']
    }).reset_index()
    brand_stats.columns = ['ブランド', '出品数', '販売数', '平均価格', '中央値', '最低価格', '最高価格']
    brand_stats = brand_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    brand_stats.to_excel(writer, sheet_name='2_ブランド別統計', index=False)

    # 3. 駆動方式別統計シート
    drive_stats = df.groupby('駆動方式').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median']
    }).reset_index()
    drive_stats.columns = ['駆動方式', '出品数', '販売数', '平均価格', '中央値']
    drive_stats = drive_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    drive_stats.to_excel(writer, sheet_name='3_駆動方式別統計', index=False)

    # 4. カテゴリ別統計シート
    category_stats = df.groupby('カテゴリ').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median']
    }).reset_index()
    category_stats.columns = ['カテゴリ', '出品数', '販売数', '平均価格', '中央値']
    category_stats = category_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    category_stats.to_excel(writer, sheet_name='4_カテゴリ別統計', index=False)

    # 5. 商品状態別統計シート
    condition_stats = df.groupby('商品状態').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median']
    }).reset_index()
    condition_stats.columns = ['商品状態', '出品数', '販売数', '平均価格', '中央値']
    condition_stats = condition_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    condition_stats.to_excel(writer, sheet_name='5_商品状態別統計', index=False)

    # 6. パーツ種類別統計シート
    parts_df = df[df['商品状態'] == 'パーツ'].copy()

    def classify_parts(title):
        title_upper = str(title).upper()
        if any(k in title_upper for k in ['BOX', 'CASE', 'ケース', '箱']):
            return '箱・ケース'
        elif any(k in title_upper for k in ['CROWN', 'KNOB', '竜頭', 'リューズ']):
            return '竜頭'
        elif any(k in title_upper for k in ['DIAL', 'FACE', '文字盤']):
            return '文字盤'
        elif any(k in title_upper for k in ['LINK', 'BRACELET PART', 'コマ', 'リンク']):
            return 'リンク/コマ'
        elif any(k in title_upper for k in ['BEZEL', 'ベゼル']):
            return 'ベゼル'
        elif any(k in title_upper for k in ['BAND', 'STRAP', 'BELT', 'ベルト', 'バンド', 'ストラップ']):
            return 'バンド/ストラップ'
        elif any(k in title_upper for k in ['BUCKLE', 'CLASP', 'バックル', 'クラスプ']):
            return 'バックル/クラスプ'
        else:
            return 'その他パーツ'

    parts_df['パーツ種類'] = parts_df['タイトル'].apply(classify_parts)
    parts_stats = parts_df.groupby('パーツ種類').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': 'median'
    }).reset_index()
    parts_stats.columns = ['パーツ種類', '出品数', '販売数', '中央値']
    parts_stats = parts_stats.sort_values('出品数', ascending=False).reset_index(drop=True)
    parts_stats.to_excel(writer, sheet_name='6_パーツ種類別統計', index=False)

    # 7. 月別推移シート
    df['販売月'] = pd.to_datetime(df['販売日']).dt.to_period('M')
    monthly = df.groupby('販売月').agg({
        'ブランド': 'count',
        '販売数': 'sum'
    }).reset_index()
    monthly.columns = ['販売月', '出品数', '販売数']
    monthly['販売月'] = monthly['販売月'].astype(str)
    monthly.to_excel(writer, sheet_name='7_月別推移', index=False)

    # 8. 価格帯分布シート（50ドル刻み）
    bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, float('inf')]
    labels = ['$0-50', '$50-100', '$100-150', '$150-200', '$200-250', '$250-300', '$300-350', '$350-400',
              '$400-450', '$450-500', '$500-550', '$550-600', '$600-650', '$650-700', '$700-750', '$750-800',
              '$800-850', '$850-900', '$900-950', '$950-1000', '$1000+']
    df['価格帯'] = pd.cut(df['価格'], bins=bins, labels=labels)
    price_dist = df.groupby('価格帯', observed=False).agg({
        'ブランド': 'count',
        '販売数': 'sum'
    }).reset_index()
    price_dist.columns = ['価格帯', '出品数', '販売数']
    price_dist.to_excel(writer, sheet_name='8_価格帯分布', index=False)

    # 9. まとめ売り分析シート
    bundle_keywords = ['LOT', 'SET', 'BULK', 'BUNDLE', 'まとめ', 'セット', 'ロット']
    bundle_df = df[df['タイトル_upper'].str.contains('|'.join(bundle_keywords), na=False)]

    bundle_brand_stats = bundle_df.groupby('ブランド').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median']
    }).reset_index()
    bundle_brand_stats.columns = ['ブランド', '出品数', '販売数', '平均価格', '中央値']
    bundle_brand_stats = bundle_brand_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    bundle_brand_stats.to_excel(writer, sheet_name='9_まとめ売り分析', index=False)

    # 10. タブ別集計要件シート
    tabs_requirements = pd.DataFrame({
        'タブ名': [
            '全体分析',
            '自動巻',
            'クオーツ',
            'ソーラー',
            '手巻き',
            'スマートウォッチ',
            'デジタル',
            'パーツ',
            'まとめ売り',
            'おすすめ出品順序',
            'SEIKO',
            'CASIO',
            'OMEGA',
            'CITIZEN',
            'Orient',
            'TAG HEUER',
            'GUCCI',
            'ROLEX',
            'Hamilton',
            'Longines',
            'Cartier',
            'RADO'
        ],
        'タブ種類': [
            '全体分析',
            '駆動方式',
            '駆動方式',
            '駆動方式',
            '駆動方式',
            '駆動方式',
            '駆動方式',
            'パーツ',
            'まとめ売り',
            'おすすめ',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド',
            'ブランド'
        ],
        '基本統計数': [4, 4, 4, 4, 4, 4, 4, 8, 4, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        'グラフ数': [6, 2, 2, 2, 2, 2, 2, 2, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        'テーブル数': [1, 2, 2, 2, 2, 2, 2, 1, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        '実装状況': [
            '✅',
            '⚠️ コンテンツなし',
            '⚠️ コンテンツなし',
            '⚠️ コンテンツなし',
            '⚠️ コンテンツなし',
            '⚠️ コンテンツなし',
            '⚠️ コンテンツなし',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '❌ 未実装',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅'
        ]
    })
    tabs_requirements.to_excel(writer, sheet_name='10_タブ別集計要件', index=False)

    # 11. HTMLとCSVギャップ分析シート
    gap_analysis = pd.DataFrame({
        'ブランド': ['CASIO', 'SEIKO', 'Longines'],
        'HTML表示（古い）': ['3,813件', '3,278件', '219件（販売数）'],
        'CSV出品数（最新）': [1811, 2742, 2981],
        'CSV販売数（最新）': [6300, 7524, 2984],
        'ギャップ': [
            'HTMLは古いデータ（更新必要）',
            'HTMLは古いデータ（更新必要）',
            '大幅に古い（219 vs 2,984件）'
        ],
        '優先度': ['高', '高', '最高']
    })
    gap_analysis.to_excel(writer, sheet_name='11_HTMLとCSVギャップ', index=False)

    # 12. デパートメント別統計シート
    dept_stats = df.groupby('デパートメント').agg({
        'ブランド': 'count',
        '販売数': 'sum',
        '価格': ['mean', 'median']
    }).reset_index()
    dept_stats.columns = ['デパートメント', '出品数', '販売数', '平均価格', '中央値']
    dept_stats = dept_stats.sort_values('販売数', ascending=False).reset_index(drop=True)
    dept_stats.to_excel(writer, sheet_name='12_デパートメント別', index=False)

print("✅ 分析シートを出力しました:")
print("   /Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx")
print("\n【シート一覧】")
print("  1. 基本統計")
print("  2. ブランド別統計（Top154ブランド）")
print("  3. 駆動方式別統計")
print("  4. カテゴリ別統計")
print("  5. 商品状態別統計")
print("  6. パーツ種類別統計")
print("  7. 月別推移")
print("  8. 価格帯分布")
print("  9. まとめ売り分析")
print(" 10. タブ別集計要件（26タブ）")
print(" 11. HTMLとCSVギャップ分析")
print(" 12. デパートメント別統計")
