#!/usr/bin/env python3
"""
パーツ（属性）別タブ生成スクリプト
ベルト素材、ケース素材、文字盤色、ケースサイズの詳細分析タブを生成
"""

import pandas as pd
import numpy as np
import json
import re
from urllib.parse import quote

# 設定
EXCHANGE_RATE = 155
FEE_RATE = 0.20
SHIPPING = 3000

# ブランド日本語マッピング
BRAND_JP_MAP = {
    'SEIKO': 'セイコー',
    'CASIO': 'カシオ',
    'CITIZEN': 'シチズン',
    'OMEGA': 'オメガ',
    'ROLEX': 'ロレックス',
    'TAG HEUER': 'タグホイヤー',
    'BREITLING': 'ブライトリング',
    'Orient': 'オリエント',
    'Longines': 'ロンジン',
    'Hamilton': 'ハミルトン',
    'GUCCI': 'グッチ',
    'Cartier': 'カルティエ',
    'RADO': 'ラドー',
    'Tissot': 'ティソ',
    'Oris': 'オリス',
    '(不明)': '不明'
}

# パーツタブ定義
PARTS_TABS = {
    'belt-material': {
        'ja': 'ベルト素材',
        'icon': '🔗',
        'color': '#795548',
        'tab_id': 'belt-material',
        'attribute': 'ベルト素材'
    },
    'case-material': {
        'ja': 'ケース素材',
        'icon': '📦',
        'color': '#607D8B',
        'tab_id': 'case-material',
        'attribute': 'ケース素材'
    },
    'dial-color': {
        'ja': '文字盤色',
        'icon': '🎨',
        'color': '#9C27B0',
        'tab_id': 'dial-color',
        'attribute': '文字盤色'
    },
    'case-size': {
        'ja': 'ケースサイズ',
        'icon': '📏',
        'color': '#00BCD4',
        'tab_id': 'case-size',
        'attribute': 'ケースサイズ'
    }
}

# 属性抽出関数
def extract_belt_material(title):
    """ベルト素材を抽出"""
    title_upper = str(title).upper()

    if any(kw in title_upper for kw in ['STEEL BAND', 'STEEL BRACELET', 'SS BAND', 'SS BRACELET',
                                         'METAL BAND', 'METAL BRACELET', 'STAINLESS BAND',
                                         'STAINLESS BRACELET', 'OYSTER', 'JUBILEE']):
        return 'スチールベルト'
    elif 'STAINLESS STEEL' in title_upper and any(kw in title_upper for kw in ['BAND', 'BRACELET', 'STRAP']):
        return 'スチールベルト'
    elif any(kw in title_upper for kw in ['LEATHER', 'CROCODILE', 'ALLIGATOR', 'CALF',
                                           'LIZARD', 'OSTRICH', 'SUEDE']):
        return '革ベルト'
    elif any(kw in title_upper for kw in ['RUBBER', 'SILICONE', 'URETHANE', 'POLYURETHANE']):
        return 'ラバーベルト'
    elif any(kw in title_upper for kw in ['NYLON', 'NATO', 'CANVAS', 'FABRIC', 'TEXTILE']):
        return 'ナイロンベルト'
    else:
        return '不明'

def extract_case_material(title):
    """ケース素材を抽出"""
    title_upper = str(title).upper()

    if 'TITANIUM' in title_upper or 'TITAN' in title_upper:
        return 'チタン'
    elif any(kw in title_upper for kw in ['18K', '14K', '10K', 'GOLD PLATED', 'GOLD FILLED',
                                           'ROSE GOLD', 'YELLOW GOLD', 'WHITE GOLD', 'GOLD TONE']):
        return 'ゴールド'
    elif 'STAINLESS STEEL' in title_upper or 'SS CASE' in title_upper or 'STAINLESS CASE' in title_upper:
        return 'ステンレス'
    elif any(kw in title_upper for kw in ['PLASTIC', 'RESIN', 'ACRYLIC']):
        return '樹脂'
    else:
        return '不明'

