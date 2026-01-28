#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROLEXタブ完全実装スクリプト (v3)
template_brand_tab.pyを基準に8セクション構成で実装
"""

import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================
# TODO 1: ブランド名の設定
# ============================================================
BRAND_NAME = 'ROLEX'

# ============================================================
# TODO 2: ライン定義（ROLEX固有）
# ============================================================
ROLEX_LINES = {
    'Datejust': ['DATEJUST', 'DATE JUST'],
    'Submariner': ['SUBMARINER', 'SUB'],
    'Oyster Perpetual': ['OYSTER PERPETUAL'],
    'Daytona': ['DAYTONA'],
    'GMT-Master': ['GMT-MASTER', 'GMT MASTER', 'GMT'],
    'Explorer': ['EXPLORER'],
    'Day-Date': ['DAY-DATE', 'DAY DATE'],
    'Yacht-Master': ['YACHT-MASTER', 'YACHT MASTER'],
    'Sea-Dweller': ['SEA-DWELLER', 'SEA DWELLER'],
    'Milgauss': ['MILGAUSS'],
    'Air-King': ['AIR-KING', 'AIR KING'],
    'Sky-Dweller': ['SKY-DWELLER', 'SKY DWELLER'],
}

def classify_line(title):
    """タイトルからラインを分類"""
    title_upper = str(title).upper()
    for line_name, keywords in ROLEX_LINES.items():
        for keyword in keywords:
            if keyword in title_upper:
                return line_name
    return f'その他{BRAND_NAME}'

# ============================================================
# TODO 3: 型番抽出関数（ROLEX固有）
# ============================================================
def extract_model_number(title):
    """
    ROLEXの型番を抽出（3パターン）
    優先順位: 6桁 > 5桁 > 4桁（新しいモデルを優先）
    """
    title_upper = str(title).upper()

    # Pattern 1: 6桁数字（最新モデル）116528, 126303など
    match = re.search(r'\b(\d{6})\b', title_upper)
    if match:
        model = match.group(1)
        # ボックス型番を除外（39xxx, 68xxx等）
        if not (model.startswith('39') or model.startswith('68')):
            return model

    # Pattern 2: 5桁数字（主要モデル）16233, 16610など
    match = re.search(r'\b(\d{5})\b', title_upper)
    if match:
        model = match.group(1)
        # ボックス型番を除外（39xxx等）
        if not model.startswith('39'):
            return model

    # Pattern 3: 4桁数字（ヴィンテージ）5512, 6917など
    match = re.search(r'\b(\d{4})\b', title_upper)
    if match:
        model = match.group(1)
        # 年号を除外（1970-2025）
        if not (1970 <= int(model) <= 2025):
            return model

    return None

# ============================================================
# TODO 4: ボックス・パーツ検出
# ============================================================
BOX_KEYWORDS = ['BOX', 'CASE', 'BOOKLET', 'TAG', 'CARD', 'POUCH', 'MANUAL', 'PAPER', 'EMPTY']

def is_box_or_parts(title):
    """タイトルからボックス・パーツを検出"""
    title_upper = str(title).upper()

    # 明確な除外キーワード
    if 'NO WATCH' in title_upper or 'EMPTY BOX' in title_upper:
        return True

    # ボックス・パーツキーワード
    for keyword in BOX_KEYWORDS:
        if keyword in title_upper:
            return True

    return False

# ============================================================
# TODO 5: ブランドカラー設定
# ============================================================
brand_color_primary = '#006039'  # ROLEXグリーン
brand_color_accent = '#C9B037'   # ゴールド

# ============================================================
# データ読み込みと分析
# ============================================================
print(f"{'='*80}")
print(f"{BRAND_NAME}タブ 完全実装スクリプト")
print(f"{'='*80}\n")

# CSVファイルを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# ROLEXのデータを抽出
brand_df = df[df['ブランド'] == BRAND_NAME].copy()
complete_data = brand_df.dropna(subset=['価格'])

print(f"【データ読み込み】")
print(f"総販売数: {len(brand_df)}個")
print(f"完全データ: {len(complete_data)}個\n")

# ボックス・パーツ検出
print("【ボックス・パーツ検出】")
complete_data['is_box'] = complete_data['タイトル'].apply(is_box_or_parts)
box_data = complete_data[complete_data['is_box'] == True]
watch_data = complete_data[complete_data['is_box'] == False]
print(f"ボックス・パーツ: {len(box_data)}個")
print(f"時計本体: {len(watch_data)}個\n")

# 型番抽出
print("【型番抽出】")
complete_data['model_number'] = complete_data['タイトル'].apply(extract_model_number)
extracted_count = complete_data['model_number'].notna().sum()
extraction_rate = extracted_count / len(complete_data) * 100
print(f"抽出数: {extracted_count}/{len(complete_data)}")
print(f"抽出率: {extraction_rate:.1f}%\n")

# ライン分類
print("【ライン分類】")
complete_data['line'] = complete_data['タイトル'].apply(classify_line)
line_counts = complete_data['line'].value_counts()
for line_name, count in line_counts.items():
    print(f"  {line_name}: {count}個")
print()

# 基本統計
median_price = complete_data['価格'].median()
mean_price = complete_data['価格'].mean()
std_price = complete_data['価格'].std()
cv_value = std_price / mean_price

print("【基本統計】")
print(f"全体中央値: ${median_price:.2f}")
print(f"全体平均値: ${mean_price:.2f}")
print(f"全体CV値: {cv_value:.3f}")
if len(watch_data) > 0:
    watch_median = watch_data['価格'].median()
    watch_mean = watch_data['価格'].mean()
    watch_cv = watch_data['価格'].std() / watch_data['価格'].mean()
    print(f"時計本体中央値: ${watch_median:.2f}")
    print(f"時計本体平均値: ${watch_mean:.2f}")
    print(f"時計本体CV値: {watch_cv:.3f}")
print()

# ============================================================
# HTMLセクション生成開始
# ============================================================
print("【HTML生成】")

# ============================================================
# セクション1: 基本統計
# ============================================================
basic_stats_html = f'''
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(brand_df)}</div>
                        <div class="stat-label">総販売数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${median_price:.0f}</div>
                        <div class="stat-label">中央値（全体）</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{cv_value:.2f}</div>
                        <div class="stat-label">CV値（ばらつき）</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{extraction_rate:.1f}%</div>
                        <div class="stat-label">型番抽出率</div>
                    </div>
                </div>
'''

# ============================================================
# TODO 6: セクション2: 仕入戦略
# ============================================================
strategy_html = f'''
                <div class="insight-box" style="background: linear-gradient(135deg, {brand_color_primary}15 0%, {brand_color_primary}05 100%); border-left: 4px solid {brand_color_primary};">
                    <h4 style="color: {brand_color_primary}; margin-top: 0;">⚠️ 重要：データの特性</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>ボックス・パーツ販売が多数</strong>（{len(box_data)}個/{len(complete_data)}個）</li>
                        <li>時計本体: {len(watch_data)}個のみ</li>
                        <li>中央値$173は<strong>ボックス価格</strong>を反映</li>
                        <li>時計本体の実際の価格帯: $2,000-10,000+</li>
                        <li>CV値2.560は極めて高い（価格幅が広い）</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, {brand_color_accent}15 0%, {brand_color_accent}05 100%); border-left: 4px solid {brand_color_accent};">
                    <h4 style="color: {brand_color_accent}; margin-top: 0;">💎 時計本体の狙い目</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Submariner</strong>（16610等）: 人気・流動性高</li>
                        <li><strong>Datejust</strong>（16233等）: 安定需要・幅広い価格帯</li>
                        <li><strong>Explorer</strong>（114270等）: エントリーモデル</li>
                        <li>型番明確・駆動方式記載のみ対象</li>
                        <li>完品（箱・保証書付き）は高値安定</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, #FF6B6B15 0%, #FF6B6B05 100%); border-left: 4px solid #FF6B6B;">
                    <h4 style="color: #FF6B6B; margin-top: 0;">⚠️ 避けるべき条件</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>ボックス・パーツのみ（利益率低・真贋リスク）</li>
                        <li>型番不明（"ROLEX Watch"のみの表記）</li>
                        <li>駆動方式不明（状態確認困難）</li>
                        <li>過度に低価格（$1000未満は要注意）</li>
                        <li>偽物リスク（専門知識必須）</li>
                    </ul>
                </div>
'''

# ============================================================
# セクション3: Plotlyグラフ用プレースホルダー
# ============================================================
graphs_html = f'''
                <div class="chart-grid">
                    <div class="chart-container">
                        <div id="rolex_price_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="rolex_category_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="rolex_movement_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="rolex_line_chart"></div>
                    </div>
                </div>
'''

# ============================================================
# セクション4: ボックス・パーツ分析
# ============================================================
box_analysis_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    📦 ボックス・パーツ vs 時計本体
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th>カテゴリ</th>
                            <th>販売数</th>
                            <th>比率</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                        </tr>
                    </thead>
                    <tbody>
'''

# ボックス・パーツ
box_median = box_data['価格'].median() if len(box_data) > 0 else 0
box_ratio = len(box_data) / len(complete_data) * 100
box_purchase_limit = int(box_median * 155 * 0.65) if box_median > 0 else 0

box_analysis_html += f'''
                        <tr>
                            <td><strong>ボックス・パーツ</strong></td>
                            <td>{len(box_data)}</td>
                            <td>{box_ratio:.1f}%</td>
                            <td>${box_median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{box_purchase_limit:,}</td>
                        </tr>
'''

# 時計本体
if len(watch_data) > 0:
    watch_median = watch_data['価格'].median()
    watch_ratio = len(watch_data) / len(complete_data) * 100
    watch_purchase_limit = int(watch_median * 155 * 0.65)

    box_analysis_html += f'''
                        <tr>
                            <td><strong>時計本体</strong></td>
                            <td>{len(watch_data)}</td>
                            <td>{watch_ratio:.1f}%</td>
                            <td>${watch_median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{watch_purchase_limit:,}</td>
                        </tr>
'''

box_analysis_html += '''
                    </tbody>
                </table>
'''

# ============================================================
# セクション5: ライン別型番Top15
# ============================================================
line_model_analysis_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    🏆 ライン別 人気型番 Top15
                </h3>
'''

# 型番が抽出できたデータのみ
model_data = complete_data[complete_data['model_number'].notna()].copy()

# ラインごとに型番を集計
for line_name in line_counts.index[:13]:  # 上位13ライン
    line_models = model_data[model_data['line'] == line_name]

    if len(line_models) == 0:
        continue

    # 型番ごとに統計を計算
    model_stats = line_models.groupby('model_number').agg({
        '価格': ['count', 'median', 'std', 'mean']
    }).round(2)
    model_stats.columns = ['count', 'median', 'std', 'mean']
    model_stats['cv'] = (model_stats['std'] / model_stats['mean']).round(3)
    model_stats = model_stats.sort_values('count', ascending=False).head(15)

    line_total = len(line_models)

    line_model_analysis_html += f'''
                <h4 style="color: {brand_color_primary}; margin-top: 25px; border-bottom: 2px solid {brand_color_primary}; padding-bottom: 5px;">
                    {line_name} <span style="font-size: 0.9em; color: #666;">（販売数: {line_total}個）</span>
                </h4>
                <table>
                    <thead>
                        <tr>
                            <th>順位</th>
                            <th>型番</th>
                            <th>販売数</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                            <th>CV値</th>
                            <th>商品例</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
'''

    for rank, (model_num, row) in enumerate(model_stats.iterrows(), 1):
        count = int(row['count'])
        median = row['median']
        cv = row['cv'] if pd.notna(row['cv']) else 0
        purchase_limit = int(median * 155 * 0.65)

        # 商品例を取得
        sample = line_models[line_models['model_number'] == model_num]['タイトル'].iloc[0]
        sample_short = sample[:50] + '...' if len(sample) > 50 else sample

        line_model_analysis_html += f'''
                        <tr>
                            <td><strong style="color: {brand_color_accent};">{rank}</strong></td>
                            <td><strong>{model_num}</strong></td>
                            <td>{count}</td>
                            <td>${median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{purchase_limit:,}</td>
                            <td>{cv:.3f}</td>
                            <td style="font-size: 0.85em;">{sample_short}</td>
                            <td>
                                <a href="https://www.ebay.com/sch/i.html?_nkw=ROLEX+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=ROLEX+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>
'''

    if len(model_stats) < 15:
        line_model_analysis_html += f'''
                        <tr style="background: #f8f9fa;">
                            <td colspan="8" style="text-align: center; color: #666; padding: 15px;">（{len(model_stats)}モデルのみ）</td>
                        </tr>
'''
    else:
        line_model_analysis_html += '''
                        <tr style="background: #f8f9fa;">
                            <td colspan="8" style="text-align: center; color: #666; padding: 15px;">... (15行まで続く)</td>
                        </tr>
'''

    line_model_analysis_html += '''
                    </tbody>
                </table>
'''

# ============================================================
# セクション6: ライン詳細分析
# ============================================================
line_detail_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    📊 ライン別 詳細分析
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th>ライン名</th>
                            <th>販売数</th>
                            <th>比率</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                            <th>CV値</th>
                            <th>安定性</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
'''

for line_name, count in line_counts.items():
    line_data = complete_data[complete_data['line'] == line_name]
    median = line_data['価格'].median()
    cv = line_data['価格'].std() / line_data['価格'].mean()
    ratio = count / len(complete_data) * 100
    purchase_limit = int(median * 155 * 0.65)

    # 安定性評価
    if cv <= 0.15:
        stability = '★★★'
    elif cv <= 0.25:
        stability = '★★☆'
    elif cv <= 0.30:
        stability = '★☆☆'
    else:
        stability = '☆☆☆'

    # 検索キーワード
    search_keyword = line_name.replace(' ', '+')

    line_detail_html += f'''
                        <tr>
                            <td><strong>{line_name}</strong></td>
                            <td>{count}</td>
                            <td>{ratio:.1f}%</td>
                            <td>${median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{purchase_limit:,}</td>
                            <td>{cv:.3f}</td>
                            <td>{stability}</td>
                            <td>
                                <a href="https://www.ebay.com/sch/i.html?_nkw=ROLEX+{search_keyword}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=ROLEX+{search_keyword}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>
'''

line_detail_html += '''
                    </tbody>
                </table>
'''

# ============================================================
# セクション7: 全ライン横断Top30
# ============================================================
top30_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    🌟 全ライン横断 Top30 型番
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th>順位</th>
                            <th>型番</th>
                            <th>ライン</th>
                            <th>販売数</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                            <th>CV値</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
'''

# 全ライン横断で型番を集計
all_model_stats = model_data.groupby(['model_number', 'line']).agg({
    '価格': ['count', 'median', 'std', 'mean']
}).round(2)
all_model_stats.columns = ['count', 'median', 'std', 'mean']
all_model_stats['cv'] = (all_model_stats['std'] / all_model_stats['mean']).round(3)
all_model_stats = all_model_stats.reset_index()
all_model_stats = all_model_stats.sort_values('count', ascending=False).head(30)

for rank, row in enumerate(all_model_stats.itertuples(), 1):
    model_num = row.model_number
    line_name = row.line
    count = int(row.count)
    median = row.median
    cv = row.cv if pd.notna(row.cv) else 0
    purchase_limit = int(median * 155 * 0.65)

    top30_html += f'''
                        <tr>
                            <td><strong style="color: {brand_color_accent};">{rank}</strong></td>
                            <td><strong>{model_num}</strong></td>
                            <td>{line_name}</td>
                            <td>{count}</td>
                            <td>${median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{purchase_limit:,}</td>
                            <td>{cv:.3f}</td>
                            <td>
                                <a href="https://www.ebay.com/sch/i.html?_nkw=ROLEX+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=ROLEX+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>
'''

top30_html += '''
                    </tbody>
                </table>
'''

# ============================================================
# セクション8: Plotlyグラフスクリプト生成
# ============================================================

# グラフ1: 価格帯別分析
price_bins = [0, 200, 500, 1000, 2000, 5000, 10000, 50000]
price_labels = ['$0-200', '$200-500', '$500-1000', '$1000-2000', '$2000-5000', '$5000-10000', '$10000+']
complete_data['price_range'] = pd.cut(complete_data['価格'], bins=price_bins, labels=price_labels)
price_dist = complete_data['price_range'].value_counts().sort_index()

price_chart_data = {
    'x': price_dist.index.tolist(),
    'y': price_dist.values.tolist(),
    'type': 'bar',
    'marker': {'color': brand_color_primary}
}

# グラフ2: ボックス vs 時計本体
category_dist = complete_data['is_box'].value_counts()
category_labels = ['時計本体' if k == False else 'ボックス・パーツ' for k in category_dist.index]
category_chart_data = {
    'labels': category_labels,
    'values': category_dist.values.tolist(),
    'type': 'pie',
    'marker': {'colors': [brand_color_primary, brand_color_accent]}
}

# グラフ3: 駆動方式別分布
movement_dist = complete_data['駆動方式'].value_counts()
movement_chart_data = {
    'labels': movement_dist.index.tolist(),
    'values': movement_dist.values.tolist(),
    'type': 'pie',
    'marker': {'colors': [brand_color_primary, brand_color_accent, '#666666', '#999999']}
}

# グラフ4: ライン別売上比率
line_dist = complete_data['line'].value_counts().head(10)
line_chart_data = {
    'labels': line_dist.index.tolist(),
    'values': line_dist.values.tolist(),
    'type': 'pie',
    'hole': 0.4
}

graph_scripts = f'''
        <script>
            // ROLEX - 価格帯別分析
            var rolex_price_data = [{price_chart_data}];
            var rolex_price_layout = {{
                title: '価格帯別 販売分布',
                xaxis: {{title: '価格帯'}},
                yaxis: {{title: '販売数'}},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('rolex_price_chart', rolex_price_data, rolex_price_layout, {{responsive: true}});

            // ROLEX - ボックス vs 時計本体
            var rolex_category_data = [{category_chart_data}];
            var rolex_category_layout = {{
                title: 'ボックス・パーツ vs 時計本体',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('rolex_category_chart', rolex_category_data, rolex_category_layout, {{responsive: true}});

            // ROLEX - 駆動方式別分布
            var rolex_movement_data = [{movement_chart_data}];
            var rolex_movement_layout = {{
                title: '駆動方式別 分布',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('rolex_movement_chart', rolex_movement_data, rolex_movement_layout, {{responsive: true}});

            // ROLEX - ライン別売上比率
            var rolex_line_data = [{line_chart_data}];
            var rolex_line_layout = {{
                title: 'ライン別 売上比率（Top10）',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('rolex_line_chart', rolex_line_data, rolex_line_layout, {{responsive: true}});
        </script>
'''

# ============================================================
# 完全なROLEXタブHTMLを組み立て
# ============================================================
brand_tab_html = f'''
            <div id="ROLEX" class="tab-content">
                <h2 style="color: {brand_color_primary}; border-bottom: 4px solid {brand_color_primary}; padding-bottom: 15px; margin-bottom: 25px;">
                    👑 ROLEX 詳細分析
                </h2>

                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px;">
                    📈 基本統計
                </h3>
{basic_stats_html}

                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    💡 仕入戦略
                </h3>
{strategy_html}

                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    📊 市場分析グラフ
                </h3>
{graphs_html}
{box_analysis_html}
{line_model_analysis_html}
{line_detail_html}
{top30_html}
            </div>
'''

# ============================================================
# TODO 7: index.htmlへの挿入
# ============================================================
print("【index.html 読み込み】")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("index.html読み込み完了\n")

# TAG HEUERタブの終了位置を検出
print("【TAG HEUERタブの終了位置を検出】")
tagheuer_start = html.find('<div id="TAG_HEUER" class="tab-content">')
if tagheuer_start == -1:
    print("エラー: TAG HEUERタブが見つかりません")
    exit(1)

# nest countingでTAG HEUERタブの終了位置を正確に検出
div_count = 1
search_pos = tagheuer_start + len('<div id="TAG_HEUER" class="tab-content">')

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        break

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        search_pos = next_close + 6
        if div_count == 0:
            tagheuer_end = next_close + 6
            break

print(f"TAG HEUERタブ終了位置: {tagheuer_end}\n")

# 既存のROLEXタブを削除
print("【既存のROLEXタブを削除】")
existing_start = html.find('<div id="ROLEX" class="tab-content">')
if existing_start != -1:
    div_count = 1
    search_pos = existing_start + len('<div id="ROLEX" class="tab-content">')

    while div_count > 0 and search_pos < len(html):
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            search_pos = next_close + 6
            if div_count == 0:
                existing_end = next_close + 6
                break

    html = html[:existing_start] + html[existing_end:]
    print("既存のROLEXタブを削除しました\n")
else:
    print("既存のROLEXタブは存在しません\n")

# TAG HEUERタブ直後に挿入
print("【ROLEXタブをTAG HEUER直後に挿入】")
html = html[:tagheuer_end] + '\n' + brand_tab_html + html[tagheuer_end:]
print("ROLEXタブを挿入しました\n")

# CSS追加
print("【CSS追加】")
rolex_css = f'''
        /* ROLEX固有のスタイル */
        #ROLEX .stat-card {{
            background: linear-gradient(135deg, {brand_color_primary}15 0%, {brand_color_primary}05 100%);
            border-top: 3px solid {brand_color_primary};
        }}

        #ROLEX .highlight {{
            background: linear-gradient(135deg, {brand_color_accent}25 0%, {brand_color_accent}10 100%);
        }}
'''

style_end = html.find('</style>')
if style_end != -1:
    html = html[:style_end] + rolex_css + html[style_end:]
    print("CSSを追加しました\n")

# JavaScriptグラフスクリプト追加
print("【グラフスクリプト追加】")
body_end = html.rfind('</body>')
if body_end != -1:
    html = html[:body_end] + graph_scripts + '\n' + html[body_end:]
    print("グラフスクリプトを追加しました\n")

# 保存
print("【index.html 保存】")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.htmlを保存しました\n")

print(f"{'='*80}")
print(f"{BRAND_NAME}タブの実装が完了しました！")
print(f"{'='*80}")
print(f"\n【実装内容サマリー】")
print(f"✓ 総販売数: {len(brand_df)}個")
print(f"✓ 型番抽出率: {extraction_rate:.1f}%")
print(f"✓ ライン数: {len(line_counts)}種類")
print(f"✓ ボックス・パーツ: {len(box_data)}個")
print(f"✓ 時計本体: {len(watch_data)}個")
print(f"✓ Plotlyグラフ: 4個")
print(f"✓ 挿入位置: TAG HEUER直後")
print(f"\n実装完了！")
