#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BREITLINGタブ作成スクリプト（template_brand_tab.py準拠）
================================================================================
template_brand_tab.pyのTODO箇所のみ変更したBREITLING専用スクリプト
"""

import pandas as pd
import json
import re
import numpy as np

# TODO 1: ブランド名を変更
BRAND_NAME = 'BREITLING'
brand_name_lower = BRAND_NAME.lower()

print(f"📄 {BRAND_NAME}タブ v3 完全版再構築開始...")

# ===== データ読み込み =====
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# ブランド名でフィルタ
df_brand = df[(df['ブランド']==BRAND_NAME) & (df['商品状態']=='完品')].copy()

print(f"✓ {BRAND_NAME}完品データ: {len(df_brand)}件")

# ===== TODO 2: ライン定義（最重要！） =====
# BREITLING固有のライン定義（優先順位順）
BRAND_LINES = {
    'Navitimer': ['NAVITIMER'],
    'Superocean': ['SUPEROCEAN', 'SUPER OCEAN'],
    'Chronomat': ['CHRONOMAT'],
    'Avenger': ['AVENGER'],
    'Colt': ['COLT'],
    'Transocean': ['TRANSOCEAN'],
    'Bentley': ['BENTLEY'],
    'Galactic': ['GALACTIC'],
    'Montbrillant': ['MONTBRILLANT'],
}

def classify_brand_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in BRAND_LINES.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return f'その他{BRAND_NAME}'

# ===== ユーティリティ関数 =====

def calculate_cv(prices):
    """変動係数を計算"""
    if len(prices) < 2:
        return 0
    mean = np.mean(prices)
    if mean == 0:
        return 0
    std = np.std(prices, ddof=1)
    return std / mean

# TODO 3: 型番抽出関数（BREITLING固有）
def extract_model_number(title):
    """BREITLINGの型番を抽出
    Pattern 1: A/B/C/D/E + 5桁（例: A17378, B13019, A21330）
    Pattern 2: AB/UB + 4桁（例: AB0121, UB0136）
    Pattern 3: 長い形式（例: A179G91PRS）
    """
    title_upper = str(title).upper()

    # Pattern 1: A/B/C/D/E + 5桁
    match = re.search(r'\b([ABCDE]\d{5})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 2: AB/UB + 4桁
    match = re.search(r'\b([AU]B\d{4})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 3: 長い形式（A + 3桁 + 英字 + 2桁 + 英字3桁）
    match = re.search(r'\b([A-Z]\d{3}[A-Z]\d{2}[A-Z]{3})\b', title_upper)
    if match:
        return match.group(1)

    return None

# ===== タイトルを大文字化 =====
df_brand['タイトル_upper'] = df_brand['タイトル'].str.upper()

# ===== ライン分類実行 =====
df_brand['ライン'] = df_brand['タイトル_upper'].apply(classify_brand_line)

# ===== TODO 4: キャラクター/コラボ判定（Swatch固有：コラボ・アート系） =====
BRAND_CHARACTERS = {
    'Limited Edition': ['LIMITED EDITION', 'LIMITED', 'SPECIAL EDITION'],
    'Blackbird': ['BLACKBIRD'],
    'Steelfish': ['STEELFISH'],
    'Skyland': ['SKYLAND'],
    'Crosswind': ['CROSSWIND'],
    'Emergency': ['EMERGENCY'],
    'Aerospace': ['AEROSPACE'],
}

def detect_brand_character(title_upper):
    """キャラクター/コラボを検出"""
    for character_name, keywords in BRAND_CHARACTERS.items():
        for kw in keywords:
            if kw in title_upper:
                return character_name
    return None

df_brand['キャラクター'] = df_brand['タイトル_upper'].apply(detect_brand_character)
df_brand_character = df_brand[df_brand['キャラクター'].notna()].copy()

# ===== 型番抽出 =====
df_brand['型番抽出'] = df_brand['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_brand['型番抽出'].notna().sum()}件 / {len(df_brand)}件 ({df_brand['型番抽出'].notna().sum()/len(df_brand)*100:.1f}%)")

# ===== ライン別統計を計算 =====
line_stats = {}
line_models_dict = {}
total_line_sales = df_brand['販売数'].sum()

for line, group in df_brand.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    # 型番別Top15を抽出
    model_stats = []
    model_group = group[group['型番抽出'].notna()].copy()

    if len(model_group) > 0:
        for model, mg in model_group.groupby('型番抽出'):
            model_sales = mg['販売数'].sum()
            if model_sales >= 2:
                prices_model = mg['価格'].values
                model_stats.append({
                    'model': model,
                    'count': int(model_sales),
                    'median': float(np.median(prices_model)),
                    'cv': float(calculate_cv(prices_model)),
                    'title_sample': mg.iloc[0]['タイトル'][:60]
                })

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:15]

    line_stats[line] = {
        'count': int(sales),
        'median': float(np.median(prices)),
        'cv': float(calculate_cv(prices)),
    }

    if len(model_stats) > 0:
        line_models_dict[line] = {
            'count': int(sales),
            'models': model_stats
        }

print(f"✓ ライン別統計: {len(line_stats)}ライン")
print(f"✓ 各ライン別型番Top15: {len(line_models_dict)}ライン")

# ===== キャラクター別統計 =====
character_stats = {}
if len(df_brand_character) > 0:
    for character, group in df_brand_character.groupby('キャラクター'):
        if len(group) >= 1:
            prices = group['価格'].values
            character_stats[character] = {
                'count': int(group['販売数'].sum()),
                'median': float(np.median(prices)),
                'ratio': float(group['販売数'].sum() / total_line_sales * 100),
            }

print(f"✓ キャラクター/コラボ統計: {len(character_stats)}種類、{len(df_brand_character)}商品")

# ===== 型番別Top30を抽出 =====
model_stats_all = []
model_group_all = df_brand[df_brand['型番抽出'].notna()].copy()

if len(model_group_all) > 0:
    for model, mg in model_group_all.groupby('型番抽出'):
        model_sales = mg['販売数'].sum()
        if model_sales >= 2:
            prices = mg['価格'].values
            model_stats_all.append({
                'model': model,
                'count': int(model_sales),
                'median': float(np.median(prices)),
                'cv': float(calculate_cv(prices)),
            })

model_stats_all = sorted(model_stats_all, key=lambda x: x['count'], reverse=True)[:30]

print(f"✓ 型番Top30: {len(model_stats_all)}モデル")

# ===== 基本統計 =====
total_sales = int(df_brand['販売数'].sum())
median_price = float(df_brand['価格'].median())
cv_value = float(calculate_cv(df_brand['価格'].values))

# ===== グラフデータ準備 =====

# 価格帯別分布
price_ranges = ['~$100', '$100-150', '$150-200', '$200-300', '$300-500', '$500-1K', '$1K-2K', '$2K~']
price_counts = [
    len(df_brand[df_brand['価格'] < 100]),
    len(df_brand[(df_brand['価格'] >= 100) & (df_brand['価格'] < 150)]),
    len(df_brand[(df_brand['価格'] >= 150) & (df_brand['価格'] < 200)]),
    len(df_brand[(df_brand['価格'] >= 200) & (df_brand['価格'] < 300)]),
    len(df_brand[(df_brand['価格'] >= 300) & (df_brand['価格'] < 500)]),
    len(df_brand[(df_brand['価格'] >= 500) & (df_brand['価格'] < 1000)]),
    len(df_brand[(df_brand['価格'] >= 1000) & (df_brand['価格'] < 2000)]),
    len(df_brand[df_brand['価格'] >= 2000]),
]

# 駆動方式別分布
movement_counts = df_brand.groupby('駆動方式')['販売数'].sum().to_dict()
movement_labels = [k for k in movement_counts.keys() if k != '不明']
movement_values = [int(movement_counts[k]) for k in movement_labels]

# デパートメント別分布
dept_dist = df_brand.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist.index if dept != '不明']
dept_values = [int(dept_dist[dept]) for dept in dept_labels]

# ライン別売上比率（Top7のみ）
top_lines = sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:7]
line_labels = [line[0] for line in top_lines]
line_values = [line[1]['count'] for line in top_lines]

# キャラクター統計の事前計算
character_median = float(df_brand_character['価格'].median()) if len(df_brand_character) > 0 else 0
character_ratio = float(len(df_brand_character) / len(df_brand) * 100)

print(f"✓ グラフデータ準備完了")

# ===== HTML生成 =====
# TODO 5: ブランドカラーを定義
brand_color_primary = '#000000'  # BREITLING黒
brand_color_accent = '#FFD700'   # アクセントゴールド

brand_html = f'''
    <div id="{BRAND_NAME}" class="tab-content">
        <h2 class="section-title {brand_name_lower}-primary">✈️ {BRAND_NAME} 詳細分析</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{total_sales:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${median_price:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">{cv_value:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">型番抽出率</div>
                <div class="value {brand_name_lower}-accent">{df_brand['型番抽出'].notna().sum()/len(df_brand)*100:.1f}%</div>
            </div>
        </div>

        <div class="insight-box" style="border-left: 5px solid {brand_color_primary};">
            <h3 class="{brand_name_lower}-primary">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid {brand_color_primary};">
                    <h4 style="color: {brand_color_primary}; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong>Navitimer:</strong> 定番人気ライン、クロノグラフモデル</li>
                        <li><strong>Superocean:</strong> ダイバーズウォッチ、プロフェッショナルモデル</li>
                        <li><strong>Chronomat:</strong> スポーティー、クロノグラフ、高級感</li>
                        <li><strong>Limited Edition:</strong> 限定版、記念モデル、高付加価値</li>
                        <li><strong>Blackbird/Steelfish:</strong> 特別版、コレクター需要</li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid {brand_color_accent};">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>型番が不明瞭な商品（検証が困難）</li>
                        <li>パーツのみ（ムーブメント、ボックス等）</li>
                        <li>状態の悪いヴィンテージモデル（修理コストが高い）</li>
                        <li>低価格帯（$500以下）の怪しい商品</li>
                    </ul>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #7b1fa2;">
                    <h4 style="color: #7b1fa2; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> ¥200,000〜¥300,000</p>
                    <p style="margin: 5px 0 0 0;"><strong class="{brand_name_lower}-accent">人気ライン:</strong> ¥300,000〜¥500,000が上限</p>
                </div>
            </div>
        </div>

        <h3 class="section-title {brand_name_lower}-primary">📊 市場分析グラフ</h3>
        <div class="{brand_name_lower}-grid">
            <div class="{brand_name_lower}-chart-container">
                <h4 class="{brand_name_lower}-primary">価格帯別分析（50ドル刻み）</h4>
                <div id="{brand_name_lower}_price_chart" style="height: 350px;"></div>
            </div>
            <div class="{brand_name_lower}-chart-container">
                <h4 class="{brand_name_lower}-primary">駆動方式別分布</h4>
                <div id="{brand_name_lower}_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="{brand_name_lower}-chart-container">
                <h4 class="{brand_name_lower}-primary">性別・カテゴリー別分布</h4>
                <div id="{brand_name_lower}_gender_chart" style="height: 300px;"></div>
            </div>
            <div class="{brand_name_lower}-chart-container">
                <h4 class="{brand_name_lower}-primary">ライン別売上比率</h4>
                <div id="{brand_name_lower}_line_chart" style="height: 350px;"></div>
            </div>
        </div>

        <h3 class="section-title {brand_name_lower}-primary">🎭 特別版・限定モデル 分析</h3>
        <p style="color: #666; margin-bottom: 15px;">Navigation Limited、Anniversary等の特別版分析</p>

        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="label">特別版商品数</div>
                <div class="value {brand_name_lower}-accent">{len(df_brand_character)}個</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${character_median:.0f}</div>
            </div>
            <div class="stat-card">
                <div class="label">全体比率</div>
                <div class="value {brand_name_lower}-accent">{character_ratio:.1f}%</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>特別版</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>中央値</th>
                        <th class="{brand_name_lower}-accent">仕入上限(¥)</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

# キャラクター別詳細テーブル
for character_name, data in sorted(character_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    breakeven = int(data['median'] * 155 * 0.65)

    brand_html += f'''
                    <tr>
                        <td><strong>{character_name}</strong></td>
                        <td>{data['count']}</td>
                        <td class="{brand_name_lower}-accent">{data['ratio']:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td class="highlight {brand_name_lower}-accent">¥{breakeven:,}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw={BRAND_NAME}+{character_name.replace(' ', '+')}+Watch&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword={BRAND_NAME}%20{character_name.replace(' ', '%20')}%20時計&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

brand_html += '''
                </tbody>
            </table>
        </div>


        <h3 class="section-title {brand_name_lower}-primary">📌 各ラインの人気モデル（実データより）Top15</h3>
        <p style="color: #666; margin-bottom: 20px;">元CSVデータから再分類した正確な人気モデルTop15</p>
'''

# 各ライン別の型番Top15テーブル
for line_name, line_data in sorted(line_models_dict.items(), key=lambda x: x[1]['count'], reverse=True):
    brand_html += f'''
        <h4 style="color: {brand_color_primary}; margin-top: 25px; border-bottom: 2px solid {brand_color_primary}; padding-bottom: 5px;">
            {line_name} <span style="font-size: 0.9em; color: #666;">（販売数: {line_data['count']}個）</span>
        </h4>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th class="{brand_name_lower}-accent">仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>商品例</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for rank, model_data in enumerate(line_data['models'], 1):
        breakeven = int(model_data['median'] * 155 * 0.65)

        brand_html += f'''
                    <tr>
                        <td><strong class="{brand_name_lower}-accent">{rank}</strong></td>
                        <td><strong>{model_data['model']}</strong></td>
                        <td>{model_data['count']}</td>
                        <td>${model_data['median']:.0f}</td>
                        <td class="highlight {brand_name_lower}-accent">¥{breakeven:,}</td>
                        <td>{model_data['cv']:.3f}</td>
                        <td class="model-sample">{model_data['title_sample']}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw={BRAND_NAME}+{model_data['model'].replace(' ', '+')}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword={BRAND_NAME}%20{model_data['model'].replace(' ', '%20')}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
        '''

    brand_html += '''
                </tbody>
            </table>
        </div>
    '''

brand_html += f'''

        <h3 class="section-title {brand_name_lower}-primary">🔵 ライン別詳細分析（全{len(line_stats)}ライン）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th class="{brand_name_lower}-accent">比率</th>
                        <th>中央値</th>
                        <th class="{brand_name_lower}-accent">仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

# ライン別詳細テーブル
for line_name, data in sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    line_ratio = data['count'] / total_line_sales * 100
    breakeven = int(data['median'] * 155 * 0.65)

    brand_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td class="{brand_name_lower}-accent">{line_ratio:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td class="highlight {brand_name_lower}-accent">¥{breakeven:,}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw={BRAND_NAME}+{line_name.replace(' ', '+')}+Watch&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword={BRAND_NAME}%20{line_name.replace(' ', '%20')}%20時計&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

brand_html += f'''
                </tbody>
            </table>
        </div>


        <h3 class="section-title {brand_name_lower}-primary">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th class="{brand_name_lower}-accent">仕入上限(¥)</th>
                        <th>CV</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

# 型番Top30テーブル
for rank, model_data in enumerate(model_stats_all, 1):
    breakeven = int(model_data['median'] * 155 * 0.65)

    brand_html += f'''
                    <tr>
                        <td><strong class="{brand_name_lower}-accent">{rank}</strong></td>
                        <td>{model_data['model']}</td>
                        <td>{model_data['count']}</td>
                        <td>${model_data['median']:.2f}</td>
                        <td class="highlight {brand_name_lower}-accent">¥{breakeven:,}</td>
                        <td>{model_data['cv']:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw={BRAND_NAME}+{model_data['model'].replace(' ', '+')}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword={BRAND_NAME}%20{model_data['model'].replace(' ', '%20')}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

brand_html += '''
                </tbody>
            </table>
        </div>

    </div>
'''

# ===== グラフスクリプト生成（Plotly使用） =====
graph_script = f'''
        <script>
        const {brand_name_lower}Primary = '{brand_color_primary}';
        const {brand_name_lower}Accent = '{brand_color_accent}';
        const {brand_name_lower}Gradient = ['{brand_color_primary}', '#7b68ee', '#9370db', '#ba55d3', '#da70d6'];

        Plotly.newPlot('{brand_name_lower}_price_chart', [{{
            x: {price_ranges},
            y: {price_counts},
            type: 'bar',
            marker: {{
                color: {brand_name_lower}Primary,
                line: {{color: {brand_name_lower}Accent, width: 1}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_name_lower}_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: {brand_name_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>割合: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_name_lower}_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: {brand_name_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>割合: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_name_lower}_line_chart', [{{
            labels: {line_labels},
            values: {line_values},
            type: 'pie',
            marker: {{colors: {brand_name_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>割合: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
'''

# ===== CSS追加 =====
css_insert = f'''
    .{brand_name_lower}-primary {{ color: {brand_color_primary}; }}
    .{brand_name_lower}-accent {{ color: {brand_color_accent}; font-weight: bold; }}
    .{brand_name_lower}-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 20px 0;
    }}
    .{brand_name_lower}-chart-container {{
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .{brand_name_lower}-chart-container h4 {{
        margin-bottom: 10px;
        font-size: 16px;
    }}

    @media (max-width: 768px) {{
        .{brand_name_lower}-grid {{
            grid-template-columns: 1fr;
        }}
    }}
'''

# ===== HTML置換処理 =====
print(f"\n📄 HTML置換処理開始...")

# Hamiltonタブの終了位置を特定（ネストカウント方式）
hamilton_start = html.find('<div id="Hamilton" class="tab-content">')
if hamilton_start == -1:
    print("❌ エラー: Hamiltonタブが見つかりません")
    exit(1)

# Hamiltonタブの終了</div>を探す（ネストを考慮）
div_count = 1
search_pos = hamilton_start + len('<div id="Hamilton" class="tab-content">')
body_pos = html.find('</body>')

while div_count > 0 and search_pos < body_pos:
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: Hamiltonタブの閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            hamilton_end = next_close + 6  # 6 = len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✓ Hamiltonタブ終了位置: {hamilton_end}")

# 既存のブランドタブを削除（存在する場合）
brand_start = html.find(f'<div id="{BRAND_NAME}" class="tab-content">')
if brand_start != -1:
    # ブランドタブの終了位置を探す
    div_count = 1
    search_pos = brand_start + len(f'<div id="{BRAND_NAME}" class="tab-content">')

    while div_count > 0 and search_pos < body_pos:
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                brand_end = next_close + 6
                # ブランドタブを削除
                html = html[:brand_start] + html[brand_end:]
                print(f"✓ 既存{BRAND_NAME}タブを削除")
                # 削除後、hamilton_endの位置を再計算
                if brand_start < hamilton_end:
                    hamilton_end -= (brand_end - brand_start)
                break
            else:
                search_pos = next_close + 6

# Hamiltonタブの後にブランドタブを挿入
html = html[:hamilton_end] + '\n' + brand_html + html[hamilton_end:]
print(f"✓ {BRAND_NAME}タブを挿入")

# CSS追加
style_end = html.find('</style>')
if style_end != -1:
    html = html[:style_end] + css_insert + '\n' + html[style_end:]
    print(f"✓ CSS追加")

# グラフスクリプトを</body>の前に追加
body_end = html.find('</body>')
if body_end != -1:
    html = html[:body_end] + graph_script + '\n' + html[body_end:]
    print(f"✓ グラフスクリプト追加")

# HTMLファイルを保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ {BRAND_NAME}タブ実装完了！")
print(f"   - ファイルサイズ: {len(html):,}文字")
print(f"   - ライン数: {len(line_stats)}種類")
print(f"   - キャラクター/特別版: {len(character_stats)}種類")
