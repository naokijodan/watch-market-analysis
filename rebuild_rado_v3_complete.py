#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADOタブ v3 完全版
- 元CSVから正確にライン分類
- キャラクター/コラボ分析（複数視点）
- 各ラインの人気モデルTop5を抽出
"""

import pandas as pd
import re
import numpy as np
import sys
sys.path.insert(0, '/Users/naokijodan/Desktop/watch-market-analysis')
from utils.common import generate_search_link_html

print("📄 RADOタブ v3 完全版再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_rado = df[(df['ブランド']=='RADO') & (df['商品状態']=='完品')].copy()

print(f"✓ RADO完品データ: {len(df_rado)}件")

# 完全なライン定義（優先順位順）
RADO_LINES_COMPLETE = {
    # ===== メインライン =====
    'DiaStar': [
        'DIASTAR', 'DIA STAR',
        # 型番パターン
        '152.', '153.', '129.', '110.', '111.', '132.', '133.', '134.',
        '636.',
    ],

    'Florence': [
        'FLORENCE',
        '153.36', '129.36', '204.',
    ],

    'Coupole': [
        'COUPOLE',
        '129.40', '129.50',
    ],

    'Golden Horse': [
        'GOLDEN HORSE',
        '11675', '116.',
    ],

    'Balboa': [
        'BALBOA',
    ],

    'Voyager': [
        'VOYAGER',
    ],

    'Manchester': [
        'MANCHESTER',
        '11006',
    ],

    'Ticino': [
        'TICINO',
    ],

    'True': [
        'TRUE',
        'R27',
    ],

    'Centrix': [
        'CENTRIX',
        'R30',
    ],

    'Integral': [
        'INTEGRAL',
        'R20',
    ],
}

def classify_rado_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in RADO_LINES_COMPLETE.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return 'その他RADO'

def extract_model_number(title):
    """タイトルから型番を抽出（RADO用）"""
    title_upper = str(title).upper()

    # RADOの型番パターン
    # パターン1: 数字.数字.数字（129.3644.4、152.0341.3等）
    pattern1 = r'\b\d{3}\.\d{4}\.\d{1}\b'
    match1 = re.search(pattern1, title_upper)
    if match1:
        return match1.group()

    # パターン2: 数字のみ（11675、11006等）
    pattern2 = r'\b\d{5}\b'
    match2 = re.search(pattern2, title_upper)
    if match2:
        candidate = match2.group()
        # 年代は除外
        if not candidate.startswith(('19', '20')):
            return candidate

    # パターン3: R+数字（R27、R30等）
    pattern3 = r'\bR\d{2}\b'
    match3 = re.search(pattern3, title_upper)
    if match3:
        return match3.group()

    return None

def calculate_cv(prices):
    """変動係数を計算"""
    if len(prices) < 2:
        return 0
    mean = np.mean(prices)
    if mean == 0:
        return 0
    std = np.std(prices, ddof=1)
    return std / mean

# ライン分類実行（通常）
df_rado['ライン'] = df_rado['タイトル_upper'].apply(classify_rado_line)

# キャラクター/コラボ判定（別視点）
CHARACTER_KEYWORDS = [
    # コラボ一般
    'COLLABORATION', 'COLLAB',
    'LIMITED EDITION', 'SPECIAL EDITION',
]

def is_character_collab(title_upper):
    """キャラクター/コラボ商品かどうか判定"""
    for kw in CHARACTER_KEYWORDS:
        if kw in title_upper:
            return True
    return False

df_rado['キャラクター/コラボ'] = df_rado['タイトル_upper'].apply(is_character_collab)

# 型番を抽出
df_rado['型番抽出'] = df_rado['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_rado['型番抽出'].notna().sum()}件")

# ライン別統計を計算
line_stats = {}
line_models_dict = {}

for line, group in df_rado.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()
    revenue = (group['価格'] * group['販売数']).sum()

    line_stats[line] = {
        'avg_price': np.mean(prices),
        'sales': sales,
        'revenue': revenue,
        'cv': calculate_cv(prices),
        'count': len(group)
    }

    # 各ラインのTop5モデル
    model_stats = []
    for model, model_group in group.groupby('型番抽出'):
        if pd.isna(model) or model == 'None':
            continue
        model_revenue = (model_group['価格'] * model_group['販売数']).sum()
        model_sales = model_group['販売数'].sum()
        model_avg_price = model_group['価格'].mean()

        model_stats.append({
            'model': model,
            'revenue': model_revenue,
            'sales': model_sales,
            'avg_price': model_avg_price
        })

    model_stats.sort(key=lambda x: x['revenue'], reverse=True)
    line_models_dict[line] = model_stats[:5]

# 基本統計
rado_sales = df_rado['販売数'].sum()
rado_avg_price = df_rado['価格'].mean()
rado_cv = calculate_cv(df_rado['価格'].values)

print(f"✓ ライン別統計計算完了: {len(line_stats)}ライン")

# Top30人気モデル
model_stats_all = []

for model, group in df_rado.groupby('型番抽出'):
    if pd.isna(model) or model == 'None':
        continue

    revenue = (group['価格'] * group['販売数']).sum()
    sales = group['販売数'].sum()
    avg_price = group['価格'].mean()
    max_price = group['価格'].max()
    min_price = group['価格'].min()
    line = group['ライン'].mode()[0] if len(group['ライン'].mode()) > 0 else 'その他RADO'

    model_stats_all.append({
        'model': model,
        'line': line,
        'revenue': revenue,
        'sales': sales,
        'avg_price': avg_price,
        'max_price': max_price,
        'min_price': min_price
    })

model_stats_all.sort(key=lambda x: x['revenue'], reverse=True)
top30_models = model_stats_all[:30]

print(f"✓ Top30モデル抽出完了: {len(top30_models)}モデル")

# キャラクター/コラボ分析
character_df = df_rado[df_rado['キャラクター/コラボ']==True].copy()

character_stats = []
if len(character_df) > 0:
    for char_name, group in character_df.groupby('タイトル_upper'):
        # キャラクター名を抽出（簡易版）
        char_match = None
        for kw in CHARACTER_KEYWORDS:
            if kw in char_name:
                char_match = kw
                break

        if not char_match:
            continue

        revenue = (group['価格'] * group['販売数']).sum()
        sales = group['販売数'].sum()
        avg_price = group['価格'].mean()

        character_stats.append({
            'name': char_match,
            'revenue': revenue,
            'sales': sales,
            'avg_price': avg_price
        })

    # 重複排除とソート
    character_stats_dict = {}
    for stat in character_stats:
        name = stat['name']
        if name in character_stats_dict:
            character_stats_dict[name]['revenue'] += stat['revenue']
            character_stats_dict[name]['sales'] += stat['sales']
        else:
            character_stats_dict[name] = stat

    character_stats = list(character_stats_dict.values())
    character_stats.sort(key=lambda x: x['revenue'], reverse=True)

print(f"✓ キャラクター/コラボ分析完了: {len(character_stats)}件")

# 7. 価格帯別分布（上限金額算出用）
price_bins = [0, 100, 200, 300, 400, 500, 750, 1000, 1500, 2000, 5000, 10000]
price_labels = ['$0-100', '$100-200', '$200-300', '$300-400', '$400-500',
                '$500-750', '$750-1000', '$1000-1500', '$1500-2000', '$2000-5000', '$5000+']

df_rado['価格帯'] = pd.cut(df_rado['価格'], bins=price_bins, labels=price_labels, right=False)
price_dist = df_rado.groupby('価格帯', observed=True)['販売数'].sum().to_dict()

# 上限金額の算出（売上の80%を占める価格帯の上限）
cumulative_sales = 0
total_sales = sum(price_dist.values())
purchase_limit = 0

for label in price_labels:
    cumulative_sales += price_dist.get(label, 0)
    if cumulative_sales >= total_sales * 0.8:
        # ラベルから上限金額を抽出
        if '+' in label:
            purchase_limit = int(label.replace('$', '').replace('+', ''))
        else:
            upper = label.split('-')[1]
            purchase_limit = int(upper.replace('$', ''))
        break

print(f"✓ 仕入上限金額: ${purchase_limit}")

# HTMLタブ生成
tab_html = f'''
        <div id="RADO" class="tab-content">
            <h2>🟣 RADO 時計市場分析</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📦</div>
                    <div class="stat-value">{rado_sales}</div>
                    <div class="stat-label">販売数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💰</div>
                    <div class="stat-value">${rado_avg_price:.0f}</div>
                    <div class="stat-label">平均価格</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value">{rado_cv:.2f}</div>
                    <div class="stat-label">変動係数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-value">${purchase_limit}</div>
                    <div class="stat-label">仕入上限目安</div>
                </div>
            </div>

            <h3>🏆 Top30人気モデル</h3>
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>ライン</th>
                        <th>売上($)</th>
                        <th>販売数</th>
                        <th>平均価格($)</th>
                        <th>最高価格($)</th>
                        <th>最低価格($)</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

for i, model in enumerate(top30_models, 1):
    search_links = generate_search_link_html('RADO', model['model'], 'model', include_checkbox=True)
    tab_html += f'''                    <tr>
                        <td>{i}</td>
                        <td><strong>{model['model']}</strong></td>
                        <td>{model['line']}</td>
                        <td>${model['revenue']:.0f}</td>
                        <td>{model['sales']}</td>
                        <td>${model['avg_price']:.0f}</td>
                        <td>${model['max_price']:.0f}</td>
                        <td>${model['min_price']:.0f}</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>
'''

tab_html += '''                </tbody>
            </table>

            <h3 class="chart-section-title">📊 グラフ分析</h3>
            <div class="chart-grid">
                <div class="chart-container">
                    <canvas id="radoPriceDistChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="radoLinePieChart"></canvas>
                </div>
            </div>

            <h3>🔵 ライン別詳細分析</h3>
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>売上($)</th>
                        <th>販売数</th>
                        <th>平均価格($)</th>
                        <th>変動係数</th>
                        <th>商品数</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

# ライン別テーブル生成
sorted_lines = sorted(line_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)
for line, stats in sorted_lines:
    search_links = generate_search_link_html('RADO', line, 'line', include_checkbox=True)
    tab_html += f'''                    <tr>
                        <td><strong>{line}</strong></td>
                        <td>${stats['revenue']:.0f}</td>
                        <td>{stats['sales']}</td>
                        <td>${stats['avg_price']:.0f}</td>
                        <td>{stats['cv']:.2f}</td>
                        <td>{stats['count']}</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>
'''

tab_html += '''                </tbody>
            </table>

            <h4>🔥 各ライン人気モデルTop5</h4>
'''

# 各ラインの人気モデル
for line, models in line_models_dict.items():
    if not models:
        continue

    tab_html += f'''
            <h5>📦 {line}</h5>
            <table>
                <thead>
                    <tr>
                        <th>型番</th>
                        <th>売上($)</th>
                        <th>販売数</th>
                        <th>平均価格($)</th>
                    </tr>
                </thead>
                <tbody>
'''

    for model in models:
        tab_html += f'''                    <tr>
                        <td>{model['model']}</td>
                        <td>${model['revenue']:.0f}</td>
                        <td>{model['sales']}</td>
                        <td>${model['avg_price']:.0f}</td>
                    </tr>
'''

    tab_html += '''                </tbody>
            </table>
'''

# キャラクター/コラボ分析
if character_stats:
    tab_html += '''
            <h3>🎭 キャラクター/コラボ分析</h3>
            <table>
                <thead>
                    <tr>
                        <th>キャラクター/コラボ</th>
                        <th>売上($)</th>
                        <th>販売数</th>
                        <th>平均価格($)</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

    for char in character_stats:
        search_links = generate_search_link_html('RADO', char['name'], 'character', include_checkbox=True)
        tab_html += f'''                    <tr>
                        <td><strong>{char['name']}</strong></td>
                        <td>${char['revenue']:.0f}</td>
                        <td>{char['sales']}</td>
                        <td>${char['avg_price']:.0f}</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>
'''

    tab_html += '''                </tbody>
            </table>
'''

tab_html += '''        </div>
'''

print("✓ HTMLタブ生成完了")

# タブコンテンツを挿入（Orientの後に）
# 注意: RADOタブボタンは既に存在するため追加不要
orient_start = html.find('<div id="Orient" class="tab-content">')
if orient_start == -1:
    print("❌ エラー: Orientタブコンテンツが見つかりません")
    exit(1)

# ネストカウントでOrientタブの終了位置を探す
div_count = 1
search_pos = orient_start + len('<div id="Orient" class="tab-content">')

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: Orientタブの閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            orient_end = next_close + 6  # 6 = len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✓ Orientタブ終了位置: {orient_end}")

# RADOタブを挿入
html = html[:orient_end] + '\n' + tab_html + html[orient_end:]

print("✓ RADOタブコンテンツ挿入完了")

# グラフ用スクリプトを生成
line_labels = [line for line, _ in sorted_lines]
line_revenues = [stats['revenue'] for _, stats in sorted_lines]

price_dist_labels = [label for label in price_labels if label in price_dist]
price_dist_values = [price_dist[label] for label in price_dist_labels]

script_html = f'''
    <script>
        // RADOライン別売上円グラフ
        var radoLineCtx = document.getElementById('radoLinePieChart').getContext('2d');
        var radoLinePieChart = new Chart(radoLineCtx, {{
            type: 'pie',
            data: {{
                labels: {line_labels},
                datasets: [{{
                    data: {line_revenues},
                    backgroundColor: [
                        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                        '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'RADOライン別売上比率',
                        font: {{ size: 16 }}
                    }},
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});

        // RADO価格帯別販売分布
        var radoPriceCtx = document.getElementById('radoPriceDistChart').getContext('2d');
        var radoPriceDistChart = new Chart(radoPriceCtx, {{
            type: 'bar',
            data: {{
                labels: {price_dist_labels},
                datasets: [{{
                    label: '販売数',
                    data: {price_dist_values},
                    backgroundColor: '#9370DB'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'RADO価格帯別販売分布',
                        font: {{ size: 16 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
'''

# スクリプトを</body>の前に挿入
body_end_pos = html.rfind('</body>')
if body_end_pos == -1:
    print("❌ エラー: </body>が見つかりません")
    exit(1)

html = html[:body_end_pos] + script_html + html[body_end_pos:]

print("✓ グラフスクリプト追加完了")

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size_kb = len(html) / 1024
print(f"\n✅ RADOタブ再構築完了！")
print(f"📄 ファイルサイズ: {file_size_kb:.1f} KB")
print(f"📊 統計:")
print(f"  - 販売数: {rado_sales}")
print(f"  - Top30モデル: {len(top30_models)}")
print(f"  - ライン数: {len(line_stats)}")
print(f"  - キャラクター/コラボ: {len(character_stats)}")
