#!/usr/bin/env python3
"""
駆動方式タブ生成スクリプト
自動巻、クオーツ、ソーラー、手巻き、スマートウォッチ、デジタルの詳細分析タブを生成
"""

import pandas as pd
import numpy as np
import json
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

# 駆動方式定義
MOVEMENTS = {
    'automatic': {
        'ja': '自動巻',
        'en': 'Automatic',
        'icon': '⚙️',
        'color': '#E65100',
        'tab_id': 'automatic'
    },
    'quartz': {
        'ja': 'クオーツ',
        'en': 'Quartz',
        'icon': '🔋',
        'color': '#1976D2',
        'tab_id': 'quartz'
    },
    'solar': {
        'ja': 'ソーラー',
        'en': 'Solar',
        'icon': '☀️',
        'color': '#FFC107',
        'tab_id': 'solar'
    },
    'manual': {
        'ja': '手巻き',
        'en': 'Manual',
        'icon': '🔧',
        'color': '#795548',
        'tab_id': 'manual'
    },
    'smartwatch': {
        'ja': 'スマートウォッチ',
        'en': 'Smartwatch',
        'icon': '📱',
        'color': '#9C27B0',
        'tab_id': 'smart'
    },
    'digital': {
        'ja': 'デジタル',
        'en': 'Digital',
        'icon': '🔢',
        'color': '#607D8B',
        'tab_id': 'digital'
    }
}

# CSVデータ読み込み
print("=== CSVデータ読み込み ===")
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()
print(f"完品データ: {len(df_complete)}件\n")


def calculate_stats(df_mov):
    """統計情報を計算"""
    if len(df_mov) == 0:
        return None

    stats = {
        'total_sales': len(df_mov),
        'avg_price': df_mov['価格'].mean(),
        'median_price': df_mov['価格'].median(),
        'min_price': df_mov['価格'].min(),
        'max_price': df_mov['価格'].max(),
        'total_revenue': df_mov['価格'].sum(),
        'cv': df_mov['価格'].std() / df_mov['価格'].mean() if df_mov['価格'].mean() > 0 else 0,
        'unique_models': df_mov['タイトル'].nunique(),
        'breakeven_median': df_mov['価格'].median() * EXCHANGE_RATE * (1 - FEE_RATE) - SHIPPING
    }

    return stats


def get_brand_data(df_mov):
    """ブランド別集計"""
    brand_data = []

    for brand in df_mov['ブランド'].value_counts().index[:20]:  # Top20
        df_brand = df_mov[df_mov['ブランド'] == brand]

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