def extract_dial_color(title):
    """文字盤色を抽出"""
    title_upper = str(title).upper()

    # DIALの前後を探す
    dial_idx = title_upper.find('DIAL')
    if dial_idx > 0:
        search_area = title_upper[max(0, dial_idx-20):dial_idx+20]
    else:
        search_area = title_upper

    if 'BLACK' in search_area:
        return '黒'
    elif 'WHITE' in search_area or 'IVORY' in search_area or 'CREAM' in search_area:
        return '白'
    elif 'BLUE' in search_area:
        return '青'
    elif 'SILVER' in search_area or 'GREY' in search_area or 'GRAY' in search_area:
        return 'シルバー'
    elif 'GREEN' in search_area:
        return '緑'
    elif 'GOLD' in search_area or 'CHAMPAGNE' in search_area:
        return 'ゴールド'
    elif 'BROWN' in search_area or 'BRONZE' in search_area:
        return '茶'
    elif 'RED' in search_area or 'BURGUNDY' in search_area:
        return '赤'
    else:
        return '不明'

def extract_case_size(title):
    """ケースサイズを抽出"""
    title_upper = str(title).upper()

    match = re.search(r'(\d+)\s*MM', title_upper)
    if match:
        size = int(match.group(1))
        if size < 36:
            return '小型(<36mm)'
        elif size < 42:
            return '中型(36-41mm)'
        else:
            return '大型(42mm+)'
    else:
        return '不明'

# CSVデータ読み込み
print("=== CSVデータ読み込み ===")
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()
print(f"完品データ: {len(df_complete)}件\n")

# 属性を抽出
print("=== 属性抽出中 ===")
df_complete['ベルト素材'] = df_complete['タイトル'].apply(extract_belt_material)
df_complete['ケース素材'] = df_complete['タイトル'].apply(extract_case_material)
df_complete['文字盤色'] = df_complete['タイトル'].apply(extract_dial_color)
df_complete['ケースサイズ'] = df_complete['タイトル'].apply(extract_case_size)

# 属性分布を表示
for attr in ['ベルト素材', 'ケース素材', '文字盤色', 'ケースサイズ']:
    print(f"\n{attr}分布:")
    print(df_complete[attr].value_counts())
    unknown_rate = (df_complete[attr] == '不明').sum() / len(df_complete) * 100
    known_count = (df_complete[attr] != '不明').sum()
    print(f"不明率: {unknown_rate:.1f}% | 判別可能: {known_count}件")

print("\n")


def calculate_stats(df_part):
    """統計情報を計算"""
    if len(df_part) == 0:
        return None

    stats = {
        'total_sales': len(df_part),
        'avg_price': df_part['価格'].mean(),
        'median_price': df_part['価格'].median(),
        'min_price': df_part['価格'].min(),
        'max_price': df_part['価格'].max(),
        'total_revenue': df_part['価格'].sum(),
        'cv': df_part['価格'].std() / df_part['価格'].mean() if df_part['価格'].mean() > 0 else 0,
        'unique_models': df_part['タイトル'].nunique(),
        'breakeven_median': df_part['価格'].median() * EXCHANGE_RATE * (1 - FEE_RATE) - SHIPPING
    }

    return stats


def get_brand_data(df_part):
    """ブランド別集計"""
    brand_data = []

    for brand in df_part['ブランド'].value_counts().index[:20]:  # Top20
        df_brand = df_part[df_part['ブランド'] == brand]

        median = df_brand['価格'].median()
        cv = df_brand['価格'].std() / df_brand['価格'].mean() if df_brand['価格'].mean() > 0 else 0
        breakeven = median * EXCHANGE_RATE * (1 - FEE_RATE) - SHIPPING

        brand_data.append({
            'brand': brand,
            'jp_brand': BRAND_JP_MAP.get(brand, brand),
            'count': len(df_brand),
            'min': df_brand['価格'].min(),
            'max': df_brand['価格'].max(),
            'median': median,
            'median_jpy': median * EXCHANGE_RATE,
            'breakeven': breakeven,
            'cv': cv
        })

    return brand_data


