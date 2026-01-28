#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAG HEUERタブ完全実装スクリプト (v3)
template_brand_tab.pyを基準に8セクション構成で実装
"""

import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================
# TODO 1: ブランド名の設定
# ============================================================
BRAND_NAME = 'TAG HEUER'

# ============================================================
# TODO 2: ライン定義（TAG HEUER固有）
# ============================================================
TAG_HEUER_LINES = {
    'Professional': ['PROFESSIONAL', '2000', '3000', '4000', '6000'],
    'Formula 1': ['FORMULA 1', 'FORMULA1', 'F1'],
    'Carrera': ['CARRERA'],
    'Link': ['LINK'],
    'Aquaracer': ['AQUARACER'],
    'Connected': ['CONNECTED'],
    'Monaco': ['MONACO'],
    'Autavia': ['AUTAVIA'],
}

def classify_line(title):
    """タイトルからラインを分類"""
    title_upper = str(title).upper()
    for line_name, keywords in TAG_HEUER_LINES.items():
        for keyword in keywords:
            if keyword in title_upper:
                return line_name
    return f'その他{BRAND_NAME}'

# ============================================================
# TODO 3: 型番抽出関数（TAG HEUER固有）
# ============================================================
def extract_model_number(title):
    """
    TAG HEUERの型番を抽出（9パターン）
    優先順位: 新しいW系 > Carrera系 > CG系 > 古いW系 > S系 > 3桁.3桁
    """
    title_upper = str(title).upper()

    # Pattern 1: 最新W系 (WAZ1010, WAH1110, WBN2111.BA0627)
    match = re.search(r'\b(W[A-Z]{2}\d{4}(?:\.[A-Z]{2}\d{4})?)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 3: Carrera系 (CAR2111, CAZ1011, CAH1111)
    match = re.search(r'\b(CA[RZVH]\d{4})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 9: CBE/CBA等最新 (CBE2110, CBN2011)
    match = re.search(r'\b(CB[EAN]\d{4})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 8: CG系 (CG1123-0)
    match = re.search(r'\b(CG\d{4}-\d)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 2: C系汎用 (CN1111, CW2111, CS2111)
    match = re.search(r'\b(C[NWSAVK]\d{4})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 4: CV/CB系 (CV2014, CB1111)
    match = re.search(r'\b(C[VB]\d{4})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 7: 古いW系 (WE1210, WK1110, WG1212-K0)
    match = re.search(r'\b(W[EKGN]\d{4}(?:-[A-Z]\d)?)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 5: S系古い型番 (S90.813, S95.715)
    match = re.search(r'\b(S\d{2}\.\d{3}[A-Z]?)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 6: 3桁.3桁 (962.213, 934.206) - 最後に判定
    match = re.search(r'\b(\d{3}\.\d{3}[A-Z]?)\b', title_upper)
    if match:
        return match.group(1)

    return None

# ============================================================
# TODO 4: キャラクター・コラボ定義
# ============================================================
TAG_HEUER_COLLABORATIONS = {
    'Ayrton Senna': ['SENNA', 'AYRTON'],
    'Gulf': ['GULF'],
}

def detect_collaboration(title):
    """タイトルからコラボを検出"""
    title_upper = str(title).upper()
    for collab_name, keywords in TAG_HEUER_COLLABORATIONS.items():
        for keyword in keywords:
            if keyword in title_upper:
                return collab_name
    return None

# ============================================================
# TODO 5: ブランドカラー設定
# ============================================================
brand_color_primary = '#D0021B'  # TAG HEUERレッド
brand_color_accent = '#000000'   # ブラック

# ============================================================
# データ読み込みと分析
# ============================================================
print(f"{'='*80}")
print(f"{BRAND_NAME}タブ 完全実装スクリプト")
print(f"{'='*80}\n")

# CSVファイルを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# TAG HEUERのデータを抽出
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

# コラボ検出
print("【コラボ検出】")
complete_data['collaboration'] = complete_data['タイトル'].apply(detect_collaboration)
collab_data = complete_data[complete_data['collaboration'].notna()]
print(f"コラボ商品: {len(collab_data)}個")
if len(collab_data) > 0:
    collab_counts = collab_data['collaboration'].value_counts()
    for collab_name, count in collab_counts.items():
        print(f"  {collab_name}: {count}個")
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
                        <li><strong>Professional</strong>シリーズ（販売数最多・安定）</li>
                        <li><strong>Formula 1</strong>エントリーモデル（$300-500）</li>
                        <li>型番：<strong>CAZ1011, WK1110, 962.208</strong>など人気モデル</li>
                        <li><strong>Ayrton Senna</strong>限定版（プレミアム価格）</li>
                        <li>クロノグラフ機能付き（需要高）</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, #FF6B6B15 0%, #FF6B6B05 100%); border-left: 4px solid #FF6B6B;">
                    <h4 style="color: #FF6B6B; margin-top: 0;">⚠️ 避けるべき条件</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>CV値 &gt; 1.0 の高ばらつきモデル</li>
                        <li>Connected（スマートウォッチ）は価値下落リスク</li>
                        <li>レディースモデル（需要限定的）</li>
                        <li>状態不明・箱なし（減額要因）</li>
                        <li>古すぎるS系・3桁型番（部品入手困難）</li>
                    </ul>
                </div>

                <div class="insight-box" style="background: linear-gradient(135deg, #4ECDC415 0%, #4ECDC405 100%); border-left: 4px solid #4ECDC4;">
                    <h4 style="color: #4ECDC4; margin-top: 0;">📊 価格帯別ガイド</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>$200-400</strong>: Professional・Formula 1 クオーツ（回転早）</li>
                        <li><strong>$400-800</strong>: Carrera・Link 自動巻（安定需要）</li>
                        <li><strong>$800-1,500</strong>: Carrera クロノグラフ（利益率高）</li>
                        <li><strong>$1,500+</strong>: Monaco・Autavia・限定版（要専門知識）</li>
                    </ul>
                </div>
'''

# ============================================================
# セクション3: Plotlyグラフ用プレースホルダー
# ============================================================
graphs_html = f'''
                <div class="chart-grid">
                    <div class="chart-container">
                        <div id="tagheuer_price_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="tagheuer_movement_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="tagheuer_gender_chart"></div>
                    </div>
                    <div class="chart-container">
                        <div id="tagheuer_line_chart"></div>
                    </div>
                </div>
'''

# ============================================================
# セクション4: コラボ別分析
# ============================================================
collab_analysis_html = ''
if len(collab_data) > 0:
    collab_analysis_html = f'''
                <h3 style="color: {brand_color_primary}; border-bottom: 3px solid {brand_color_primary}; padding-bottom: 10px; margin-top: 30px;">
                    🤝 コラボレーション・特別版 分析
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th>コラボレーション</th>
                            <th>販売数</th>
                            <th>比率</th>
                            <th>中央値</th>
                            <th style="background: {brand_color_accent}; color: white;">仕入上限(¥)</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
'''

    collab_stats = collab_data.groupby('collaboration').agg({
        '価格': ['count', 'median']
    }).round(2)
    collab_stats.columns = ['count', 'median']
    collab_stats = collab_stats.sort_values('count', ascending=False)

    for collab_name, row in collab_stats.iterrows():
        count = int(row['count'])
        median = row['median']
        ratio = count / len(collab_data) * 100
        purchase_limit = int(median * 155 * 0.65)

        search_keyword = collab_name.replace(' ', '+')

        collab_analysis_html += f'''
                        <tr>
                            <td><strong>{collab_name}</strong></td>
                            <td>{count}</td>
                            <td>{ratio:.1f}%</td>
                            <td>${median:.0f}</td>
                            <td class="highlight" style="color: {brand_color_accent}; font-weight: bold;">¥{purchase_limit:,}</td>
                            <td>
                                <a href="https://www.ebay.com/sch/i.html?_nkw=TAG+HEUER+{search_keyword}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=TAG+HEUER+{search_keyword}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>
'''

    collab_analysis_html += '''
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=TAG+HEUER+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=TAG+HEUER+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=TAG+HEUER+{search_keyword}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=TAG+HEUER+{search_keyword}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
                                <a href="https://www.ebay.com/sch/i.html?_nkw=TAG+HEUER+{model_num}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="https://jp.mercari.com/search?keyword=TAG+HEUER+{model_num}" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
price_bins = [0, 200, 400, 600, 800, 1000, 1500, 2000, 5000]
price_labels = ['$0-200', '$200-400', '$400-600', '$600-800', '$800-1000', '$1000-1500', '$1500-2000', '$2000+']
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
            // TAG HEUER - 価格帯別分析
            var tagheuer_price_data = [{price_chart_data}];
            var tagheuer_price_layout = {{
                title: '価格帯別 販売分布',
                xaxis: {{title: '価格帯'}},
                yaxis: {{title: '販売数'}},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('tagheuer_price_chart', tagheuer_price_data, tagheuer_price_layout, {{responsive: true}});

            // TAG HEUER - 駆動方式別分布
            var tagheuer_movement_data = [{movement_chart_data}];
            var tagheuer_movement_layout = {{
                title: '駆動方式別 分布',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('tagheuer_movement_chart', tagheuer_movement_data, tagheuer_movement_layout, {{responsive: true}});

            // TAG HEUER - 性別・カテゴリー別
            var tagheuer_gender_data = [{gender_chart_data}];
            var tagheuer_gender_layout = {{
                title: '性別・カテゴリー別 販売数',
                xaxis: {{title: 'カテゴリー'}},
                yaxis: {{title: '販売数'}},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('tagheuer_gender_chart', tagheuer_gender_data, tagheuer_gender_layout, {{responsive: true}});

            // TAG HEUER - ライン別売上比率
            var tagheuer_line_data = [{line_chart_data}];
            var tagheuer_line_layout = {{
                title: 'ライン別 売上比率',
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: '#ffffff'
            }};
            Plotly.newPlot('tagheuer_line_chart', tagheuer_line_data, tagheuer_line_layout, {{responsive: true}});
        </script>
'''

# ============================================================
# 完全なTAG HEUERタブHTMLを組み立て
# ============================================================
brand_tab_html = f'''
            <div id="TAG_HEUER" class="tab-content">
                <h2 style="color: {brand_color_primary}; border-bottom: 4px solid {brand_color_primary}; padding-bottom: 15px; margin-bottom: 25px;">
                    🔴 TAG HEUER 詳細分析
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
{collab_analysis_html}
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

# GUCCIタブの終了位置を検出
print("【GUCCIタブの終了位置を検出】")
gucci_start = html.find('<div id="GUCCI" class="tab-content">')
if gucci_start == -1:
    print("エラー: GUCCIタブが見つかりません")
    exit(1)

# nest countingでGUCCIタブの終了位置を正確に検出
div_count = 1
search_pos = gucci_start + len('<div id="GUCCI" class="tab-content">')

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
            gucci_end = next_close + 6
            break

print(f"GUCCIタブ終了位置: {gucci_end}\n")

# 既存のTAG HEUERタブを削除
print("【既存のTAG HEUERタブを削除】")
existing_start = html.find('<div id="TAG_HEUER" class="tab-content">')
if existing_start != -1:
    div_count = 1
    search_pos = existing_start + len('<div id="TAG_HEUER" class="tab-content">')

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
    print("既存のTAG HEUERタブを削除しました\n")
else:
    print("既存のTAG HEUERタブは存在しません\n")

# GUCCIタブ直後に挿入
print("【TAG HEUERタブをGUCCI直後に挿入】")
html = html[:gucci_end] + '\n' + brand_tab_html + html[gucci_end:]
print("TAG HEUERタブを挿入しました\n")

# CSS追加
print("【CSS追加】")
tagheuer_css = f'''
        /* TAG HEUER固有のスタイル */
        #TAG_HEUER .stat-card {{
            background: linear-gradient(135deg, {brand_color_primary}15 0%, {brand_color_primary}05 100%);
            border-top: 3px solid {brand_color_primary};
        }}

        #TAG_HEUER .highlight {{
            background: linear-gradient(135deg, {brand_color_accent}25 0%, {brand_color_accent}10 100%);
        }}
'''

style_end = html.find('</style>')
if style_end != -1:
    html = html[:style_end] + tagheuer_css + html[style_end:]
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
print(f"✓ コラボ商品: {len(collab_data)}個")
print(f"✓ Plotlyグラフ: 4個")
print(f"✓ 挿入位置: GUCCI直後")
print(f"\n実装完了！")
