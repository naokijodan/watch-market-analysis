#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブランド詳細分析.json を CSVから再生成するスクリプト
rebuild_*_v3_complete.py スクリプト群が依存するJSONファイルを生成
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from collections import Counter

print("=" * 80)
print("ブランド詳細分析.json 再生成")
print("=" * 80)

# CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
print(f"✓ CSV読み込み: {len(df)}件")

# 完品データ
df_clean = df[df['商品状態'] == '完品'].copy()

# USD→JPY レート
JPY_RATE = 155

def extract_model_number(title, brand):
    """タイトルから型番を抽出"""
    patterns = {
        'SEIKO': r'(SPB\d{3}|SBDC\d{3}|SARB\d{3}|SNK\d{3}|SRPD?\d{2,3}|SSC\d{3}|SUR\d{3}|SNXS?\d{2,3}|SNA\d{3}|SKX\d{3}|SBDX\d{3}|SARX\d{3}|SBGX?\d{3}|SRP\d{3}|SNZG?\d{2}|SNKE?\d{2}|SBBN\d{3})',
        'CASIO': r'(G[A-Z]?[WMS]?-?\d{3,5}[A-Z]*|DW-?\d{4}[A-Z]*|GW[A-Z]?-?\d{4,5}[A-Z]*|GA[A-Z]?-?\d{3,4}[A-Z]*|MTP-?\d{4}[A-Z]*|EF[A-Z]?-?\d{3}[A-Z]*|PRG-?\d{3}[A-Z]*|OCW-?\d{2,4}[A-Z]*)',
        'OMEGA': r'([\d\.]+/[\d\.]+|Ref\.?\s*[\d\.]+)',
        'CITIZEN': r'(BN\d{4}|BJ\d{4}|AT\d{4}|CB\d{4}|BL\d{4}|AW\d{4}|NH\d{4}|NJ\d{4})',
        'Orient': r'(FAC\d{5}|RA-[A-Z]{2}\d{4}|FER\d{5}|SAA\d{5})',
        'TAG HEUER': r'(WAR\d{3,4}|WAZ\d{4}|CAR\d{3,4}|WBD\d{4}|CBN\d{4})',
        'GUCCI': r'(YA\d{3,6})',
        'ROLEX': r'(\d{4,6})',
        'Hamilton': r'(H\d{8})',
        'Longines': r'(L[\d\.]+)',
        'Cartier': r'(W\d{7}|WSTA\d{4})',
        'RADO': r'(R\d{8}|01\.\d{3}\.\d{4})',
    }
    pattern = patterns.get(brand, r'([A-Z]{2,4}[\-]?\d{3,6}[A-Z]*)')
    match = re.search(pattern, str(title), re.IGNORECASE)
    return match.group(1) if match else None


