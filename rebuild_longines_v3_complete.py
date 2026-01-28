#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Longinesタブ完全実装スクリプト (v3)
template_brand_tab.pyを基準に8セクション構成で実装
"""

import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================
# TODO 1: ブランド名の設定
# ============================================================
BRAND_NAME = 'Longines'

# ============================================================
# TODO 2: ライン定義（Longines固有）
# ============================================================
LONGINES_LINES = {
    'Conquest': ['CONQUEST'],
    'Flagship': ['FLAGSHIP'],
    'DolceVita': ['DOLCEVITA', 'DOLCE VITA'],
    'Heritage': ['HERITAGE'],
    'Master Collection': ['MASTER COLLECTION', 'MASTER'],
    'HydroConquest': ['HYDROCONQUEST', 'HYDRO CONQUEST'],
    'Spirit': ['SPIRIT'],
    'Legend Diver': ['LEGEND DIVER', 'LEGEND'],
}

def classify_line(title):
    """タイトルからラインを分類"""
    title_upper = str(title).upper()
    for line_name, keywords in LONGINES_LINES.items():
        for keyword in keywords:
            if keyword in title_upper:
                return line_name
    return f'その他{BRAND_NAME}'

# ============================================================
# TODO 3: 型番抽出関数（Longines固有）
# ============================================================
def extract_model_number(title):
    """
    Longinesの型番を抽出
    Pattern 1: L + 数字.数字.数字（最優先）
    Pattern 2: L + 数字.数字（主要パターン）
    Pattern 3: L + 5-10桁（補助）
    Pattern 4: 数字-数字（補助）
    """
    title_upper = str(title).upper()

    # Pattern 1: L + 数字.数字.数字
    match = re.search(r'\b(L\d+\.\d+\.\d+)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 2: L + 数字.数字
    match = re.search(r'\b(L\d+\.\d+)\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 3: L + 5-10桁
    match = re.search(r'\b(L\d{5,10})\b', title_upper)
    if match:
        return match.group(1)

    # Pattern 4: 数字-数字
    match = re.search(r'\b(\d{3,4}-\d{2,4})\b', title_upper)
    if match:
        return match.group(1)

    return None

# ============================================================
# TODO 4: 特別版・コラボの定義（Longines固有）
# ============================================================
LONGINES_SPECIAL = {
    'Navigation Limited': ['NAVIGATION LIMITED', 'NAVIGATION 3000'],
    '150th Anniversary': ['150TH ANNIVERSARY', '150 ANNIVERSARY'],
    '165th Anniversary': ['165TH ANNIVERSARY', '165 ANNIVERSARY'],
    'Chronometer': ['CHRONOMETER', 'COSC'],
}

def classify_special(title):
    """タイトルから特別版を分類"""
    title_upper = str(title).upper()
    for special_name, keywords in LONGINES_SPECIAL.items():
        for keyword in keywords:
            if keyword in title_upper:
                return special_name
    return None

# ============================================================
# TODO 5: ブランドカラーの設定
# ============================================================
BRAND_COLOR_PRIMARY = '#003057'  # Longinesネイビー
BRAND_COLOR_ACCENT = '#D4AF37'   # ゴールド

# ============================================================
# メイン処理
# ============================================================

print("=" * 60)
print(f"{BRAND_NAME}タブ完全実装スクリプト")
print("=" * 60)

# データ読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# Longinesのデータを抽出
brand_df = df[df['ブランド'] == BRAND_NAME].copy()

print(f"\n✅ {BRAND_NAME}データ抽出: {len(brand_df)}個")

# 型番抽出
brand_df['型番'] = brand_df['タイトル'].apply(extract_model_number)
extracted_count = brand_df['型番'].notna().sum()
extraction_rate = (extracted_count / len(brand_df)) * 100

print(f"✅ 型番抽出: {extracted_count}個 ({extraction_rate:.1f}%)")

# ライン分類
brand_df['ライン'] = brand_df['タイトル'].apply(classify_line)
line_counts = brand_df['ライン'].value_counts()

print(f"✅ ライン分類: {len(line_counts)}ライン")
for line_name, count in line_counts.items():
    print(f"   - {line_name}: {count}個")

# 特別版分類
brand_df['特別版'] = brand_df['タイトル'].apply(classify_special)
special_counts = brand_df['特別版'].value_counts()

print(f"✅ 特別版: {len(special_counts)}種類")
for special_name, count in special_counts.items():
    print(f"   - {special_name}: {count}個")

# 統計計算
median_price = brand_df['価格'].median()
mean_price = brand_df['価格'].mean()
std_price = brand_df['価格'].std()
cv_value = std_price / mean_price

print(f"\n📊 統計:")
print(f"   - 中央値: ${median_price:.2f}")
print(f"   - 平均値: ${mean_price:.2f}")
print(f"   - CV値: {cv_value:.3f}")

# ============================================================
# HTML生成
# ============================================================

print("\n" + "=" * 60)
print("HTML生成開始")
print("=" * 60)

# ============================================================
# セクション1: 基本統計
# ============================================================
section1_basic_stats = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                📊 基本統計
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">総販売数</div>
                    <div class="stat-value">{len(brand_df)}個</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">中央値</div>
                    <div class="stat-value">${median_price:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">CV値</div>
                    <div class="stat-value">{cv_value:.3f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">型番抽出率</div>
                    <div class="stat-value">{extraction_rate:.1f}%</div>
                </div>
            </div>
        </div>
'''

# ============================================================
# セクション2: 仕入戦略
# ============================================================

# ライン別中央値計算
line_stats = {}
for line_name in line_counts.index[:8]:  # 上位8ライン
    line_data = brand_df[brand_df['ライン'] == line_name]
    line_median = line_data['価格'].median()
    line_count = len(line_data)
    line_stats[line_name] = {'median': line_median, 'count': line_count}

# 仕入戦略テキスト生成
strategy_lines = []
for line_name, stats in sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
    purchase_limit_usd = stats['median'] * 0.65
    purchase_limit_jpy = int(purchase_limit_usd * 155)
    strategy_lines.append(
        f"            <li><strong>{line_name}</strong>: 販売数{stats['count']}個、中央値${stats['median']:.0f} → 仕入上限¥{purchase_limit_jpy:,}</li>"
    )

section2_strategy = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                💡 仕入戦略
            </div>
            <div style="padding: 20px; line-height: 1.8;">
                <h3 style="color: {BRAND_COLOR_PRIMARY}; margin-top: 0;">注目ライン</h3>
                <ul style="margin: 10px 0; padding-left: 30px;">
{''.join(strategy_lines)}
                </ul>
                <h3 style="color: {BRAND_COLOR_PRIMARY};">特別版・限定モデル</h3>
                <ul style="margin: 10px 0; padding-left: 30px;">
                    <li><strong>Navigation Limited</strong>: 3000本限定モデル</li>
                    <li><strong>Anniversary Models</strong>: 150周年、165周年記念モデル</li>
                    <li><strong>Chronometer</strong>: COSC認定高精度モデル</li>
                </ul>
            </div>
        </div>
'''

# ============================================================
# セクション3: 市場分析グラフ（Plotly × 4個）
# ============================================================

section3_graphs = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                📈 市場分析グラフ
            </div>
            <div class="graph-grid">
                <div id="longines_price_chart" class="graph-item"></div>
                <div id="longines_movement_chart" class="graph-item"></div>
                <div id="longines_gender_chart" class="graph-item"></div>
                <div id="longines_line_chart" class="graph-item"></div>
            </div>
        </div>
'''

# ============================================================
# セクション4: 特別版・限定モデル 分析
# ============================================================

special_df = brand_df[brand_df['特別版'].notna()].copy()
special_stats = special_df.groupby('特別版').agg({
    '価格': ['count', 'median', 'mean', 'std']
}).round(2)

special_rows = []
for special_name in special_stats.index:
    count = int(special_stats.loc[special_name, ('価格', 'count')])
    median = special_stats.loc[special_name, ('価格', 'median')]
    mean = special_stats.loc[special_name, ('価格', 'mean')]
    std_val = special_stats.loc[special_name, ('価格', 'std')]
    cv = std_val / mean if mean > 0 else 0

    purchase_limit_usd = median * 0.65
    purchase_limit_jpy = int(purchase_limit_usd * 155)

    ebay_keyword = f"{BRAND_NAME}+{special_name.replace(' ', '+')}"
    mercari_keyword = f"{BRAND_NAME}%20{special_name.replace(' ', '%20')}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={ebay_keyword}+Watch&LH_Sold=1&LH_Complete=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={mercari_keyword}%20時計&status=on_sale"

    special_rows.append(f'''
                    <tr>
                        <td><strong>{special_name}</strong></td>
                        <td>{count}</td>
                        <td>${median:.2f}</td>
                        <td>{cv:.3f}</td>
                        <td style="background: {BRAND_COLOR_ACCENT}; color: white; font-weight: bold;">¥{purchase_limit_jpy:,}</td>
                        <td>
                            <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>''')

section4_special = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                🏆 特別版・限定モデル 分析
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr style="background: {BRAND_COLOR_PRIMARY};">
                            <th>特別版名</th>
                            <th>販売数</th>
                            <th>中央値</th>
                            <th>CV値</th>
                            <th style="background: {BRAND_COLOR_ACCENT}; color: white;">仕入上限(¥)</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
{''.join(special_rows)}
                    </tbody>
                </table>
            </div>
        </div>
'''

# ============================================================
# セクション5: ライン別型番Top15（8ライン）
# ============================================================

section5_lines = []

for line_name in line_counts.index[:8]:  # 上位8ライン
    line_data = brand_df[brand_df['ライン'] == line_name].copy()
    line_data = line_data[line_data['型番'].notna()]

    if len(line_data) == 0:
        continue

    model_stats = line_data.groupby('型番').agg({
        '価格': ['count', 'median']
    }).round(2)
    model_stats.columns = ['販売数', '中央値']
    model_stats = model_stats.sort_values('販売数', ascending=False).head(15)

    model_rows = []
    for idx, (model, row) in enumerate(model_stats.iterrows(), 1):
        sales = int(row['販売数'])
        median = row['中央値']

        purchase_limit_usd = median * 0.65
        purchase_limit_jpy = int(purchase_limit_usd * 155)

        ebay_keyword = f"{BRAND_NAME}+{model.replace(' ', '+')}"
        mercari_keyword = f"{BRAND_NAME}%20{model.replace(' ', '%20')}"
        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={ebay_keyword}&LH_Sold=1&LH_Complete=1"
        mercari_url = f"https://jp.mercari.com/search?keyword={mercari_keyword}&status=on_sale"

        model_rows.append(f'''
                        <tr>
                            <td>{idx}</td>
                            <td><strong>{model}</strong></td>
                            <td>{sales}</td>
                            <td>${median:.2f}</td>
                            <td style="background: {BRAND_COLOR_ACCENT}; color: white; font-weight: bold;">¥{purchase_limit_jpy:,}</td>
                            <td>
                                <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                                <input type="checkbox" class="search-checkbox">
                                <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                                <input type="checkbox" class="search-checkbox">
                            </td>
                        </tr>''')

    line_box = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                📊 {line_name} - 型番別Top15
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr style="background: {BRAND_COLOR_PRIMARY};">
                            <th>順位</th>
                            <th>型番</th>
                            <th>販売数</th>
                            <th>中央値</th>
                            <th style="background: {BRAND_COLOR_ACCENT}; color: white;">仕入上限(¥)</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
{''.join(model_rows)}
                    </tbody>
                </table>
            </div>
        </div>
'''
    section5_lines.append(line_box)

section5_line_tops = '\n'.join(section5_lines)

# ============================================================
# セクション6: ライン詳細分析（★仕入上限・検索リンク含む）
# ============================================================

line_detail_rows = []

for line_name in line_counts.index[:8]:  # 上位8ライン
    line_data = brand_df[brand_df['ライン'] == line_name]
    count = len(line_data)
    ratio = (count / len(brand_df)) * 100
    median = line_data['価格'].median()
    mean = line_data['価格'].mean()
    std_val = line_data['価格'].std()
    cv = std_val / mean if mean > 0 else 0

    # 仕入上限計算
    purchase_limit_usd = median * 0.65
    purchase_limit_jpy = int(purchase_limit_usd * 155)

    # 安定性判定
    if cv < 0.3:
        stability = '安定'
        stability_color = '#4caf50'
    elif cv < 0.7:
        stability = '中程度'
        stability_color = '#ff9800'
    else:
        stability = '不安定'
        stability_color = '#f44336'

    # 検索リンク生成
    ebay_keyword = f"{BRAND_NAME}+{line_name.replace(' ', '+')}"
    mercari_keyword = f"{BRAND_NAME}%20{line_name.replace(' ', '%20')}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={ebay_keyword}+Watch&LH_Sold=1&LH_Complete=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={mercari_keyword}%20時計&status=on_sale"

    line_detail_rows.append(f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{count}</td>
                        <td>{ratio:.1f}%</td>
                        <td>${median:.2f}</td>
                        <td style="background: {BRAND_COLOR_ACCENT}; color: white; font-weight: bold;">¥{purchase_limit_jpy:,}</td>
                        <td>{cv:.3f}</td>
                        <td><span style="color: {stability_color}; font-weight: bold;">{stability}</span></td>
                        <td>
                            <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>''')

section6_line_detail = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                🔵 ライン詳細分析
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr style="background: {BRAND_COLOR_PRIMARY};">
                            <th>ライン名</th>
                            <th>販売数</th>
                            <th>比率</th>
                            <th>中央値</th>
                            <th style="background: {BRAND_COLOR_ACCENT}; color: white;">仕入上限(¥)</th>
                            <th>CV値</th>
                            <th>安定性</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
{''.join(line_detail_rows)}
                    </tbody>
                </table>
            </div>
        </div>
'''

# ============================================================
# セクション7: 全ライン横断Top30
# ============================================================

top30_df = brand_df[brand_df['型番'].notna()].copy()
top30_stats = top30_df.groupby('型番').agg({
    '価格': ['count', 'median']
}).round(2)
top30_stats.columns = ['販売数', '中央値']
top30_stats = top30_stats.sort_values('販売数', ascending=False).head(30)

top30_rows = []
for idx, (model, row) in enumerate(top30_stats.iterrows(), 1):
    sales = int(row['販売数'])
    median = row['中央値']

    # このモデルのライン名を取得
    model_line = top30_df[top30_df['型番'] == model]['ライン'].mode()
    line_name = model_line.iloc[0] if len(model_line) > 0 else 'その他Longines'

    purchase_limit_usd = median * 0.65
    purchase_limit_jpy = int(purchase_limit_usd * 155)

    ebay_keyword = f"{BRAND_NAME}+{model.replace(' ', '+')}"
    mercari_keyword = f"{BRAND_NAME}%20{model.replace(' ', '%20')}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={ebay_keyword}&LH_Sold=1&LH_Complete=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={mercari_keyword}&status=on_sale"

    top30_rows.append(f'''
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{model}</strong></td>
                        <td>{line_name}</td>
                        <td>{sales}</td>
                        <td>${median:.2f}</td>
                        <td style="background: {BRAND_COLOR_ACCENT}; color: white; font-weight: bold;">¥{purchase_limit_jpy:,}</td>
                        <td>
                            <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>''')

section7_top30 = f'''
        <div class="section-box">
            <div class="section-title" style="background: {BRAND_COLOR_PRIMARY};">
                🏆 全ライン横断 Top30人気モデル
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr style="background: {BRAND_COLOR_PRIMARY};">
                            <th>順位</th>
                            <th>型番</th>
                            <th>ライン</th>
                            <th>販売数</th>
                            <th>中央値</th>
                            <th style="background: {BRAND_COLOR_ACCENT}; color: white;">仕入上限(¥)</th>
                            <th>検索</th>
                        </tr>
                    </thead>
                    <tbody>
{''.join(top30_rows)}
                    </tbody>
                </table>
            </div>
        </div>
'''

# ============================================================
# セクション8: グラフスクリプト + CSS
# ============================================================

# グラフ用データ準備
# 1. 価格帯別
price_bins = [0, 200, 400, 600, 800, 1000, 1500, 10000]
price_labels = ['$0-200', '$200-400', '$400-600', '$600-800', '$800-1000', '$1000-1500', '$1500+']
brand_df['価格帯'] = pd.cut(brand_df['価格'], bins=price_bins, labels=price_labels)
price_dist = brand_df['価格帯'].value_counts().sort_index()

# 2. 駆動方式別
movement_dist = brand_df['駆動方式'].value_counts()

# 3. 性別・カテゴリー別
gender_dist = brand_df['カテゴリ'].value_counts()

# 4. ライン別
line_dist = brand_df['ライン'].value_counts().head(8)

section8_scripts = f'''
        <style>
            .{BRAND_NAME.lower()}-primary {{
                background: {BRAND_COLOR_PRIMARY};
                color: white;
            }}
            .{BRAND_NAME.lower()}-accent {{
                background: {BRAND_COLOR_ACCENT};
                color: white;
            }}
        </style>

        <script>
            // 1. 価格帯別分析
            {{
                const data = [{{
                    x: {list(price_dist.index.astype(str))},
                    y: {list(price_dist.values)},
                    type: 'bar',
                    marker: {{color: '{BRAND_COLOR_PRIMARY}'}}
                }}];
                const layout = {{
                    title: '価格帯別販売分布',
                    xaxis: {{title: '価格帯'}},
                    yaxis: {{title: '販売数'}},
                    height: 400
                }};
                Plotly.newPlot('longines_price_chart', data, layout);
            }}

            // 2. 駆動方式別
            {{
                const data = [{{
                    values: {list(movement_dist.values)},
                    labels: {list(movement_dist.index.astype(str))},
                    type: 'pie',
                    marker: {{colors: ['{BRAND_COLOR_PRIMARY}', '{BRAND_COLOR_ACCENT}', '#6c757d']}}
                }}];
                const layout = {{
                    title: '駆動方式別分布',
                    height: 400
                }};
                Plotly.newPlot('longines_movement_chart', data, layout);
            }}

            // 3. 性別・カテゴリー別
            {{
                const data = [{{
                    values: {list(gender_dist.values)},
                    labels: {list(gender_dist.index.astype(str))},
                    type: 'pie',
                    marker: {{colors: ['{BRAND_COLOR_PRIMARY}', '{BRAND_COLOR_ACCENT}', '#6c757d']}}
                }}];
                const layout = {{
                    title: '性別・カテゴリー別',
                    height: 400
                }};
                Plotly.newPlot('longines_gender_chart', data, layout);
            }}

            // 4. ライン別売上比率
            {{
                const data = [{{
                    values: {list(line_dist.values)},
                    labels: {list(line_dist.index.astype(str))},
                    type: 'pie',
                    marker: {{colors: ['{BRAND_COLOR_PRIMARY}', '{BRAND_COLOR_ACCENT}', '#17a2b8', '#ffc107', '#28a745', '#dc3545', '#6610f2', '#fd7e14']}}
                }}];
                const layout = {{
                    title: 'ライン別売上比率',
                    height: 400
                }};
                Plotly.newPlot('longines_line_chart', data, layout);
            }}
        </script>
'''

# ============================================================
# 全セクション結合
# ============================================================

full_tab_content = f'''
    <!-- {BRAND_NAME}タブ -->
    <div id="{BRAND_NAME}" class="tab-content">
{section1_basic_stats}
{section2_strategy}
{section3_graphs}
{section4_special}
{section5_line_tops}
{section6_line_detail}
{section7_top30}
{section8_scripts}
    </div>
'''

print(f"✅ HTML生成完了（{len(full_tab_content)}文字）")

# ============================================================
# index.htmlに挿入
# ============================================================

print("\n" + "=" * 60)
print("index.htmlへの挿入")
print("=" * 60)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"✅ index.html読み込み完了（{len(html)}文字）")

# Hamiltonタブの終了位置を探す（ネストカウント方式）
hamilton_start = html.find('<div id="Hamilton" class="tab-content">')
if hamilton_start == -1:
    print("❌ エラー: Hamiltonタブが見つかりません")
    exit(1)

print(f"✅ Hamiltonタブ開始位置: {hamilton_start}")

# Hamiltonタブの終了</div>を探す
div_count = 1
search_pos = hamilton_start + len('<div id="Hamilton" class="tab-content">')

while div_count > 0 and search_pos < len(html):
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

print(f"✅ Hamiltonタブ終了位置: {hamilton_end}")

# 挿入位置の前後を確認
print("\n挿入位置の前後50文字:")
print(f"前: ...{html[hamilton_end-50:hamilton_end]}")
print(f"後: {html[hamilton_end:hamilton_end+50]}...")

# Longinesタブを挿入
html = html[:hamilton_end] + '\n' + full_tab_content + html[hamilton_end:]

print(f"\n✅ Longinesタブ挿入完了")
print(f"   挿入前: {len(html) - len(full_tab_content)}文字")
print(f"   挿入後: {len(html)}文字")
print(f"   増加量: {len(full_tab_content)}文字")

# ナビゲーションボタンの確認
if '<button class="tab-button" onclick="showTab(\'Longines\')">Longines</button>' in html:
    print("✅ ナビゲーションボタン確認: 既に存在")
else:
    print("⚠️  ナビゲーションボタンが見つかりません（手動で追加してください）")

# ファイル保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n" + "=" * 60)
print("✅ index.html保存完了")
print("=" * 60)

print("\n📊 最終確認:")
print(f"   - タブコンテンツdiv: {'✅' if '<div id=\"Longines\" class=\"tab-content\">' in html else '❌'}")
print(f"   - 基本統計セクション: {'✅' if '📊 基本統計' in html else '❌'}")
print(f"   - 仕入戦略セクション: {'✅' if '💡 仕入戦略' in html else '❌'}")
print(f"   - グラフセクション: {'✅' if 'longines_price_chart' in html else '❌'}")
print(f"   - 特別版セクション: {'✅' if '🏆 特別版・限定モデル 分析' in html else '❌'}")
print(f"   - ライン別Top15: {'✅' if f'{line_counts.index[0]} - 型番別Top15' in html else '❌'}")
print(f"   - ライン詳細分析: {'✅' if '🔵 ライン詳細分析' in html else '❌'}")
print(f"   - Top30セクション: {'✅' if '🏆 全ライン横断 Top30人気モデル' in html else '❌'}")

# Plotlyグラフの数を確認
plotly_count = html.count('Plotly.newPlot(\'longines_')
print(f"   - Plotlyグラフ数: {plotly_count}個")

# 仕入上限の数を確認
purchase_limit_count = html.count('仕入上限(¥)')
print(f"   - 仕入上限(¥)表示: {purchase_limit_count}箇所")

# eBay/メルカリリンクの数を確認
ebay_link_count = html.count('link-ebay">eBay</a>')
mercari_link_count = html.count('link-mercari">メルカリ</a>')
print(f"   - eBayリンク: {ebay_link_count}個")
print(f"   - メルカリリンク: {mercari_link_count}個")

print("\n🎉 Longinesタブ実装完了！")