def generate_parts_tab_html(parts_key, df_complete):
    """パーツタブのHTMLを生成"""

    parts = PARTS_TABS[parts_key]
    attribute_name = parts['attribute']

    # 「不明」を除外してデータ抽出
    df_part = df_complete[df_complete[attribute_name] != '不明'].copy()

    if len(df_part) == 0:
        print(f"⚠️ {parts['ja']}: データなし")
        return ""

    print(f"✓ {parts['ja']}: {len(df_part)}件（不明除外後）")

    # 統計情報
    stats = calculate_stats(df_part)

    # ブランド別データ
    brand_data = get_brand_data(df_part)

    # ブランド別販売数（Top10）
    brand_top10 = [(b['jp_brand'], b['count']) for b in brand_data[:10]]

    # 価格帯分布（50ドル刻み）
    price_bins = list(range(0, 1001, 50))
    price_bins.append(10000)  # 1000+
    price_labels = [f'${i}-{i+49}' for i in range(0, 1000, 50)]
    price_labels.append('$1000+')

    price_dist = {}
    for i, label in enumerate(price_labels):
        if i < len(price_bins) - 1:
            count = len(df_part[(df_part['価格'] >= price_bins[i]) & (df_part['価格'] < price_bins[i+1])])
            price_dist[label] = count
        else:
            count = len(df_part[df_part['価格'] >= 1000])
            price_dist[label] = count

    # デパートメント分布
    dept_dist = df_part['デパートメント'].value_counts().to_dict()

    # 属性値別分布（Top10）
    attr_dist = df_part[attribute_name].value_counts().head(10).to_dict()

    # HTML生成
    html = f'''
    <div id="{parts['tab_id']}" class="tab-content">
        <h2 class="section-title">{parts['icon']} {parts['ja']}別市場分析</h2>

        <div class="info-box" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px;">
            <strong>📊 データ判別率</strong><br>
            タイトルから判別可能なデータ: <strong>{len(df_part):,}件</strong> / 全体 {len(df_complete):,}件<br>
            判別率: <strong>{len(df_part)/len(df_complete)*100:.1f}%</strong><br>
            <em>※「不明」は除外して分析しています</em>
        </div>

        <!-- 統計カード -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{stats['total_sales']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">ユニークモデル数</div>
                <div class="value">{stats['unique_models']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">平均価格</div>
                <div class="value">${stats['avg_price']:,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${stats['median_price']:,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">最高価格</div>
                <div class="value">${stats['max_price']:,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">総売上</div>
                <div class="value">${stats['total_revenue']:,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV値（価格安定性）</div>
                <div class="value">{stats['cv']:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">仕入れ上限中央値</div>
                <div class="value">¥{stats['breakeven_median']:,.0f}</div>
            </div>
        </div>

        <!-- グラフエリア -->
        <h3 class="section-title">📊 市場分析グラフ</h3>
        <div class="chart-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="chart-container"><div id="{parts['tab_id']}_brand_bar"></div></div>
            <div class="chart-container"><div id="{parts['tab_id']}_brand_pie"></div></div>
            <div class="chart-container"><div id="{parts['tab_id']}_price_dist"></div></div>
            <div class="chart-container"><div id="{parts['tab_id']}_attr_pie"></div></div>
        </div>

        <!-- ブランド別集計テーブル -->
        <h3 class="section-title">🏷️ ブランド別集計（Top20）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ブランド</th>
                        <th>販売数</th>
                        <th>最低価格</th>
                        <th>最高価格</th>
                        <th>中央値($)</th>
                        <th>中央値(¥)</th>
                        <th>仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

    # ブランド別テーブル行
    for b in brand_data:
        # 検索キーワードの生成
        attr_keyword_en = parts['ja']  # 英語化が必要な場合は別途マッピング
        attr_keyword_ja = parts['ja']

        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(b['brand'])}+Watch&LH_Sold=1&LH_Complete=1"
        mercari_url = f"https://jp.mercari.com/search?keyword={quote(b['jp_brand'])}+時計&status=on_sale"

        html += f'''
                    <tr>
                        <td><strong>{b['jp_brand']}</strong> ({b['brand']})</td>
                        <td>{b['count']}</td>
                        <td>${b['min']:.2f}</td>
                        <td>${b['max']:.2f}</td>
                        <td>${b['median']:.2f}</td>
                        <td>¥{b['median_jpy']:,.0f}</td>
                        <td class="highlight">¥{b['breakeven']:,.0f}</td>
                        <td>{b['cv']:.3f}</td>
                        <td>
                            <a href="{ebay_url}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox" data-id="{parts['tab_id']}_brand_{b['brand']}_ebay">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox" data-id="{parts['tab_id']}_brand_{b['brand']}_mercari">
                        </td>
                    </tr>
'''

    html += '''
                </tbody>
            </table>
        </div>
    </div>

    <script>
