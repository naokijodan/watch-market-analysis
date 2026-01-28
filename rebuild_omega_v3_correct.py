#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGAタブ v3 正しい構造版
- RADOと同じ構造に統一
- Plotlyグラフを使用
- 仕入上限(¥)、比率、安定度を含む
"""

import pandas as pd
import json
import re
import numpy as np

print("📄 OMEGAタブ v3 正しい構造版で再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

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

# ライン分類実行
df_omega['ライン'] = df_omega['タイトル_upper'].apply(classify_omega_line)

# 特徴・価値軸判定
OMEGA_FEATURES = {
    'Vintage': ['VINTAGE', 'RETRO', '60S', '70S', '80S', '90S'],
    'Co-Axial': ['CO-AXIAL', 'COAXIAL'],
    'Chronometer': ['CHRONOMETER', 'OFFICIALLY CERTIFIED'],
    'Chronograph': ['CHRONOGRAPH', 'CHRONO'],
    'GMT/World Time': ['GMT', 'WORLD TIME', 'WORLDTIME'],
    'Limited Edition': ['LIMITED', 'SPECIAL EDITION', 'ANNIVERSARY'],
}

def detect_omega_feature(title_upper):
    """特徴・価値軸を検出"""
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
df_omega['型番抽出'] = df_omega['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_omega['型番抽出'].notna().sum()}件 / {len(df_omega)}件 ({df_omega['型番抽出'].notna().sum()/len(df_omega)*100:.1f}%)")

# ライン別統計を計算
line_stats = {}
total_line_sales = df_omega['販売数'].sum()

for line, group in df_omega.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    line_stats[line] = {
        'count': int(sales),
        'median': float(np.median(prices)),
        'cv': float(calculate_cv(prices)),
    }

print(f"✓ ライン別統計: {len(line_stats)}ライン")

# 特徴別統計を計算
feature_stats = {}
for feature_name in OMEGA_FEATURES.keys():
    feature_group = df_omega[df_omega['特徴'].notna() & df_omega['特徴'].str.contains(feature_name, na=False)]
    if len(feature_group) >= 2:
        prices = feature_group['価格'].values
        feature_stats[feature_name] = {
            'count': int(feature_group['販売数'].sum()),
            'median': float(np.median(prices)),
            'cv': float(calculate_cv(prices)),
        }

print(f"✓ 特徴別統計: {len(feature_stats)}特徴")

# 基本統計
total_sales = int(df_omega['販売数'].sum())
median_price = float(df_omega['価格'].median())
cv_value = float(calculate_cv(df_omega['価格'].values))

# 価格帯別分布（50ドル刻み）
price_ranges = ['~$100', '$100-150', '$150-200', '$200-300', '$300-500', '$500-1K', '$1K-2K', '$2K~']
price_counts = [
    len(df_omega[df_omega['価格'] < 100]),
    len(df_omega[(df_omega['価格'] >= 100) & (df_omega['価格'] < 150)]),
    len(df_omega[(df_omega['価格'] >= 150) & (df_omega['価格'] < 200)]),
    len(df_omega[(df_omega['価格'] >= 200) & (df_omega['価格'] < 300)]),
    len(df_omega[(df_omega['価格'] >= 300) & (df_omega['価格'] < 500)]),
    len(df_omega[(df_omega['価格'] >= 500) & (df_omega['価格'] < 1000)]),
    len(df_omega[(df_omega['価格'] >= 1000) & (df_omega['価格'] < 2000)]),
    len(df_omega[df_omega['価格'] >= 2000]),
]

# 駆動方式別分布
movement_counts = df_omega.groupby('駆動方式')['販売数'].sum().to_dict()
movement_labels = list(movement_counts.keys())
movement_values = [int(v) for v in movement_counts.values()]

# デパートメント別分布
dept_dist = df_omega.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist.index if dept != '不明']
dept_values = [int(dept_dist[dept]) for dept in dept_labels]

# ライン別売上比率（Top7のみ）
top_lines = sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:7]
line_labels = [line[0] for line in top_lines]
line_values = [line[1]['count'] for line in top_lines]

print(f"✓ グラフデータ準備完了")

# ===== HTML生成 =====
omega_html = f'''
    <div id="OMEGA" class="tab-content">
        <h2 class="section-title omega-purple">🟣 OMEGA 詳細分析</h2>

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
                <div class="value omega-accent">{df_omega['型番抽出'].notna().sum()/len(df_omega)*100:.1f}%</div>
            </div>
        </div>

        <div class="insight-box" style="border-left: 5px solid #667eea;">
            <h3 class="omega-purple">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <h4 style="color: #667eea; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong class="omega-accent">Seamaster/De Ville</strong>の2大主力ライン（市場の66%）</li>
                        <li>型番が<strong>明確に記載</strong>されている商品</li>
                        <li><strong class="omega-accent">Co-Axial/Chronometer</strong>機構搭載モデル</li>
                        <li>ヴィンテージで状態が良好なもの</li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #764ba2;">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>型番不明の「その他OMEGA」</li>
                        <li>状態不明・箱なし品</li>
                        <li>マイナーライン（Cosmic、Dynamic等）</li>
                        <li>修理歴不明のヴィンテージ品</li>
                    </ul>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #7b1fa2;">
                    <h4 style="color: #7b1fa2; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> ¥25,000以下</p>
                    <p style="margin: 5px 0 0 0;"><strong class="omega-accent">Seamaster/De Ville:</strong> ¥40,000前後が上限</p>
                </div>
            </div>
        </div>

        <h3 class="section-title omega-purple">📊 市場分析グラフ</h3>
        <div class="omega-grid">
            <div class="omega-chart-container">
                <h4 class="omega-purple">価格帯別分析（50ドル刻み）</h4>
                <div id="omega_price_chart" style="height: 350px;"></div>
            </div>
            <div class="omega-chart-container">
                <h4 class="omega-purple">駆動方式別分布</h4>
                <div id="omega_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="omega-chart-container">
                <h4 class="omega-purple">性別・カテゴリー別分布</h4>
                <div id="omega_gender_chart" style="height: 300px;"></div>
            </div>
            <div class="omega-chart-container">
                <h4 class="omega-purple">ライン別売上比率</h4>
                <div id="omega_line_chart" style="height: 350px;"></div>
            </div>
        </div>

        <h3 class="section-title omega-purple">🔵 ライン別詳細分析（全{len(line_stats)}ライン）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th class="omega-accent">比率</th>
                        <th>中央値</th>
                        <th class="omega-accent">仕入上限(¥)</th>
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
    breakeven = int(data['median'] * 155 * 0.65)  # 為替155円 × 利益率0.65

    omega_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td class="omega-accent">{line_ratio:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td class="highlight omega-accent">¥{breakeven:,}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=OMEGA+{line_name.replace(' ', '+')}+Watch&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=OMEGA%20{line_name.replace(' ', '%20')}%20時計&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

omega_html += '''
                </tbody>
            </table>
        </div>


        <h3 class="section-title omega-purple">🎭 特徴・価値軸分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>特徴</th>
                        <th>商品数</th>
                        <th>中央値</th>
                        <th class="omega-accent">仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

# 特徴別詳細テーブル
for feature_name, data in sorted(feature_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    breakeven = int(data['median'] * 155 * 0.65)

    omega_html += f'''
                    <tr>
                        <td><strong>{feature_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>${data['median']:.0f}</td>
                        <td class="highlight omega-accent">¥{breakeven:,}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=OMEGA+{feature_name.replace(' ', '+').replace('/', '%2F')}+Watch&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=OMEGA%20{feature_name.replace(' ', '%20').replace('/', '%2F')}%20時計&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

omega_html += '''
                </tbody>
            </table>
        </div>

    </div>
'''

# ===== グラフスクリプト生成（Plotly使用） =====
graph_script = f'''
        <script>
        const omegaPurple = '#667eea';
        const omegaAccent = '#764ba2';
        const omegaGradient = ['#667eea', '#7b68ee', '#9370db', '#ba55d3', '#da70d6'];

        Plotly.newPlot('omega_price_chart', [{{
            x: {price_ranges},
            y: {price_counts},
            type: 'bar',
            marker: {{
                color: omegaPurple,
                line: {{color: omegaAccent, width: 1}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('omega_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: omegaGradient}},
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>割合: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('omega_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: omegaGradient}},
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>割合: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('omega_line_chart', [{{
            labels: {line_labels},
            values: {line_values},
            type: 'pie',
            marker: {{colors: omegaGradient}},
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
css_insert = '''
    .omega-purple { color: #667eea; }
    .omega-accent { color: #764ba2; font-weight: bold; }
    .omega-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    .omega-chart-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .omega-chart-container h4 {
        margin-bottom: 10px;
        font-size: 16px;
    }
'''

# ===== HTML置換 =====

# 1. 既存OMEGAタブを削除
omega_tab_start = html.find('<div id="OMEGA" class="tab-content">')
if omega_tab_start == -1:
    print("❌ OMEGAタブが見つかりません")
    exit(1)

# ネストカウントで終了位置を特定
div_count = 1
search_pos = omega_tab_start + len('<div id="OMEGA" class="tab-content">')
omega_tab_end = -1

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ OMEGAタブの終了タグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            omega_tab_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

if omega_tab_end == -1:
    print("❌ OMEGAタブの終了位置が特定できません")
    exit(1)

# 既存のOMEGAタブを削除
html = html[:omega_tab_start] + html[omega_tab_end:]

print(f"✓ 既存OMEGAタブ削除完了（{omega_tab_start}〜{omega_tab_end}）")

# 2. RADOタブの後ろに新しいOMEGAタブを挿入
rado_tab_start = html.find('<div id="RADO" class="tab-content">')
if rado_tab_start == -1:
    print("❌ RADOタブが見つかりません")
    exit(1)

# RADOタブの終了位置を特定
div_count = 1
search_pos = rado_tab_start + len('<div id="RADO" class="tab-content">')
rado_tab_end = -1

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ RADOタブの終了タグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            rado_tab_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

if rado_tab_end == -1:
    print("❌ RADOタブの終了位置が特定できません")
    exit(1)

# RADOタブの後ろに挿入
html = html[:rado_tab_end] + '\n\n' + omega_html + html[rado_tab_end:]

print(f"✓ 新しいOMEGAタブ挿入完了（RADOタブの後ろ）")

# 3. CSS追加
css_marker = '    .rado-chart-container h4 {'
css_pos = html.find(css_marker)
if css_pos != -1:
    # その行の最後に追加
    line_end = html.find('\n', css_pos)
    next_marker = html.find('}\n', css_pos) + 2
    html = html[:next_marker] + css_insert + html[next_marker:]
    print(f"✓ CSS追加完了")
else:
    print("⚠️ CSS挿入位置が見つかりませんでした")

# 4. グラフスクリプトを</body>の前に追加
body_end = html.rfind('</body>')
if body_end == -1:
    print("❌ </body>タグが見つかりません")
    exit(1)

html = html[:body_end] + graph_script + '\n' + html[body_end:]

print(f"✓ Plotlyグラフスクリプト追加完了")

# ===== 保存 =====
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ OMEGAタブ再構築完了！")
print(f"   - Plotlyグラフ: 4個（価格帯・駆動方式・性別・ライン別）")
print(f"   - ライン別詳細分析: {len(line_stats)}ライン（比率・仕入上限・安定度を含む）")
print(f"   - 特徴別分析: {len(feature_stats)}特徴")
print(f"\n📝 ブラウザで index.html を開いて OMEGA タブを確認してください")
