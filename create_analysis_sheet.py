#!/usr/bin/env python3
"""
分析シート作成スクリプト
CSVデータから各タブの要件と現状を分析
"""

import pandas as pd
from collections import Counter
import re

# CSVファイル読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

print("=" * 80)
print("watch-market-analysis 分析シート")
print("=" * 80)

# 1. 基本統計
print("\n【1. 基本統計】")
print(f"総出品数: {len(df):,} 件")
print(f"総販売数: {df['販売数'].sum():,} 個")
print(f"平均価格: ${df['価格'].mean():.2f}")
print(f"中央値価格: ${df['価格'].median():.2f}")
print(f"最低価格: ${df['価格'].min():.2f}")
print(f"最高価格: ${df['価格'].max():.2f}")

# 2. ユニーク値の確認
print("\n【2. 列ごとのユニーク値】")
print(f"\nブランド（{df['ブランド'].nunique()}種類）:")
brand_counts = df['ブランド'].value_counts()
for brand, count in brand_counts.head(25).items():
    sales = df[df['ブランド'] == brand]['販売数'].sum()
    print(f"  {brand:20} 出品数: {count:5}, 販売数: {sales:6}")

print(f"\n駆動方式（{df['駆動方式'].nunique()}種類）:")
drive_counts = df.groupby('駆動方式').agg({
    'ブランド': 'count',
    '販売数': 'sum'
}).rename(columns={'ブランド': '出品数'})
for drive, row in drive_counts.iterrows():
    print(f"  {drive:20} 出品数: {row['出品数']:5}, 販売数: {row['販売数']:6}")

print(f"\nカテゴリ（{df['カテゴリ'].nunique()}種類）:")
for cat in df['カテゴリ'].unique():
    count = len(df[df['カテゴリ'] == cat])
    sales = df[df['カテゴリ'] == cat]['販売数'].sum()
    print(f"  {cat:30} 出品数: {count:5}, 販売数: {sales:6}")

print(f"\n商品状態（{df['商品状態'].nunique()}種類）:")
for cond in df['商品状態'].unique():
    count = len(df[df['商品状態'] == cond])
    sales = df[df['商品状態'] == cond]['販売数'].sum()
    print(f"  {cond:20} 出品数: {count:5}, 販売数: {sales:6}")

print(f"\nデパートメント（{df['デパートメント'].nunique()}種類）:")
dept_counts = df['デパートメント'].value_counts()
for dept, count in dept_counts.head(15).items():
    sales = df[df['デパートメント'] == dept]['販売数'].sum()
    print(f"  {dept:20} 出品数: {count:5}, 販売数: {sales:6}")

# 3. パーツ種類の抽出
print("\n【3. パーツ種類の分析】")
parts_df = df[df['商品状態'] == 'パーツ'].copy()
print(f"パーツ総数: {len(parts_df)} 件")

# パーツ種類の判定
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
parts_summary = parts_df.groupby('パーツ種類').agg({
    'ブランド': 'count',
    '販売数': 'sum',
    '価格': 'median'
}).rename(columns={'ブランド': '出品数'})

print("\nパーツ種類別統計:")
for parts_type, row in parts_summary.sort_values('出品数', ascending=False).iterrows():
    print(f"  {parts_type:20} 出品数: {int(row['出品数']):4}, 販売数: {int(row['販売数']):5}, 中央値: ${row['価格']:.2f}")

# 4. まとめ売りの分析
print("\n【4. まとめ売りの分析】")
bundle_keywords = ['LOT', 'SET', 'BULK', 'BUNDLE', 'まとめ', 'セット', 'ロット']
bundle_df = df[df['タイトル_upper'].str.contains('|'.join(bundle_keywords), na=False)]
print(f"まとめ売り件数: {len(bundle_df)} 件")
print(f"まとめ売り販売数: {bundle_df['販売数'].sum()} 個")
print(f"まとめ売り平均価格: ${bundle_df['価格'].mean():.2f}")
print(f"まとめ売り中央値: ${bundle_df['価格'].median():.2f}")

# 5. 特別版・限定モデルの分析
print("\n【5. 特別版・限定モデルの分析】")
special_keywords = ['LIMITED', 'ANNIVERSARY', 'CHRONOGRAPH', 'GOLD', 'SPECIAL', 'COLLECTOR',
                   'VINTAGE', 'RARE', '限定', '記念', 'アニバーサリー']
special_df = df[df['タイトル_upper'].str.contains('|'.join(special_keywords), na=False)]
print(f"特別版件数: {len(special_df)} 件")
print(f"特別版販売数: {special_df['販売数'].sum()} 個")
print(f"特別版平均価格: ${special_df['価格'].mean():.2f}")
print(f"特別版中央値: ${special_df['価格'].median():.2f}")

# 6. 型番抽出率の分析
print("\n【6. 型番抽出率の分析（ブランド別）】")

