#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hamiltonタブ完全実装スクリプト (v3)
template_brand_tab.pyを基準に8セクション構成で実装
"""

import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================
# TODO 1: ブランド名の設定
# ============================================================
BRAND_NAME = 'Hamilton'

# ============================================================
# TODO 2: ライン定義（Hamilton固有）
# ============================================================
HAMILTON_LINES = {
    'Jazzmaster': ['JAZZMASTER', 'JAZZ MASTER'],
    'Khaki Field': ['KHAKI FIELD', 'KHAKI-FIELD'],
    'Ventura': ['VENTURA'],
    'Khaki Aviation': ['KHAKI AVIATION', 'KHAKI PILOT', 'KHAKI AIR', 'X-WIND'],
    'American Classic': ['AMERICAN CLASSIC'],
    'Khaki Navy': ['KHAKI NAVY', 'KHAKI SUB'],
    'Intra-Matic': ['INTRA-MATIC', 'INTRAMATIC'],
    'Broadway': ['BROADWAY'],
}

def classify_line(title):
    """タイトルからラインを分類"""
    title_upper = str(title).upper()
    for line_name, keywords in HAMILTON_LINES.items():
        for keyword in keywords:
            if keyword in title_upper:
                return line_name
    return f'その他{BRAND_NAME}'

# ============================================================
# TODO 3: 型番抽出関数（Hamilton固有）
# ============================================================
def extract_model_number(title):
    """
    Hamiltonの型番を抽出
    Pattern 1: H + 5-10桁数字（主要パターン）
    Pattern 2: 数字のみ 6-8桁（補助パターン）
    """
    title_upper = str(title).upper()

    # Pattern 1: H + 5-10桁数字（H384110, H24555331など）
    match = re.search(r'\b(H\d{5,10})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 2: 数字のみ 6-8桁（706050, 326651など）
    match = re.search(r'\b(\d{6,8})\b', title_upper)
    if match:
        model = match.group(1)
        # 年号を除外（1900-2025）
        if not (1900 <= int(model[:4]) <= 2025):
            return model

    return None

# ============================================================
# TODO 4: 特別版・コラボ定義
# ============================================================
HAMILTON_SPECIAL = {
    'Elvis Edition': ['ELVIS'],
    'Tokyo Cat Street': ['TOKYO CAT STREET', 'CAT STREET'],
}

def detect_special_edition(title):
    """タイトルから特別版を検出"""
    title_upper = str(title).upper()
    for special_name, keywords in HAMILTON_SPECIAL.items():
        for keyword in keywords:
            if keyword in title_upper:
                return special_name
    return None

# ============================================================
# TODO 5: ブランドカラー設定
# ============================================================
brand_color_primary = '#002855'  # Hamiltonネイビー
brand_color_accent = '#C8A882'   # ベージュゴールド

# ============================================================
# データ読み込みと分析
# ============================================================
print(f"{'='*80}")
print(f"{BRAND_NAME}タブ 完全実装スクリプト")
print(f"{'='*80}\n")

# CSVファイルを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# Hamiltonのデータを抽出
brand_df = df[df['ブランド'] == BRAND_NAME].copy()
complete_data = brand_df.dropna(subset=['価格'])

print(f"【データ読み込み】")
print(f"総販売数: {len(brand_df)}個")
print(f"完全データ: {len(complete_data)}個\n")

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

# 特別版検出
print("【特別版検出】")
complete_data['special_edition'] = complete_data['タイトル'].apply(detect_special_edition)
special_data = complete_data[complete_data['special_edition'].notna()]
print(f"特別版商品: {len(special_data)}個")
if len(special_data) > 0:
    special_counts = special_data['special_edition'].value_counts()
    for special_name, count in special_counts.items():
        print(f"  {special_name}: {count}個")
print()

# 基本統計
median_price = complete_data['価格'].median()
mean_price = complete_data['価格'].mean()
std_price = complete_data['価格'].std()
cv_value = std_price / mean_price

print("【基本統計】")
print(f"中央値: ${median_price:.2f}")
print(f"平均値: ${mean_price:.2f}")
print(f"標準偏差: ${std_price:.2f}")
print(f"CV値: {cv_value:.3f}\n")

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
                        <div class="stat-label">中央値</div>
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
                    <h4 style="color: {brand_color_primary}; margin-top: 0;">💎 狙い目の条件</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Ventura</strong>: アイコニックな三角形ケース、コレクター人気</li>
                        <li><strong>Jazzmaster</strong>: 最多販売数、安定需要</li>
                        <li><strong>Khaki Field</strong>: ミリタリースタイル、男性人気</li>
                        <li>自動巻 &gt; クオーツ（付加価値高）</li>
                        <li>Elvis Edition等の特別版（プレミアム価格）</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, #FF6B6B15 0%, #FF6B6B05 100%); border-left: 4px solid #FF6B6B;">
                    <h4 style="color: #FF6B6B; margin-top: 0;">⚠️ 避けるべき条件</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>CV値 &gt; 0.8 の高ばらつきモデル</li>
                        <li>型番不明（"Hamilton Watch"のみの表記）</li>
                        <li>状態不明・箱なし（減額要因）</li>
                        <li>レディースモデル（需要限定的）</li>
                        <li>過度に低価格（$200未満は要注意）</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, {brand_color_accent}15 0%, {brand_color_accent}05 100%); border-left: 4px solid {brand_color_accent};">
                    <h4 style="color: {brand_color_accent}; margin-top: 0;">📊 価格帯別ガイド</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>$200-400</strong>: Khaki Field クオーツ、エントリーモデル</li>
                        <li><strong>$400-600</strong>: Jazzmaster・Khaki 自動巻（安定需要）</li>
                        <li><strong>$600-1,000</strong>: Ventura・特別版（高利益率）</li>
                        <li><strong>$1,000+</strong>: ヴィンテージ・限定版（要専門知識）</li>
                    </ul>
                </div>
'''

# ============================================================
# セクション3: Plotlyグラフ用プレースホルダー
# ============================================================
graphs_html = f'''
                <div class="chart-grid">
                    <div class="chart-container">
                        <div id="hamilton_price_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="hamilton_movement_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="hamilton_gender_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="hamilton_line_chart"></div>
                    </div>
                </div>
'''

# ============================================================
# セクション4: 特別版分析
# ============================================================
special_analysis_html = ''
if len(special_data) > 0:
    special_analysis_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    ⭐ 特別版・限定モデル 分析
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th>特別版</th>
                            <th>販売数</th>
                            <th>比率</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
'''

    special_stats = special_data.groupby('special_edition').agg({
        '価格': ['count', 'median']
    }).round(2)
    special_stats.columns = ['count', 'median']
    special_stats = special_stats.sort_values('count', ascending=False)

    for special_name, row in special_stats.iterrows():
        count = int(row['count'])
        median = row['median']
        ratio = count / len(special_data) * 100
        purchase_limit = int(median * 155 * 0.65)

        search_keyword = special_name.replace(' ', '+')

        special_analysis_html += f'''
                        <tr>
                            <td><strong>{special_name}</strong></td>
                            <td>{count}</td>
                            <td>{ratio:.1f}%</td>
                            <td>${median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{purchase_limit:,}</td>
                            <td>
                                <a href="https://www.ebay.com/sch/i.html?_nkw=Hamilton+{search_keyword}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=Hamilton+{search_keyword}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>
'''

    special_analysis_html += '''
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
for line_name in line_counts.index[:9]:  # 上位9ライン
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=Hamilton+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=Hamilton+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
# セクション6: ライン詳細分析（仕入上限・検索リンク含む）
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=Hamilton+{search_keyword}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=Hamilton+{search_keyword}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=Hamilton+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=Hamilton+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
price_bins = [0, 200, 400, 600, 800, 1000, 1500, 5000]
price_labels = ['$0-200', '$200-400', '$400-600', '$600-800', '$800-1000', '$1000-1500', '$1500+']
complete_data['price_range'] = pd.cut(complete_data['価格'], bins=price_bins, labels=price_labels)
price_dist = complete_data['price_range'].value_counts().sort_index()

price_chart_data = {
    'x': price_dist.index.tolist(),
    'y': price_dist.values.tolist(),
    'type': 'bar',
    'marker': {'color': brand_color_primary}
}

# グラフ2: 駆動方式別分布
movement_dist = complete_data['駆動方式'].value_counts()
movement_chart_data = {
    'labels': movement_dist.index.tolist(),
    'values': movement_dist.values.tolist(),
    'type': 'pie',
    'marker': {'colors': [brand_color_primary, brand_color_accent, '#666666', '#999999', '#CCCCCC']}
}

# グラフ3: 性別・カテゴリー別
gender_dist = complete_data['デパートメント'].value_counts()
gender_chart_data = {
    'x': gender_dist.index.tolist(),
    'y': gender_dist.values.tolist(),
    'type': 'bar',
    'marker': {'color': brand_color_accent}
}

# グラフ4: ライン別売上比率
line_dist = complete_data['line'].value_counts().head(8)
line_chart_data = {
    'labels': line_dist.index.tolist(),
    'values': line_dist.values.tolist(),
    'type': 'pie',
    'hole': 0.4
}

graph_scripts = f'''
        <script>
            // Hamilton - 価格帯別分析
            var hamilton_price_data = [{price_chart_data}];
            var hamilton_price_layout = {{
                title: '価格帯別 販売分布',
                xaxis: {{title: '価格帯'}},
                yaxis: {{title: '販売数'}},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('hamilton_price_chart', hamilton_price_data, hamilton_price_layout, {{responsive: true}});

            // Hamilton - 駆動方式別分布
            var hamilton_movement_data = [{movement_chart_data}];
            var hamilton_movement_layout = {{
                title: '駆動方式別 分布',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('hamilton_movement_chart', hamilton_movement_data, hamilton_movement_layout, {{responsive: true}});

            // Hamilton - 性別・カテゴリー別
            var hamilton_gender_data = [{gender_chart_data}];
            var hamilton_gender_layout = {{
                title: '性別・カテゴリー別 販売数',
                xaxis: {{title: 'カテゴリー'}},
                yaxis: {{title: '販売数'}},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('hamilton_gender_chart', hamilton_gender_data, hamilton_gender_layout, {{responsive: true}});

            // Hamilton - ライン別売上比率
            var hamilton_line_data = [{line_chart_data}];
            var hamilton_line_layout = {{
                title: 'ライン別 売上比率',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('hamilton_line_chart', hamilton_line_data, hamilton_line_layout, {{responsive: true}});
        </script>
'''

# ============================================================
# 完全なHamiltonタブHTMLを組み立て
# ============================================================
brand_tab_html = f'''
            <div id="Hamilton" class="tab-content">
                <h2 style="color: {brand_color_primary}; border-bottom: 4px solid {brand_color_primary}; padding-bottom: 15px; margin-bottom: 25px;">
                    ⚓ Hamilton 詳細分析
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
{special_analysis_html}
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

# ROLEXタブの終了位置を検出
print("【ROLEXタブの終了位置を検出】")
rolex_start = html.find('<div id="ROLEX" class="tab-content">')
if rolex_start == -1:
    print("エラー: ROLEXタブが見つかりません")
    exit(1)

# nest countingでROLEXタブの終了位置を正確に検出
div_count = 1
search_pos = rolex_start + len('<div id="ROLEX" class="tab-content">')

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
            rolex_end = next_close + 6
            break

print(f"ROLEXタブ終了位置: {rolex_end}\n")

# 既存のHamiltonタブを削除
print("【既存のHamiltonタブを削除】")
existing_start = html.find('<div id="Hamilton" class="tab-content">')
if existing_start != -1:
    div_count = 1
    search_pos = existing_start + len('<div id="Hamilton" class="tab-content">')

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
    print("既存のHamiltonタブを削除しました\n")
else:
    print("既存のHamiltonタブは存在しません\n")

# ROLEXタブ直後に挿入
print("【HamiltonタブをROLEX直後に挿入】")
html = html[:rolex_end] + '\n' + brand_tab_html + html[rolex_end:]
print("Hamiltonタブを挿入しました\n")

# CSS追加
print("【CSS追加】")
hamilton_css = f'''
        /* Hamilton固有のスタイル */
        #Hamilton .stat-card {{
            background: linear-gradient(135deg, {brand_color_primary}15 0%, {brand_color_primary}05 100%);
            border-top: 3px solid {brand_color_primary};
        }}

        #Hamilton .highlight {{
            background: linear-gradient(135deg, {brand_color_accent}25 0%, {brand_color_accent}10 100%);
        }}
'''

style_end = html.find('</style>')
if style_end != -1:
    html = html[:style_end] + hamilton_css + html[style_end:]
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
print(f"✓ 特別版: {len(special_data)}個")
print(f"✓ Plotlyグラフ: 4個")
print(f"✓ 挿入位置: ROLEX直後")
print(f"\n実装完了！")
