#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGAタブ v3 完全版
- 元CSVから正しくライン分類
- De Ville、Seamaster、Speedmaster等8ラインを分析
- 各ラインの人気モデルを正確に抽出
"""

import pandas as pd
import json
import re
import numpy as np

print("📄 OMEGAタブ v3 完全版再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_omega = df[(df['ブランド']=='OMEGA') & (df['商品状態']=='完品')].copy()

print(f"✓ OMEGA完品データ: {len(df_omega)}件")

# 完全なライン定義（優先順位順）
OMEGA_LINES = {
    'De Ville': ['DE VILLE', 'DEVILLE'],
    'Seamaster': ['SEAMASTER'],
    'Speedmaster': ['SPEEDMASTER'],
    'Constellation': ['CONSTELLATION'],
    'Geneve': ['GENEVE', 'GENEVA'],
    'Cosmic': ['COSMIC'],
    'Dynamic': ['DYNAMIC'],
    'Railmaster': ['RAILMASTER'],
}

def classify_omega_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in OMEGA_LINES.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return 'その他OMEGA'

def calculate_cv(prices):
    """変動係数を計算"""
    if len(prices) < 2:
        return 0
    mean = np.mean(prices)
    if mean == 0:
        return 0
    std = np.std(prices, ddof=1)
    return std / mean

def extract_model_number(title):
    """OMEGAの型番を抽出（4パターン対応）"""
    title_upper = str(title).upper()

    # パターン1: 3桁.2桁.2桁.2桁.2桁.3桁（例：121.92.41.50.01.001）
    pattern1 = r'\b\d{3}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{3}\b'
    match1 = re.search(pattern1, title_upper)
    if match1:
        return match1.group()

    # パターン2: 4桁.2桁（例：3510.12）← 最多パターン
    pattern2 = r'\b\d{4}\.\d{2}\b'
    match2 = re.search(pattern2, title_upper)
    if match2:
        return match2.group()

    # パターン3: 3桁.4桁.1桁（例：195.0076）
    pattern3 = r'\b\d{3}\.\d{4}\.\d\b'
    match3 = re.search(pattern3, title_upper)
    if match3:
        return match3.group()

    # パターン4: 3桁.4桁（例：166.0117）
    pattern4 = r'\b\d{3}\.\d{4}\b'
    match4 = re.search(pattern4, title_upper)
    if match4:
        return match4.group()

    return None

# タイトルを大文字化して処理
df_omega['タイトル_upper'] = df_omega['タイトル'].str.upper()

# ライン分類実行（通常）
df_omega['ライン'] = df_omega['タイトル_upper'].apply(classify_omega_line)

# 特徴・価値軸判定（別視点）
OMEGA_FEATURES = {
    'Vintage': ['VINTAGE', '1960', '1970', '1980', '1990'],
    'Co-Axial': ['CO-AXIAL', 'COAXIAL'],
    'Gold': ['GOLD', ' GP', ' YG', ' PG'],
    'Chronograph': ['CHRONOGRAPH', 'CHRONO'],
    'Chronometer': ['CHRONOMETER'],
    'Limited': ['LIMITED', 'SPECIAL EDITION'],
}

def detect_omega_feature(title_upper):
    """特徴を検出"""
    features = []
    for feature_name, keywords in OMEGA_FEATURES.items():
        for kw in keywords:
            if kw in title_upper:
                features.append(feature_name)
                break
    return ', '.join(features) if features else None

df_omega['特徴'] = df_omega['タイトル_upper'].apply(detect_omega_feature)
df_omega['特徴あり'] = df_omega['特徴'].notna()

# 型番を抽出
df_omega['型番'] = df_omega['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_omega['型番'].notna().sum()}件")

# ライン別集計
line_summary = []
for line in df_omega['ライン'].unique():
    df_line = df_omega[df_omega['ライン'] == line]
    count = len(df_line)
    avg_price = df_line['価格'].mean()
    cv = calculate_cv(df_line['価格'].values)
    line_summary.append({
        'ライン': line,
        '商品数': count,
        '平均価格': avg_price,
        '変動係数': cv
    })

line_summary = sorted(line_summary, key=lambda x: x['商品数'], reverse=True)

print("\n=== ライン別分類結果 ===")
for item in line_summary:
    pct = item['商品数'] / len(df_omega) * 100

    # 各ラインの人気モデルTop15を抽出
    df_line = df_omega[df_omega['ライン'] == item['ライン']]
    df_line_with_model = df_line[df_line['型番'].notna()]

    if len(df_line_with_model) > 0:
        model_counts = df_line_with_model.groupby('型番').agg({
            '販売数': 'sum',
            '価格': 'mean'
        }).reset_index()
        model_counts = model_counts.sort_values('販売数', ascending=False)
        top_models = len(model_counts[:15])
    else:
        top_models = 0

    print(f"{item['ライン']}: {item['商品数']}個 ({pct:.1f}%) - 人気モデル: {top_models}個（Top15まで抽出）")

# 特徴別集計
feature_summary = []
for feature_name in OMEGA_FEATURES.keys():
    df_feature = df_omega[df_omega['特徴'].notna() & df_omega['特徴'].str.contains(feature_name, na=False)]
    if len(df_feature) > 0:
        count = len(df_feature)
        avg_price = df_feature['価格'].mean()
        cv = calculate_cv(df_feature['価格'].values)
        feature_summary.append({
            '特徴': feature_name,
            '商品数': count,
            '平均価格': avg_price,
            '変動係数': cv
        })

feature_summary = sorted(feature_summary, key=lambda x: x['商品数'], reverse=True)

# 全ライン横断Top30を抽出
df_with_model = df_omega[df_omega['型番'].notna()].copy()
model_stats = df_with_model.groupby('型番').agg({
    '販売数': 'sum',
    '価格': 'mean',
    'タイトル': 'first',
    'ライン': 'first'
}).reset_index()
model_stats['count'] = df_with_model.groupby('型番').size().values
model_stats = model_stats.sort_values('count', ascending=False)[:30]

# === HTML生成 ===

# 1. 📊 詳細分析セクション
total_sales = df_omega['販売数'].sum()
avg_price = df_omega['価格'].mean()
cv = calculate_cv(df_omega['価格'].values)

html_stats = f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
        <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📦 完品商品数</div>
            <div style="font-size: 32px; font-weight: bold;">{len(df_omega)}</div>
        </div>
        <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📈 総販売数</div>
            <div style="font-size: 32px; font-weight: bold;">{total_sales}</div>
        </div>
        <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 平均落札価格</div>
            <div style="font-size: 32px; font-weight: bold;">¥{avg_price:,.0f}</div>
        </div>
        <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📊 価格変動係数</div>
            <div style="font-size: 32px; font-weight: bold;">{cv:.2f}</div>
        </div>
    </div>
</div>
"""

