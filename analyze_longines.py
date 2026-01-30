#!/usr/bin/env python3
"""Longinesデータの詳細分析"""

import pandas as pd
import numpy as np

# CSVファイルを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# Longinesデータを抽出（完品のみ）
longines = df[(df['ブランド'] == 'Longines') & (df['商品状態'] == '完品')].copy()

print(f'=== CSVデータ: Longines完品のみ ===')
print(f'総件数: {len(longines):,}')
print(f'総販売数: {int(longines["販売数"].sum()):,}')
print(f'平均価格: ${longines["価格"].mean():.2f}')
print(f'中央値: ${longines["価格"].median():.2f}')
print(f'最低価格: ${longines["価格"].min():.2f}')
print(f'最高価格: ${longines["価格"].max():.2f}')

# CV値計算
cv = longines["価格"].std() / longines["価格"].mean()
print(f'CV値: {cv:.3f}')

# 駆動方式別
print(f'\n=== 駆動方式別 ===')
drive_stats = longines.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
for drive, sales in drive_stats.head(5).items():
    pct = sales / longines['販売数'].sum() * 100
    print(f'{drive}: {int(sales):,}個 ({pct:.1f}%)')

# ライン分類（タイトルから抽出）
print(f'\n=== ライン別（推定） ===')
lines = {
    'Conquest': longines[longines['タイトル'].str.contains('Conquest', case=False, na=False)]['販売数'].sum(),
    'Flagship': longines[longines['タイトル'].str.contains('Flagship', case=False, na=False)]['販売数'].sum(),
    'Heritage': longines[longines['タイトル'].str.contains('Heritage', case=False, na=False)]['販売数'].sum(),
    'DolceVita': longines[longines['タイトル'].str.contains('DolceVita|Dolce Vita', case=False, na=False)]['販売数'].sum(),
    'Spirit': longines[longines['タイトル'].str.contains('Spirit', case=False, na=False)]['販売数'].sum(),
    'HydroConquest': longines[longines['タイトル'].str.contains('HydroConquest|Hydro Conquest', case=False, na=False)]['販売数'].sum(),
}
total_line_sales = sum(lines.values())
other_sales = longines['販売数'].sum() - total_line_sales
lines['その他Longines'] = other_sales

for line, sales in sorted(lines.items(), key=lambda x: x[1], reverse=True):
    if sales > 0:
        pct = sales / longines['販売数'].sum() * 100
        print(f'{line}: {int(sales):,}個 ({pct:.1f}%)')

# 型番抽出率
has_model = longines['型番'].notna() & (longines['型番'] != 'N/A')
model_count = longines[has_model].shape[0]
model_rate = model_count / len(longines) * 100
print(f'\n=== 型番抽出 ===')
print(f'型番あり: {model_count:,}件 / {len(longines):,}件 ({model_rate:.1f}%)')

# Top10型番
print(f'\n=== Top10型番（販売数） ===')
top_models = longines[has_model].groupby('型番')['販売数'].sum().sort_values(ascending=False).head(10)
for i, (model, sales) in enumerate(top_models.items(), 1):
    # 中央値も表示
    median_price = longines[longines['型番'] == model]['価格'].median()
    print(f'{i}. {model}: {int(sales):,}個 (中央値: ${median_price:.2f})')

# 性別分布
print(f'\n=== 性別分布 ===')
if 'Department' in longines.columns:
    gender_stats = longines.groupby('Department')['販売数'].sum().sort_values(ascending=False)
    for gender, sales in gender_stats.items():
        pct = sales / longines['販売数'].sum() * 100
        print(f'{gender}: {int(sales):,}個 ({pct:.1f}%)')