def calc_brand_stats(df_brand, df_brand_clean, brand):
    """ブランド別の統計情報を計算"""
    stats = {}
    stats['total_records'] = len(df_brand)
    stats['clean_records'] = len(df_brand_clean)
    stats['total_sales'] = int(df_brand_clean['販売数'].sum()) if '販売数' in df_brand_clean.columns else len(df_brand_clean)

    prices = df_brand_clean['価格'].dropna()
    stats['median_price'] = float(prices.median()) if len(prices) > 0 else 0
    stats['mean_price'] = float(prices.mean()) if len(prices) > 0 else 0
    stats['std_price'] = float(prices.std()) if len(prices) > 1 else 0
    stats['cv'] = round(stats['std_price'] / stats['mean_price'], 2) if stats['mean_price'] > 0 else 0
    stats['min_price'] = float(prices.min()) if len(prices) > 0 else 0
    stats['max_price'] = float(prices.max()) if len(prices) > 0 else 0

    # 価格帯分布
    price_segments = {}
    if len(prices) > 0:
        entry = prices[prices < 100]
        mid = prices[(prices >= 100) & (prices < 500)]
        high = prices[prices >= 500]
        price_segments['エントリー'] = {'count': len(entry), 'ratio': round(len(entry)/len(prices)*100, 1)}
        price_segments['ミドル'] = {'count': len(mid), 'ratio': round(len(mid)/len(prices)*100, 1)}
        price_segments['ハイエンド'] = {'count': len(high), 'ratio': round(len(high)/len(prices)*100, 1)}
    stats['price_segments'] = price_segments

    # 駆動方式分布
    if '駆動方式' in df_brand_clean.columns:
        movement_dist = df_brand_clean['駆動方式'].value_counts().to_dict()
        stats['movement_distribution'] = {k: int(v) for k, v in movement_dist.items()}
    else:
        stats['movement_distribution'] = {}

    # デパートメント分布
    if 'デパートメント' in df_brand_clean.columns:
        dept_dist = df_brand_clean['デパートメント'].value_counts().to_dict()
        stats['department_distribution'] = {k: int(v) for k, v in dept_dist.items()}
    else:
        stats['department_distribution'] = {}

    # JDM分析
    jdm_mask = df_brand_clean['タイトル'].str.contains('JDM|Japan Domestic|日本製|Made in Japan', case=False, na=False)
    jdm_count = jdm_mask.sum()
    stats['jdm_count'] = int(jdm_count)
    if jdm_count > 0 and len(prices) > 0:
        jdm_median = df_brand_clean.loc[jdm_mask, '価格'].median()
        non_jdm_median = df_brand_clean.loc[~jdm_mask, '価格'].median()
        stats['jdm_premium'] = round((jdm_median / non_jdm_median - 1) * 100, 1) if non_jdm_median > 0 else 0
    else:
        stats['jdm_premium'] = 0

    # ヴィンテージ分析
    vintage_mask = df_brand_clean['タイトル'].str.contains('Vintage|ヴィンテージ|ビンテージ|Antique', case=False, na=False)
    stats['vintage_count'] = int(vintage_mask.sum())
    if vintage_mask.sum() > 0 and len(prices) > 0:
        v_median = df_brand_clean.loc[vintage_mask, '価格'].median()
        nv_median = df_brand_clean.loc[~vintage_mask, '価格'].median()
        stats['vintage_premium'] = round((v_median / nv_median - 1) * 100, 1) if nv_median > 0 else 0
    else:
        stats['vintage_premium'] = 0

    # 箱付き分析
    box_mask = df_brand_clean['タイトル'].str.contains('Box|箱付|With Box', case=False, na=False)
    stats['box_count'] = int(box_mask.sum())
    if box_mask.sum() > 0 and len(prices) > 0:
        b_median = df_brand_clean.loc[box_mask, '価格'].median()
        nb_median = df_brand_clean.loc[~box_mask, '価格'].median()
        stats['box_premium'] = round((b_median / nb_median - 1) * 100, 1) if nb_median > 0 else 0
    else:
        stats['box_premium'] = 0

    # 型番別統計（Top30）
    df_brand_clean = df_brand_clean.copy()
    df_brand_clean['型番'] = df_brand_clean['タイトル'].apply(lambda t: extract_model_number(t, brand))
    model_groups = df_brand_clean.dropna(subset=['型番']).groupby('型番')

    model_stats = []
    for model, group in model_groups:
        if len(group) >= 2:
            prices_g = group['価格']
            sales = int(group['販売数'].sum()) if '販売数' in group.columns else len(group)
            jpy = int(prices_g.median() * JPY_RATE)
            model_stats.append({
                'model': model,
                'count': sales,
                'transactions': len(group),
                'min': float(prices_g.min()),
                'max': float(prices_g.max()),
                'median': float(prices_g.median()),
                'cv': float(prices_g.std() / prices_g.mean()) if prices_g.mean() > 0 else 0,
                'jpy': jpy,
                'breakeven': int(jpy * 0.722)
            })

    model_stats.sort(key=lambda x: x['count'], reverse=True)
    stats['model_stats'] = model_stats[:30]

    return stats


# 全ブランドの統計を計算
brands = df['ブランド'].unique()
brand_data = {}

for brand in brands:
    df_brand = df[df['ブランド'] == brand]
    df_brand_clean = df_clean[df_clean['ブランド'] == brand]
    if len(df_brand_clean) >= 5:  # 最低5件のデータがあるブランドのみ
        brand_data[brand] = calc_brand_stats(df_brand, df_brand_clean, brand)
        print(f"  ✓ {brand}: {brand_data[brand]['clean_records']}件 (販売数: {brand_data[brand]['total_sales']})")

# パーツデータ
parts_by_brand = {}
df_parts = df[df['商品状態'] != '完品']
for brand in brands:
    df_bp = df_parts[df_parts['ブランド'] == brand]
    if len(df_bp) > 0:
        parts_by_brand[brand] = {
            'count': len(df_bp),
            'total_sales': int(df_bp['販売数'].sum()) if '販売数' in df_bp.columns else len(df_bp)
        }

# 結果を保存
output = {
    'brands': brand_data,
    'parts_by_brand': parts_by_brand,
    'config': {
        'jpy_rate': JPY_RATE,
        'min_transactions': 2,
        'top_models': 30
    },
    'generated_at': datetime.now().isoformat()
}

output_path = '/Users/naokijodan/Desktop/ブランド詳細分析.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 保存完了: {output_path}")
print(f"   ブランド数: {len(brand_data)}")