# 2. 🎯 仕入れ戦略
html_strategy = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">🎯 OMEGA 仕入れ戦略</h3>
<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
        <div style="padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-weight: bold; color: #667eea; margin-bottom: 8px;">🎯 主力ライン</div>
            <div style="font-size: 14px;">De Ville（34%）、Seamaster（32%）が市場の2/3を占有。Speedmaster（13%）も安定需要。</div>
        </div>
        <div style="padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #764ba2;">
            <div style="font-weight: bold; color: #764ba2; margin-bottom: 8px;">💎 価値軸</div>
            <div style="font-size: 14px;">Vintage（45%）が最大セグメント。Co-Axial、Chronometer等の高級機構も人気。</div>
        </div>
        <div style="padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-weight: bold; color: #667eea; margin-bottom: 8px;">🔍 仕入れポイント</div>
            <div style="font-size: 14px;">型番明記商品を優先。Seamaster・De Villeのヴィンテージモデルは高回転。</div>
        </div>
    </div>
</div>
"""

# 3. 📊 グラフセクション
html_graphs = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">📊 市場分析グラフ</h3>
<div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
        <div style="background: white; padding: 15px; border-radius: 8px;">
            <canvas id="omegaPriceDistChart"></canvas>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px;">
            <canvas id="omegaLineDistChart"></canvas>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px;">
            <canvas id="omegaFeatureDistChart"></canvas>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px;">
            <canvas id="omegaTopLinesChart"></canvas>
        </div>
    </div>
</div>
"""

