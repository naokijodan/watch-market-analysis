#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時計市場データ深掘り分析スクリプト v3.5
- SEIKO/CASIO/CITIZENのライン別分析
- 駆動方式別の詳細市場構造分析
"""

import pandas as pd
import json
import numpy as np
from collections import defaultdict
import re

# SEIKOライン定義
SEIKO_LINES = {
    'Grand Seiko': ['GRAND SEIKO', 'GS ', 'SBGR', 'SBGA', 'SBGM', 'SBGX'],
    'SEIKO 5': ['SEIKO 5', 'SEIKO5', '5 SPORTS', 'SNZG', 'SNK', 'SRPD'],
    'Prospex': ['PROSPEX', 'SBDC', 'SBDN', 'SPB', 'SRP'],
    'Presage': ['PRESAGE', 'SARY', 'SRPB', 'SSA', 'SRPE'],
    'Astron': ['ASTRON', 'SSE'],
    'King Seiko': ['KING SEIKO'],
    'Lord Marvel': ['LORD MARVEL'],
    'Dolce': ['DOLCE'],
    'Chariot': ['CHARIOT'],
}

# CASIOライン定義
CASIO_LINES = {
    'G-SHOCK': ['G-SHOCK', 'GSHOCK', 'G SHOCK', 'DW-', 'GA-', 'GW-', 'GMW-', 'GBD-', 'GST-', 'MTG-'],
    'BABY-G': ['BABY-G', 'BABY G', 'BABYG', 'BG-', 'BGA-', 'BGD-'],
    'PRO TREK': ['PRO TREK', 'PROTREK', 'PRW-', 'PRG-', 'PRT-'],
    'OCEANUS': ['OCEANUS', 'OCW-'],
    'EDIFICE': ['EDIFICE', 'EF-', 'EQB-', 'ECB-'],
    'LINEAGE': ['LINEAGE', 'LCW-', 'LIW-'],
    'SHEEN': ['SHEEN', 'SHE-'],
}

# CITIZENライン定義
CITIZEN_LINES = {
    'Promaster': ['PROMASTER', 'プロマスター', 'BN', 'JY', 'JV'],
    'Attesa': ['ATTESA', 'アテッサ', 'AT', 'CB', 'CC'],
    'Exceed': ['EXCEED', 'エクシード', 'EBS', 'EBG'],
    'The CITIZEN': ['THE CITIZEN'],
    'Collection': ['COLLECTION'],
    'Eco-Drive One': ['ECO-DRIVE ONE', 'AR5'],
    'Chandler': ['CHANDLER'],
}

def extract_line(title_upper, brand, line_dict):
    """ライン名を抽出"""
    for line_name, keywords in line_dict.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return f'その他{brand}'

def calculate_cv(prices):
    """変動係数（CV）を計算"""
    if len(prices) < 2:
        return 0
    mean = np.mean(prices)
    if mean == 0:
        return 0
    std = np.std(prices, ddof=1)
    return std / mean

def calculate_price_distribution(prices, bins=6):
    """価格帯分布を計算"""
    bin_edges = [0, 100, 200, 300, 500, 1000, 10000]
    bin_labels = ['$0-100', '$100-200', '$200-300', '$300-500', '$500-1000', '$1000+']

    counts = []
    for i in range(len(bin_edges) - 1):
        count = len([p for p in prices if bin_edges[i] <= p < bin_edges[i+1]])
        counts.append(count)

    return dict(zip(bin_labels, counts))

print("📊 時計市場データ深掘り分析開始...")

# CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df['販売日'] = pd.to_datetime(df['販売日'])
print(f"✓ データ読み込み完了: {len(df)}件")

# 完品のみ抽出
df_complete = df[df['商品状態']=='完品'].copy()
print(f"✓ 完品データ: {len(df_complete)}件")

# === 1. SEIKOライン別分析 ===
print("\n🔵 SEIKO ライン別分析中...")
df_seiko = df_complete[df_complete['ブランド']=='SEIKO'].copy()
df_seiko['ライン'] = df_seiko['タイトル_upper'].apply(lambda x: extract_line(x, 'SEIKO', SEIKO_LINES))

seiko_lines = {}
for line, group in df_seiko.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    # 駆動方式分布
    movement_dist = group['駆動方式'].value_counts().to_dict()

    # JDM分析
    jdm_count = (group['JDM']==True).sum()
    jdm_median = group[group['JDM']==True]['価格'].median() if jdm_count > 0 else 0
    non_jdm_median = group[group['JDM']==False]['価格'].median() if len(group[group['JDM']==False]) > 0 else 0
    jdm_premium = ((jdm_median - non_jdm_median) / non_jdm_median * 100) if non_jdm_median > 0 and jdm_count >= 2 else 0

    # 型番別Top5
    model_stats = []
    if '型番' in group.columns:
        for model, model_group in group.groupby('型番'):
            if pd.isna(model) or model == '' or len(model_group) < 2:
                continue
            model_sales = model_group['販売数'].sum()
            if model_sales >= 2:
                model_stats.append({
                    'model': model,
                    'count': int(model_sales),
                    'median': float(model_group['価格'].median()),
                    'cv': float(calculate_cv(model_group['価格'].values))
                })

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:5]

    seiko_lines[line] = {
        'count': int(sales),
        'items': len(group),
        'median': float(np.median(prices)),
        'mean': float(np.mean(prices)),
        'cv': float(calculate_cv(prices)),
        'min': float(np.min(prices)),
        'max': float(np.max(prices)),
        'movement_distribution': movement_dist,
        'jdm_count': int(jdm_count),
        'jdm_premium': float(jdm_premium),
        'price_distribution': calculate_price_distribution(prices),
        'top_models': model_stats
    }

print(f"  ✓ {len(seiko_lines)}ライン分析完了")

# === 2. CASIOライン別分析 ===
print("\n🟢 CASIO ライン別分析中...")
df_casio = df_complete[df_complete['ブランド']=='CASIO'].copy()
df_casio['ライン'] = df_casio['タイトル_upper'].apply(lambda x: extract_line(x, 'CASIO', CASIO_LINES))

casio_lines = {}
for line, group in df_casio.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    movement_dist = group['駆動方式'].value_counts().to_dict()

    jdm_count = (group['JDM']==True).sum()
    jdm_median = group[group['JDM']==True]['価格'].median() if jdm_count > 0 else 0
    non_jdm_median = group[group['JDM']==False]['価格'].median() if len(group[group['JDM']==False]) > 0 else 0
    jdm_premium = ((jdm_median - non_jdm_median) / non_jdm_median * 100) if non_jdm_median > 0 and jdm_count >= 2 else 0

    # コラボ・限定判定（G-SHOCK用）
    if line == 'G-SHOCK':
        collab_count = group['タイトル_upper'].str.contains('×|COLLABORATION|COLLAB', na=False).sum()
        limited_count = group['タイトル_upper'].str.contains('LIMITED|EDITION|限定', na=False).sum()
    else:
        collab_count = 0
        limited_count = 0

    model_stats = []
    if '型番' in group.columns:
        for model, model_group in group.groupby('型番'):
            if pd.isna(model) or model == '' or len(model_group) < 2:
                continue
            model_sales = model_group['販売数'].sum()
            if model_sales >= 2:
                model_stats.append({
                    'model': model,
                    'count': int(model_sales),
                    'median': float(model_group['価格'].median()),
                    'cv': float(calculate_cv(model_group['価格'].values))
                })

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:10 if line == 'G-SHOCK' else 5]

    casio_lines[line] = {
        'count': int(sales),
        'items': len(group),
        'median': float(np.median(prices)),
        'mean': float(np.mean(prices)),
        'cv': float(calculate_cv(prices)),
        'min': float(np.min(prices)),
        'max': float(np.max(prices)),
        'movement_distribution': movement_dist,
        'jdm_count': int(jdm_count),
        'jdm_premium': float(jdm_premium),
        'collab_count': int(collab_count),
        'limited_count': int(limited_count),
        'price_distribution': calculate_price_distribution(prices),
        'top_models': model_stats
    }

print(f"  ✓ {len(casio_lines)}ライン分析完了")

# === 3. CITIZENライン別分析 ===
print("\n🟠 CITIZEN ライン別分析中...")
df_citizen = df_complete[df_complete['ブランド']=='CITIZEN'].copy()
df_citizen['ライン'] = df_citizen['タイトル_upper'].apply(lambda x: extract_line(x, 'CITIZEN', CITIZEN_LINES))

# Eco-Drive判定
df_citizen['Eco-Drive'] = df_citizen['タイトル_upper'].str.contains('ECO-DRIVE|ECO DRIVE|ECODRIVE', na=False)

citizen_lines = {}
for line, group in df_citizen.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    movement_dist = group['駆動方式'].value_counts().to_dict()

    jdm_count = (group['JDM']==True).sum()
    jdm_median = group[group['JDM']==True]['価格'].median() if jdm_count > 0 else 0
    non_jdm_median = group[group['JDM']==False]['価格'].median() if len(group[group['JDM']==False]) > 0 else 0
    jdm_premium = ((jdm_median - non_jdm_median) / non_jdm_median * 100) if non_jdm_median > 0 and jdm_count >= 2 else 0

    # Eco-Drive分析
    eco_count = (group['Eco-Drive']==True).sum()
    eco_median = group[group['Eco-Drive']==True]['価格'].median() if eco_count > 0 else 0
    non_eco_median = group[group['Eco-Drive']==False]['価格'].median() if len(group[group['Eco-Drive']==False]) > 0 else 0
    eco_premium = ((eco_median - non_eco_median) / non_eco_median * 100) if non_eco_median > 0 and eco_count >= 2 else 0

    model_stats = []
    if '型番' in group.columns:
        for model, model_group in group.groupby('型番'):
            if pd.isna(model) or model == '' or len(model_group) < 2:
                continue
            model_sales = model_group['販売数'].sum()
            if model_sales >= 2:
                model_stats.append({
                    'model': model,
                    'count': int(model_sales),
                    'median': float(model_group['価格'].median()),
                    'cv': float(calculate_cv(model_group['価格'].values))
                })

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:5]

    citizen_lines[line] = {
        'count': int(sales),
        'items': len(group),
        'median': float(np.median(prices)),
        'mean': float(np.mean(prices)),
        'cv': float(calculate_cv(prices)),
        'min': float(np.min(prices)),
        'max': float(np.max(prices)),
        'movement_distribution': movement_dist,
        'jdm_count': int(jdm_count),
        'jdm_premium': float(jdm_premium),
        'eco_drive_count': int(eco_count),
        'eco_drive_premium': float(eco_premium),
        'price_distribution': calculate_price_distribution(prices),
        'top_models': model_stats
    }

print(f"  ✓ {len(citizen_lines)}ライン分析完了")

# === 4. 駆動方式別詳細分析 ===
print("\n⚙️ 駆動方式別詳細分析中...")
movement_details = {}

for movement, group in df_complete.groupby('駆動方式'):
    if movement in ['不明', ''] or len(group) < 10:
        continue

    # ブランド別ランキングTop15
    brand_ranking = []
    for brand, brand_group in group.groupby('ブランド'):
        if brand == '(不明)' or pd.isna(brand):
            continue
        sales = brand_group['販売数'].sum()
        if sales < 3:
            continue

        brand_ranking.append({
            'brand': brand,
            'count': int(sales),
            'median': float(brand_group['価格'].median()),
            'cv': float(calculate_cv(brand_group['価格'].values)),
            'items': len(brand_group)
        })

    brand_ranking = sorted(brand_ranking, key=lambda x: x['count'], reverse=True)[:15]

    # 価格帯分布
    prices = group['価格'].values
    price_dist = calculate_price_distribution(prices)

    # 売れ筋価格帯（中央値±25%）
    median = np.median(prices)
    lower = median * 0.75
    upper = median * 1.25
    bestseller_count = len([p for p in prices if lower <= p <= upper])
    bestseller_ratio = bestseller_count / len(prices) * 100

    # 月別推移
    monthly_data = group.groupby(group['販売日'].dt.to_period('M'))['販売数'].sum().to_dict()
    monthly_list = [{'month': str(k), 'count': int(v)} for k, v in monthly_data.items()]

    movement_details[movement] = {
        'total_count': int(group['販売数'].sum()),
        'total_items': len(group),
        'median': float(median),
        'brand_ranking': brand_ranking,
        'price_distribution': price_dist,
        'bestseller_range': f'${lower:.0f}-${upper:.0f}',
        'bestseller_ratio': float(bestseller_ratio),
        'monthly_trend': monthly_list
    }

print(f"  ✓ {len(movement_details)}種類の駆動方式分析完了")

# === 5. 統合データ作成 ===
integrated_data = {
    'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
    'seiko_lines': seiko_lines,
    'casio_lines': casio_lines,
    'citizen_lines': citizen_lines,
    'movement_details': movement_details
}

# JSON保存
output_path = '/Users/naokijodan/Desktop/時計分析_深掘り版.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(integrated_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 深掘り分析完了！ {output_path} に保存しました")
print(f"\n【サマリー】")
print(f"  SEIKO: {len(seiko_lines)}ライン")
print(f"  CASIO: {len(casio_lines)}ライン")
print(f"  CITIZEN: {len(citizen_lines)}ライン")
print(f"  駆動方式: {len(movement_details)}種類")