def extract_model_number_seiko(title):
    patterns = [
        r'\b([567][A-Z]{3}[0-9]{3,4}[A-Z]?)\b',
        r'\b(SBD[CX]\d{3})\b',
        r'\b(SRP[A-Z]?\d{3})\b'
    ]
    for p in patterns:
        match = re.search(p, title.upper())
        if match:
            return match.group(1)
    return None

def extract_model_number_casio(title):
    patterns = [
        r'\b([A-Z]{2,3}-[A-Z0-9]{3,5}(?:-\d+)?[A-Z]?)\b',
        r'\b(G-[A-Z0-9]{4,6})\b',
        r'\b(DW-[A-Z0-9]{4,6})\b'
    ]
    for p in patterns:
        match = re.search(p, title.upper())
        if match:
            return match.group(1)
    return None

brand_extraction = {}
for brand in brand_counts.head(12).index:
    brand_df = df[df['ブランド'] == brand].copy()
    if brand == 'SEIKO':
        brand_df['型番'] = brand_df['タイトル'].apply(extract_model_number_seiko)
    elif brand == 'CASIO':
        brand_df['型番'] = brand_df['タイトル'].apply(extract_model_number_casio)
    else:
        brand_df['型番'] = None

    extracted = brand_df['型番'].notna().sum()
    total = len(brand_df)
    rate = (extracted / total * 100) if total > 0 else 0
    brand_extraction[brand] = {'抽出数': extracted, '総数': total, '抽出率': rate}

for brand, stats in brand_extraction.items():
    print(f"  {brand:20} 抽出数: {stats['抽出数']:4}/{stats['総数']:4} ({stats['抽出率']:.1f}%)")

# 7. 月別推移の分析
print("\n【7. 月別推移】")
df['販売月'] = pd.to_datetime(df['販売日']).dt.to_period('M')
monthly = df.groupby('販売月').agg({
    'ブランド': 'count',
    '販売数': 'sum'
}).rename(columns={'ブランド': '出品数'})
print(monthly)

# 8. 価格帯分布（50ドル刻み）
print("\n【8. 価格帯分布】")
bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, float('inf')]
labels = ['$0-50', '$50-100', '$100-150', '$150-200', '$200-250', '$250-300', '$300-350', '$350-400',
          '$400-450', '$450-500', '$500-550', '$550-600', '$600-650', '$650-700', '$700-750', '$750-800',
          '$800-850', '$850-900', '$900-950', '$950-1000', '$1000+']
df['価格帯'] = pd.cut(df['価格'], bins=bins, labels=labels)
price_dist = df.groupby('価格帯').agg({
    'ブランド': 'count',
    '販売数': 'sum'
}).rename(columns={'ブランド': '出品数'})
print(price_dist)

# 9. タブ別の必要集計数
print("\n【9. タブ別の必要集計数】")
tabs = {
    '全体分析': {'基本統計': 4, 'グラフ': 6, 'テーブル': 1},
    '駆動方式タブ（6個）': {'基本統計': 4, 'グラフ': 2, 'テーブル': 2},
    'パーツタブ': {'基本統計': 8, 'グラフ': 2, 'テーブル': 1},
    'まとめ売りタブ': {'基本統計': 4, 'グラフ': 0, 'テーブル': 0},
    'おすすめ出品順序タブ': {'基本統計': 0, 'グラフ': 0, 'テーブル': 2},
    'ブランドタブ（12個）': {'基本統計': 4, 'グラフ': 4, 'テーブル': 3}
}
for tab, stats in tabs.items():
    print(f"  {tab:30} 基本統計: {stats['基本統計']}, グラフ: {stats['グラフ']}, テーブル: {stats['テーブル']}")

# 10. HTMLとCSVデータのギャップ分析
print("\n【10. HTMLとCSVデータのギャップ分析】")
print("\n現状のHTML（古いデータ）:")
print("  - CASIO: 3,813件")
print("  - SEIKO: 3,278件")
print("  - Longines: 219件（販売数）")
print("\n最新のCSVデータ:")
print(f"  - CASIO: {brand_counts.get('CASIO', 0)} 件（出品数）, {df[df['ブランド']=='CASIO']['販売数'].sum()} 件（販売数）")
print(f"  - SEIKO: {brand_counts.get('SEIKO', 0)} 件（出品数）, {df[df['ブランド']=='SEIKO']['販売数'].sum()} 件（販売数）")
print(f"  - Longines: {brand_counts.get('Longines', 0)} 件（出品数）, {df[df['ブランド']=='Longines']['販売数'].sum()} 件（販売数）")
print("\n⚠️ ギャップ:")
print("  - 全体分析タブのデータは古い（更新が必要）")
print("  - Longinesタブは大幅に古い（219 vs 2,946件）")
print("  - 全ブランドタブの再生成が必要")

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