# 4. 🔵 ライン別詳細分析
html_lines = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">🔵 ライン別詳細分析</h3>
<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <thead>
        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <th style="padding: 15px; text-align: left;">ライン名</th>
            <th style="padding: 15px; text-align: center;">商品数</th>
            <th style="padding: 15px; text-align: right;">平均価格</th>
            <th style="padding: 15px; text-align: center;">価格変動係数</th>
            <th style="padding: 15px; text-align: center;">検索</th>
        </tr>
    </thead>
    <tbody>
"""

for i, item in enumerate(line_summary):
    bg_color = "#f8f9fa" if i % 2 == 0 else "white"
    line_name = item['ライン']
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=OMEGA+{line_name.replace(' ', '+')}+Watch&LH_Sold=1"
    mercari_url = f"https://jp.mercari.com/search?keyword=OMEGA%20{line_name.replace(' ', '%20')}%20時計&status=on_sale"

    html_lines += f"""
        <tr style="background: {bg_color}; border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 12px;"><strong>{line_name}</strong></td>
            <td style="padding: 12px; text-align: center;">{item['商品数']}</td>
            <td style="padding: 12px; text-align: right;">¥{item['平均価格']:,.0f}</td>
            <td style="padding: 12px; text-align: center;">{item['変動係数']:.2f}</td>
            <td style="padding: 12px; text-align: center;">
                <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                <input type="checkbox" class="search-checkbox">
                <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                <input type="checkbox" class="search-checkbox">
            </td>
        </tr>
    """

html_lines += """
    </tbody>
</table>
</div>
"""

# 5. 🎭 特徴分析
html_features = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">🎭 特徴・価値軸分析</h3>
<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <thead>
        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <th style="padding: 15px; text-align: left;">特徴</th>
            <th style="padding: 15px; text-align: center;">商品数</th>
            <th style="padding: 15px; text-align: right;">平均価格</th>
            <th style="padding: 15px; text-align: center;">価格変動係数</th>
            <th style="padding: 15px; text-align: center;">検索</th>
        </tr>
    </thead>
    <tbody>
"""

for i, item in enumerate(feature_summary):
    bg_color = "#f8f9fa" if i % 2 == 0 else "white"
    feature_name = item['特徴']
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=OMEGA+{feature_name.replace(' ', '+')}+Watch&LH_Sold=1"
    mercari_url = f"https://jp.mercari.com/search?keyword=OMEGA%20{feature_name.replace(' ', '%20')}%20時計&status=on_sale"

    html_features += f"""
        <tr style="background: {bg_color}; border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 12px;"><strong>{feature_name}</strong></td>
            <td style="padding: 12px; text-align: center;">{item['商品数']}</td>
            <td style="padding: 12px; text-align: right;">¥{item['平均価格']:,.0f}</td>
            <td style="padding: 12px; text-align: center;">{item['変動係数']:.2f}</td>
            <td style="padding: 12px; text-align: center;">
                <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                <input type="checkbox" class="search-checkbox">
                <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                <input type="checkbox" class="search-checkbox">
            </td>
        </tr>
    """

html_features += """
    </tbody>
</table>
</div>
"""

# 6. 📌 各ラインTop15
html_line_top15 = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">📌 各ラインの人気モデルTop15</h3>
"""

for line in [item['ライン'] for item in line_summary if item['商品数'] >= 5]:
    df_line = df_omega[df_omega['ライン'] == line]
    df_line_with_model = df_line[df_line['型番'].notna()]

    if len(df_line_with_model) == 0:
        continue

    line_model_stats = df_line_with_model.groupby('型番').agg({
        '販売数': 'sum',
        '価格': 'mean',
        'タイトル': 'first'
    }).reset_index()
    line_model_stats['count'] = df_line_with_model.groupby('型番').size().values
    line_model_stats = line_model_stats.sort_values('count', ascending=False)[:15]

    html_line_top15 += f"""