def generate_movement_tab_html(movement_key, df_complete):
    """駆動方式タブのHTMLを生成"""

    movement = MOVEMENTS[movement_key]
    df_mov = df_complete[df_complete['駆動方式'] == movement['ja']].copy()

    if len(df_mov) == 0:
        print(f"⚠️ {movement['ja']}: データなし")
        return ""

    print(f"✓ {movement['ja']}: {len(df_mov)}件")

    # 統計情報
    stats = calculate_stats(df_mov)

    # ブランド別データ
    brand_data = get_brand_data(df_mov)

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
            count = len(df_mov[(df_mov['価格'] >= price_bins[i]) & (df_mov['価格'] < price_bins[i+1])])
            price_dist[label] = count
        else:
            count = len(df_mov[df_mov['価格'] >= 1000])
            price_dist[label] = count

    # デパートメント分布
    dept_dist = df_mov['デパートメント'].value_counts().to_dict()

    # 月別推移（デパートメント別）
    df_mov['年月'] = pd.to_datetime(df_mov['販売日']).dt.to_period('M')
    monthly_data = {}
    for dept in df_mov['デパートメント'].unique():
        monthly_counts = df_mov[df_mov['デパートメント'] == dept].groupby('年月').size()
        monthly_data[dept] = monthly_counts.to_dict()

    # HTML生成
    html = f'''
    <div id="{movement['tab_id']}" class="tab-content">
        <h2 class="section-title">{movement['icon']} {movement['ja']}ウォッチ市場分析</h2>

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
            <div class="chart-container"><div id="{movement['tab_id']}_brand_bar"></div></div>
            <div class="chart-container"><div id="{movement['tab_id']}_brand_pie"></div></div>
            <div class="chart-container"><div id="{movement['tab_id']}_price_dist"></div></div>
            <div class="chart-container"><div id="{movement['tab_id']}_dept_pie"></div></div>
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
        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(b['brand'])}+Watch+{quote(movement['en'])}&LH_Sold=1&LH_Complete=1"
        mercari_url = f"https://jp.mercari.com/search?keyword={quote(b['jp_brand'])}+時計+{quote(movement['ja'])}&status=on_sale"

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
                            <input type="checkbox" class="search-checkbox" data-id="{movement['tab_id']}_brand_{b['brand']}_ebay">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox" data-id="{movement['tab_id']}_brand_{b['brand']}_mercari">
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

    dept_labels = list(dept_dist.keys())
    dept_values = list(dept_dist.values())

    html += f'''
    // ブランド別販売数（横棒グラフ）
    Plotly.newPlot('{movement['tab_id']}_brand_bar', [{{
        x: {brand_values},
        y: {json.dumps(brand_labels)},
        type: 'bar',
        orientation: 'h',
        marker: {{color: '{movement['color']}'}}
    }}], {{...plotlyLayout, title: 'ブランド別販売数（Top10）', xaxis: {{title: '販売数'}}, yaxis: {{title: 'ブランド'}}}}, plotlyConfig);

    // ブランド別シェア（円グラフ）
    Plotly.newPlot('{movement['tab_id']}_brand_pie', [{{
        labels: {json.dumps(brand_labels)},
        values: {brand_values},
        type: 'pie'
    }}], {{...plotlyLayout, title: 'ブランド別シェア（Top10）'}}, plotlyConfig);

    // 価格帯分布
    Plotly.newPlot('{movement['tab_id']}_price_dist', [{{
        x: {json.dumps(price_labels_list)},
        y: {price_values_list},
        type: 'bar',
        marker: {{color: '{movement['color']}'}}
    }}], {{...plotlyLayout, title: '価格帯分布（50ドル刻み）', xaxis: {{title: '価格帯'}}, yaxis: {{title: '件数'}}}}, plotlyConfig);

    // デパートメント分布
    Plotly.newPlot('{movement['tab_id']}_dept_pie', [{{
        labels: {json.dumps(dept_labels)},
        values: {dept_values},
        type: 'pie'
    }}], {{...plotlyLayout, title: 'デパートメント分布'}}, plotlyConfig);
    </script>
'''

    return html


# メイン処理
print("=== 駆動方式タブHTML生成 ===\n")

# HTMLファイル読み込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 全駆動方式タブを置換
for movement_key in ['automatic', 'quartz', 'solar', 'manual', 'smartwatch', 'digital']:
    movement = MOVEMENTS[movement_key]

    # 既存タブの開始位置を探す
    tab_start = html.find(f'<div id="{movement["tab_id"]}" class="tab-content">')

    if tab_start == -1:
        print(f"❌ {movement['ja']}タブが見つかりません")
        continue

    # タブの終了位置を探す（ネストカウント）
    div_count = 1
    search_pos = tab_start + len(f'<div id="{movement["tab_id"]}" class="tab-content">')

    while div_count > 0 and search_pos < len(html):
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            print(f"❌ {movement['ja']}タブの終了位置が見つかりません")
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                tab_end = next_close + 6
                break
            else:
                search_pos = next_close + 6

    # 新しいタブHTMLを生成
    new_tab_html = generate_movement_tab_html(movement_key, df_complete)

    # 置換
    html = html[:tab_start] + new_tab_html + html[tab_end:]
    print(f"✅ {movement['ja']}タブを置換しました\n")

# HTMLファイルを保存
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("=== 完了 ===")
print(f"ファイルサイズ: {len(html)}文字")