'''

    # グラフ用JavaScript
    brand_labels = [b[0] for b in brand_top10]
    brand_values = [b[1] for b in brand_top10]

    price_labels_list = list(price_dist.keys())
    price_values_list = list(price_dist.values())

    attr_labels = list(attr_dist.keys())
    attr_values = list(attr_dist.values())

    html += f'''
    // ブランド別販売数（横棒グラフ）
    Plotly.newPlot('{parts['tab_id']}_brand_bar', [{{
        x: {brand_values},
        y: {json.dumps(brand_labels)},
        type: 'bar',
        orientation: 'h',
        marker: {{color: '{parts['color']}'}}
    }}], {{...plotlyLayout, title: 'ブランド別販売数（Top10）', xaxis: {{title: '販売数'}}, yaxis: {{title: 'ブランド'}}}}, plotlyConfig);

    // ブランド別シェア（円グラフ）
    Plotly.newPlot('{parts['tab_id']}_brand_pie', [{{
        labels: {json.dumps(brand_labels)},
        values: {brand_values},
        type: 'pie'
    }}], {{...plotlyLayout, title: 'ブランド別シェア（Top10）'}}, plotlyConfig);

    // 価格帯分布
    Plotly.newPlot('{parts['tab_id']}_price_dist', [{{
        x: {json.dumps(price_labels_list)},
        y: {price_values_list},
        type: 'bar',
        marker: {{color: '{parts['color']}'}}
    }}], {{...plotlyLayout, title: '価格帯分布（50ドル刻み）', xaxis: {{title: '価格帯'}}, yaxis: {{title: '件数'}}}}, plotlyConfig);

    // {parts['ja']}別分布
    Plotly.newPlot('{parts['tab_id']}_attr_pie', [{{
        labels: {json.dumps(attr_labels)},
        values: {attr_values},
        type: 'pie'
    }}], {{...plotlyLayout, title: '{parts['ja']}別分布（Top10）'}}, plotlyConfig);
    </script>
'''

    return html


# メイン処理
print("=== パーツタブHTML生成 ===\n")

# HTMLファイル読み込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# デジタルタブの終了位置を探す（パーツタブはその後に追加）
digital_tab_start = html.find('<div id="digital" class="tab-content">')
if digital_tab_start == -1:
    print("❌ デジタルタブが見つかりません")
    exit(1)

# デジタルタブの終了位置を探す（ネストカウント）
div_count = 1
search_pos = digital_tab_start + len('<div id="digital" class="tab-content">')

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ デジタルタブの終了位置が見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            digital_tab_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

print(f"デジタルタブ終了位置: {digital_tab_end}")

# パーツタブを生成して挿入
all_parts_html = ""
for parts_key in ['belt-material', 'case-material', 'dial-color', 'case-size']:
    parts_html = generate_parts_tab_html(parts_key, df_complete)
    all_parts_html += parts_html

# 挿入
html = html[:digital_tab_end] + all_parts_html + html[digital_tab_end:]
print(f"\n✅ 全パーツタブを挿入しました\n")

# タブボタンも追加（駆動方式タブの後）
tab_buttons_insert = html.find('<button class="tab-btn" data-tab="automatic">')
if tab_buttons_insert == -1:
    print("❌ タブボタン挿入位置が見つかりません")
else:
    # デジタルタブボタンの後を探す
    digital_btn_pos = html.find('<button class="tab-btn" data-tab="digital">')
    if digital_btn_pos == -1:
        print("❌ デジタルタブボタンが見つかりません")
    else:
        # </button>の終了位置を探す
        digital_btn_end = html.find('</button>', digital_btn_pos) + 9

        # パーツタブボタンを生成
        parts_buttons = ""
        for parts_key in ['belt-material', 'case-material', 'dial-color', 'case-size']:
            parts = PARTS_TABS[parts_key]
            parts_buttons += f'\n                <button class="tab-btn" data-tab="{parts['tab_id']}">{parts['icon']} {parts['ja']}</button>'

        # 挿入
        html = html[:digital_btn_end] + parts_buttons + html[digital_btn_end:]
        print(f"✅ パーツタブボタンを追加しました\n")

# HTMLファイルを保存
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("=== 完了 ===")
print(f"ファイルサイズ: {len(html):,}文字")