<h4 style="color: #667eea; margin-top: 20px;">🔹 {line}</h4>
<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">
    <thead>
        <tr style="background: #667eea; color: white;">
            <th style="padding: 12px; text-align: center;">順位</th>
            <th style="padding: 12px; text-align: left;">型番</th>
            <th style="padding: 12px; text-align: left;">商品タイトル例</th>
            <th style="padding: 12px; text-align: center;">出品数</th>
            <th style="padding: 12px; text-align: right;">平均価格</th>
            <th style="padding: 12px; text-align: center;">検索</th>
        </tr>
    </thead>
    <tbody>
"""

    for rank, row in enumerate(line_model_stats.itertuples(), 1):
        bg_color = "#f8f9fa" if rank % 2 == 0 else "white"
        model = row.型番
        title_sample = row.タイトル[:50] + "..." if len(row.タイトル) > 50 else row.タイトル

        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=OMEGA+{model.replace('.', '+')}+Watch&LH_Sold=1"
        mercari_url = f"https://jp.mercari.com/search?keyword=OMEGA%20{model.replace('.', '%20')}%20時計&status=on_sale"

        html_line_top15 += f"""
        <tr style="background: {bg_color}; border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 10px; text-align: center;"><strong>{rank}</strong></td>
            <td style="padding: 10px;"><strong>{model}</strong></td>
            <td style="padding: 10px; font-size: 13px;">{title_sample}</td>
            <td style="padding: 10px; text-align: center;">{row.count}</td>
            <td style="padding: 10px; text-align: right;">¥{row.価格:,.0f}</td>
            <td style="padding: 10px; text-align: center; white-space: nowrap;">
                <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                <input type="checkbox" class="search-checkbox">
                <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                <input type="checkbox" class="search-checkbox">
            </td>
        </tr>
        """

    html_line_top15 += """
    </tbody>
</table>
</div>
"""

# 7. 🏆 全ライン横断Top30（最後）
html_top30 = """
<h3 style="color: #667eea; border-left: 5px solid #667eea; padding-left: 15px; margin-top: 30px;">🏆 全ライン横断 人気モデルTop30</h3>
<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <thead>
        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <th style="padding: 15px; text-align: center;">順位</th>
            <th style="padding: 15px; text-align: left;">型番</th>
            <th style="padding: 15px; text-align: left;">ライン</th>
            <th style="padding: 15px; text-align: left;">商品タイトル例</th>
            <th style="padding: 15px; text-align: center;">出品数</th>
            <th style="padding: 15px; text-align: right;">平均価格</th>
            <th style="padding: 15px; text-align: center;">検索</th>
        </tr>
    </thead>
    <tbody>
"""

for rank, row in enumerate(model_stats.itertuples(), 1):
    bg_color = "#f8f9fa" if rank % 2 == 0 else "white"
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""

    model = row.型番
    line = row.ライン
    title_sample = row.タイトル[:50] + "..." if len(row.タイトル) > 50 else row.タイトル

    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=OMEGA+{model.replace('.', '+')}+Watch&LH_Sold=1"
    mercari_url = f"https://jp.mercari.com/search?keyword=OMEGA%20{model.replace('.', '%20')}%20時計&status=on_sale"

    html_top30 += f"""
        <tr style="background: {bg_color}; border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 12px; text-align: center;"><strong>{medal} {rank}</strong></td>
            <td style="padding: 12px;"><strong>{model}</strong></td>
            <td style="padding: 12px;">{line}</td>
            <td style="padding: 12px; font-size: 13px;">{title_sample}</td>
            <td style="padding: 12px; text-align: center;">{row.count}</td>
            <td style="padding: 12px; text-align: right;">¥{row.価格:,.0f}</td>
            <td style="padding: 12px; text-align: center; white-space: nowrap;">
                <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                <input type="checkbox" class="search-checkbox">
                <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                <input type="checkbox" class="search-checkbox">
            </td>
        </tr>
    """

html_top30 += """
    </tbody>
</table>
</div>
"""

# グラフのスクリプト生成（ドル建て価格用）
price_ranges = ['~$200', '$200-500', '$500-1K', '$1K-2K', '$2K~']
price_counts = [
    len(df_omega[df_omega['価格'] < 200]),
    len(df_omega[(df_omega['価格'] >= 200) & (df_omega['価格'] < 500)]),
    len(df_omega[(df_omega['価格'] >= 500) & (df_omega['価格'] < 1000)]),
    len(df_omega[(df_omega['価格'] >= 1000) & (df_omega['価格'] < 2000)]),
    len(df_omega[df_omega['価格'] >= 2000])
]

line_names = [item['ライン'] for item in line_summary[:8]]
line_counts = [item['商品数'] for item in line_summary[:8]]

feature_names = [item['特徴'] for item in feature_summary]
feature_counts = [item['商品数'] for item in feature_summary]

top7_lines = [item['ライン'] for item in line_summary[:7]]
top7_sales = []
for line in top7_lines:
    df_line = df_omega[df_omega['ライン'] == line]
    top7_sales.append(int(df_line['販売数'].sum()))

graph_script = f"""
<script>
// OMEGA 価格帯別分布
new Chart(document.getElementById('omegaPriceDistChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(price_ranges)},
        datasets: [{{
            label: '商品数',
            data: {json.dumps(price_counts)},
            backgroundColor: 'rgba(102, 126, 234, 0.8)'
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'OMEGA 価格帯別分布' }}
        }}
    }}
}});

// OMEGA ライン別分布
new Chart(document.getElementById('omegaLineDistChart'), {{
    type: 'pie',
    data: {{
        labels: {json.dumps(line_names)},
        datasets: [{{
            data: {json.dumps(line_counts)},
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(118, 75, 162, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)'
            ]
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'OMEGA ライン別分布' }}
        }}
    }}
}});

// OMEGA 特徴別分布
new Chart(document.getElementById('omegaFeatureDistChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(feature_names)},
        datasets: [{{
            label: '商品数',
            data: {json.dumps(feature_counts)},
            backgroundColor: 'rgba(118, 75, 162, 0.8)'
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'OMEGA 特徴別分布' }}
        }}
    }}
}});

// OMEGA Top7ライン売上
new Chart(document.getElementById('omegaTopLinesChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(top7_lines)},
        datasets: [{{
            label: '販売数',
            data: {json.dumps(top7_sales)},
            backgroundColor: 'rgba(102, 126, 234, 0.8)'
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: 'OMEGA Top7ライン販売数' }}
        }}
    }}
}});
</script>
"""

# 全セクションを結合
omega_content = f"""
<h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-top: 30px;">🟣 OMEGA 詳細分析</h2>
{html_stats}
{html_strategy}
{html_graphs}
{html_lines}
{html_features}
{html_line_top15}
{html_top30}

{graph_script}
"""

# === HTML置換 ===

# RADOタブの終了位置を探す
rado_start = html.find('<div id="RADO" class="tab-content">')
if rado_start == -1:
    print("❌ エラー: RADOタブが見つかりません")
    exit(1)

# ネストカウントでRADOタブの終了</div>を特定
div_count = 1
search_pos = rado_start + len('<div id="RADO" class="tab-content">')
body_pos = html.find('</body>')

while div_count > 0 and search_pos < body_pos:
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: RADOタブの閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            rado_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

# OMEGAタブを挿入
omega_tab_html = f"""
<div id="OMEGA" class="tab-content">
{omega_content}
</div>

"""

html = html[:rado_end] + omega_tab_html + html[rado_end:]

# HTMLを保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ OMEGAタブ v3 完全版完成！")
print(f"📦 ファイルサイズ: {len(html)} bytes ({len(html)/1024:.1f} KB)")
print(f"🎯 改善内容:")
print(f"  ✓ 元CSVから正確にライン分類")
print(f"  ✓ 8ラインを認識（De Ville、Seamaster、Speedmaster等）")
print(f"  ✓ 各ラインの実際の人気モデルTop15を抽出")
print(f"  ✓ 特徴・価値軸分析を追加（Vintage、Co-Axial等）")
print(f"  ✓ 商品タイトルサンプルを表示")
print(f"  ✓ 全セクションに検索リンク + チェックボックス追加")
