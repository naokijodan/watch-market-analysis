#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時計市場分析HTML生成スクリプト v3.5（深掘り版）
- SEIKO/CASIO/CITIZENライン別タブ
- G-SHOCK専用タブ
- 駆動方式別詳細グラフ
"""

import json
import os

# JSONを読み込み
with open('/Users/naokijodan/Desktop/時計分析_完全版.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

with open('/Users/naokijodan/Desktop/時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive_data = json.load(f)

# 基本HTMLヘッダー
html_header = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>時計市場分析 v3.5 - 深掘り版</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            text-align: center;
            color: white;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .tabs {
            display: flex;
            flex-wrap: wrap;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            overflow-x: auto;
        }
        .tab {
            padding: 15px 25px;
            cursor: pointer;
            background: transparent;
            border: none;
            font-size: 1em;
            transition: all 0.3s;
            white-space: nowrap;
        }
        .tab:hover {
            background: rgba(102, 126, 234, 0.1);
        }
        .tab.active {
            background: white;
            border-bottom: 3px solid #667eea;
            font-weight: bold;
            color: #667eea;
        }
        .content {
            padding: 40px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .stat-card p {
            font-size: 2em;
            font-weight: bold;
        }
        .chart {
            margin: 30px 0;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .section-title {
            font-size: 1.8em;
            margin: 30px 0 20px 0;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
        }
        .badge-high {
            background: #ff6b6b;
            color: white;
        }
        .badge-medium {
            background: #ffd93d;
            color: #333;
        }
        .badge-low {
            background: #6bcf7f;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 時計市場分析レポート v3.5</h1>
            <p>深掘り版 - SEIKO/CASIO/CITIZENライン別詳細分析</p>
            <p style="font-size: 0.9em; margin-top: 10px;">生成日時: ''' + deepdive_data['generated_at'] + '''</p>
        </div>

        <div class="tabs" id="tabs">
            <button class="tab active" onclick="showTab('overview')">概要</button>
            <button class="tab" onclick="showTab('seiko_lines')">SEIKO詳細</button>
            <button class="tab" onclick="showTab('casio_lines')">CASIO詳細</button>
            <button class="tab" onclick="showTab('citizen_lines')">CITIZEN詳細</button>
            <button class="tab" onclick="showTab('gshock')">G-SHOCK特集</button>
            <button class="tab" onclick="showTab('movement_auto')">自動巻</button>
            <button class="tab" onclick="showTab('movement_quartz')">クォーツ</button>
            <button class="tab" onclick="showTab('movement_solar')">ソーラー</button>
            <button class="tab" onclick="showTab('parts')">パーツ</button>
            <button class="tab" onclick="showTab('bundles')">まとめ売り</button>
            <button class="tab" onclick="showTab('recommendations')">おすすめ</button>
        </div>

        <div class="content" id="content">
'''

# 概要タブ生成
def generate_overview_tab():
    overall = full_data['overall']
    html = f'''
        <div class="tab-content active" id="overview">
            <h2 class="section-title">📊 全体統計</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>総商品数</h3>
                    <p>{overall['total_items']:,}</p>
                </div>
                <div class="stat-card">
                    <h3>総販売数</h3>
                    <p>{overall['total_sales']:,}</p>
                </div>
                <div class="stat-card">
                    <h3>平均価格</h3>
                    <p>${overall['avg_price']:.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>中央値価格</h3>
                    <p>${overall['median_price']:.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>総売上高</h3>
                    <p>${overall['total_revenue']:,.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>データ期間</h3>
                    <p style="font-size: 0.9em;">{overall['data_period']}</p>
                </div>
            </div>

            <h2 class="section-title">🏆 ブランド別販売数Top20</h2>
            <div class="chart" id="brand_chart"></div>

            <h2 class="section-title">⚙️ 駆動方式別分布</h2>
            <div class="chart" id="movement_chart"></div>

            <h2 class="section-title">📈 月別販売推移</h2>
            <div class="chart" id="monthly_chart"></div>
        </div>
    '''
    return html

# SEIKOライン別タブ生成
def generate_seiko_lines_tab():
    seiko_lines = deepdive_data['seiko_lines']

    # テーブルHTML生成
    table_html = '<table><tr><th>ライン</th><th>販売数</th><th>中央値</th><th>CV値</th><th>安定度</th><th>JDM比率</th><th>JDMプレミアム</th></tr>'

    for line, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        cv_badge = 'badge-low' if data['cv'] <= 0.3 else ('badge-medium' if data['cv'] <= 0.5 else 'badge-high')
        stability = '★★★' if data['cv'] <= 0.15 else ('★★☆' if data['cv'] <= 0.25 else ('★☆☆' if data['cv'] <= 0.30 else '☆☆☆'))
        jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'

        table_html += f'''<tr>
            <td><strong>{line}</strong></td>
            <td>{data['count']:,}</td>
            <td>${data['median']:.0f}</td>
            <td><span class="badge {cv_badge}">{data['cv']:.3f}</span></td>
            <td>{stability}</td>
            <td>{jdm_ratio}</td>
            <td>{data['jdm_premium']:+.1f}%</td>
        </tr>'''

    table_html += '</table>'

    # 上位モデル表示
    models_html = '<h3 style="margin-top: 30px;">📌 各ラインの人気モデルTop5</h3>'
    for line, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        if data['top_models']:
            models_html += f'<h4 style="margin-top: 20px; color: #667eea;">{line}</h4><table><tr><th>型番</th><th>販売数</th><th>中央値</th><th>CV値</th></tr>'
            for model in data['top_models']:
                models_html += f"<tr><td>{model['model']}</td><td>{model['count']}</td><td>${model['median']:.0f}</td><td>{model['cv']:.3f}</td></tr>"
            models_html += '</table>'

    html = f'''
        <div class="tab-content" id="seiko_lines">
            <h2 class="section-title">🔵 SEIKO ライン別詳細分析</h2>
            {table_html}
            <div class="chart" id="seiko_lines_chart"></div>
            {models_html}
        </div>
    '''
    return html

# CASIOライン別タブ生成
def generate_casio_lines_tab():
    casio_lines = deepdive_data['casio_lines']

    table_html = '<table><tr><th>ライン</th><th>販売数</th><th>中央値</th><th>CV値</th><th>安定度</th><th>JDM比率</th><th>コラボ数</th><th>限定数</th></tr>'

    for line, data in sorted(casio_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        cv_badge = 'badge-low' if data['cv'] <= 0.3 else ('badge-medium' if data['cv'] <= 0.5 else 'badge-high')
        stability = '★★★' if data['cv'] <= 0.15 else ('★★☆' if data['cv'] <= 0.25 else ('★☆☆' if data['cv'] <= 0.30 else '☆☆☆'))
        jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'

        table_html += f'''<tr>
            <td><strong>{line}</strong></td>
            <td>{data['count']:,}</td>
            <td>${data['median']:.0f}</td>
            <td><span class="badge {cv_badge}">{data['cv']:.3f}</span></td>
            <td>{stability}</td>
            <td>{jdm_ratio}</td>
            <td>{data.get('collab_count', 0)}</td>
            <td>{data.get('limited_count', 0)}</td>
        </tr>'''

    table_html += '</table>'

    # 上位モデル表示
    models_html = '<h3 style="margin-top: 30px;">📌 各ラインの人気モデル</h3>'
    for line, data in sorted(casio_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        if data['top_models']:
            top_n = len(data['top_models'])
            models_html += f'<h4 style="margin-top: 20px; color: #667eea;">{line} (Top{top_n})</h4><table><tr><th>型番</th><th>販売数</th><th>中央値</th><th>CV値</th></tr>'
            for model in data['top_models']:
                models_html += f"<tr><td>{model['model']}</td><td>{model['count']}</td><td>${model['median']:.0f}</td><td>{model['cv']:.3f}</td></tr>"
            models_html += '</table>'

    html = f'''
        <div class="tab-content" id="casio_lines">
            <h2 class="section-title">🟢 CASIO ライン別詳細分析</h2>
            {table_html}
            <div class="chart" id="casio_lines_chart"></div>
            {models_html}
        </div>
    '''
    return html

# CITIZENライン別タブ生成
def generate_citizen_lines_tab():
    citizen_lines = deepdive_data['citizen_lines']

    table_html = '<table><tr><th>ライン</th><th>販売数</th><th>中央値</th><th>CV値</th><th>安定度</th><th>Eco-Drive比率</th><th>Eco-Driveプレミアム</th></tr>'

    for line, data in sorted(citizen_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        cv_badge = 'badge-low' if data['cv'] <= 0.3 else ('badge-medium' if data['cv'] <= 0.5 else 'badge-high')
        stability = '★★★' if data['cv'] <= 0.15 else ('★★☆' if data['cv'] <= 0.25 else ('★☆☆' if data['cv'] <= 0.30 else '☆☆☆'))
        eco_ratio = f"{data['eco_drive_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'

        table_html += f'''<tr>
            <td><strong>{line}</strong></td>
            <td>{data['count']:,}</td>
            <td>${data['median']:.0f}</td>
            <td><span class="badge {cv_badge}">{data['cv']:.3f}</span></td>
            <td>{stability}</td>
            <td>{eco_ratio}</td>
            <td>{data['eco_drive_premium']:+.1f}%</td>
        </tr>'''

    table_html += '</table>'

    # 上位モデル表示
    models_html = '<h3 style="margin-top: 30px;">📌 各ラインの人気モデルTop5</h3>'
    for line, data in sorted(citizen_lines.items(), key=lambda x: x[1]['count'], reverse=True):
        if data['top_models']:
            models_html += f'<h4 style="margin-top: 20px; color: #667eea;">{line}</h4><table><tr><th>型番</th><th>販売数</th><th>中央値</th><th>CV値</th></tr>'
            for model in data['top_models']:
                models_html += f"<tr><td>{model['model']}</td><td>{model['count']}</td><td>${model['median']:.0f}</td><td>{model['cv']:.3f}</td></tr>"
            models_html += '</table>'

    html = f'''
        <div class="tab-content" id="citizen_lines">
            <h2 class="section-title">🟠 CITIZEN ライン別詳細分析</h2>
            {table_html}
            <div class="chart" id="citizen_lines_chart"></div>
            {models_html}
        </div>
    '''
    return html

# G-SHOCK専用タブ生成
def generate_gshock_tab():
    gshock_data = deepdive_data['casio_lines'].get('G-SHOCK', {})

    if not gshock_data:
        return '<div class="tab-content" id="gshock"><p>G-SHOCKのデータがありません</p></div>'

    html = f'''
        <div class="tab-content" id="gshock">
            <h2 class="section-title">⚡ G-SHOCK 特集</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>総販売数</h3>
                    <p>{gshock_data['count']:,}</p>
                </div>
                <div class="stat-card">
                    <h3>中央値</h3>
                    <p>${gshock_data['median']:.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>CV値（安定度）</h3>
                    <p>{gshock_data['cv']:.3f}</p>
                </div>
                <div class="stat-card">
                    <h3>コラボモデル数</h3>
                    <p>{gshock_data.get('collab_count', 0)}</p>
                </div>
                <div class="stat-card">
                    <h3>限定モデル数</h3>
                    <p>{gshock_data.get('limited_count', 0)}</p>
                </div>
                <div class="stat-card">
                    <h3>JDMプレミアム</h3>
                    <p>{gshock_data['jdm_premium']:+.1f}%</p>
                </div>
            </div>

            <h3 style="margin-top: 30px;">📌 G-SHOCK 人気モデルTop10</h3>
            <table>
                <tr><th>順位</th><th>型番</th><th>販売数</th><th>中央値</th><th>CV値</th></tr>
    '''

    for i, model in enumerate(gshock_data.get('top_models', []), 1):
        html += f"<tr><td>{i}</td><td><strong>{model['model']}</strong></td><td>{model['count']}</td><td>${model['median']:.0f}</td><td>{model['cv']:.3f}</td></tr>"

    html += '''
            </table>
            <div class="chart" id="gshock_chart"></div>
        </div>
    '''
    return html

# 駆動方式別詳細タブ生成（自動巻の例）
def generate_movement_tab(movement_type, movement_name, emoji):
    movement_data = deepdive_data['movement_details'].get(movement_type, {})

    if not movement_data:
        return f'<div class="tab-content" id="movement_{movement_name}"><p>{movement_type}のデータがありません</p></div>'

    # ブランドランキングテーブル
    table_html = '<table><tr><th>順位</th><th>ブランド</th><th>販売数</th><th>中央値</th><th>CV値</th></tr>'
    for i, brand in enumerate(movement_data.get('brand_ranking', []), 1):
        table_html += f"<tr><td>{i}</td><td><strong>{brand['brand']}</strong></td><td>{brand['count']:,}</td><td>${brand['median']:.0f}</td><td>{brand['cv']:.3f}</td></tr>"
    table_html += '</table>'

    # 売れ筋価格帯
    bestseller_html = f'''
    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>🎯 売れ筋価格帯: {movement_data.get('bestseller_range', 'N/A')}</h3>
        <p>この価格帯に全体の {movement_data.get('bestseller_ratio', 0):.1f}% が集中しています</p>
    </div>
    '''

    html = f'''
        <div class="tab-content" id="movement_{movement_name}">
            <h2 class="section-title">{emoji} {movement_type} 詳細分析</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>総販売数</h3>
                    <p>{movement_data.get('total_count', 0):,}</p>
                </div>
                <div class="stat-card">
                    <h3>中央値</h3>
                    <p>${movement_data.get('median', 0):.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>商品数</h3>
                    <p>{movement_data.get('total_items', 0):,}</p>
                </div>
            </div>

            {bestseller_html}

            <h3 style="margin-top: 30px;">🏆 ブランド別販売数Top15</h3>
            {table_html}

            <h3 style="margin-top: 30px;">📊 価格帯分布</h3>
            <div class="chart" id="movement_{movement_name}_price_dist"></div>

            <h3 style="margin-top: 30px;">📈 月別販売推移</h3>
            <div class="chart" id="movement_{movement_name}_monthly"></div>
        </div>
    '''
    return html

# パーツタブ
def generate_parts_tab():
    parts = full_data['parts_analysis']

    table_html = '<table><tr><th>パーツ種類</th><th>販売数</th><th>中央値</th><th>最安値</th><th>最高値</th></tr>'
    for parts_type, data in sorted(parts.items(), key=lambda x: x[1]['count'] if isinstance(x[1], dict) and 'count' in x[1] else 0, reverse=True):
        if parts_type != 'by_brand' and isinstance(data, dict) and 'count' in data:
            table_html += f"<tr><td><strong>{parts_type}</strong></td><td>{data['count']}</td><td>${data['median']:.0f}</td><td>${data['min']:.0f}</td><td>${data['max']:.0f}</td></tr>"
    table_html += '</table>'

    brand_html = '<h3 style="margin-top: 30px;">ブランド別パーツ販売Top10</h3><table><tr><th>ブランド</th><th>販売数</th><th>中央値</th></tr>'
    for brand in parts.get('by_brand', []):
        brand_html += f"<tr><td><strong>{brand['brand']}</strong></td><td>{brand['count']}</td><td>${brand['median']:.0f}</td></tr>"
    brand_html += '</table>'

    html = f'''
        <div class="tab-content" id="parts">
            <h2 class="section-title">🔧 パーツ市場分析</h2>
            {table_html}
            {brand_html}
            <div class="chart" id="parts_chart"></div>
        </div>
    '''
    return html

# まとめ売りタブ
def generate_bundles_tab():
    bundles = full_data['bundle_analysis']

    html = f'''
        <div class="tab-content" id="bundles">
            <h2 class="section-title">📦 まとめ売り市場分析</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>総販売数</h3>
                    <p>{bundles['total_count']}</p>
                </div>
                <div class="stat-card">
                    <h3>商品数</h3>
                    <p>{bundles['total_items']}</p>
                </div>
                <div class="stat-card">
                    <h3>中央値</h3>
                    <p>${bundles['median']:.0f}</p>
                </div>
                <div class="stat-card">
                    <h3>平均価格</h3>
                    <p>${bundles['avg']:.0f}</p>
                </div>
            </div>
            <p style="margin-top: 20px; line-height: 1.8;">
                まとめ売り商品は、複数の時計やパーツをセットで販売する形式です。<br>
                中央値${bundles['median']:.0f}と単品よりも高額になる傾向がありますが、<br>
                バイヤーにとっては仕入れ効率が良く、利益率も期待できます。
            </p>
        </div>
    '''
    return html

# おすすめタブ
def generate_recommendations_tab():
    rotation = full_data['recommendation']['rotation_mode']
    profit = full_data['recommendation']['profit_mode']

    rotation_html = '<h3>🔄 回転重視モード（安定性＆低リスク）</h3><p style="margin-bottom: 15px;">CV≤0.3、仕入れ上限≤¥30,000の安定商材</p><table><tr><th>順位</th><th>ブランド</th><th>駆動方式</th><th>販売数</th><th>中央値</th><th>仕入れ上限</th><th>CV</th><th>安定度</th><th>リスク</th></tr>'

    for i, item in enumerate(rotation[:30], 1):
        rotation_html += f'''<tr>
            <td>{i}</td>
            <td><strong>{item['brand']}</strong></td>
            <td>{item['movement']}</td>
            <td>{item['count']}</td>
            <td>${item['median']:.0f}</td>
            <td>¥{item['breakeven']:,.0f}</td>
            <td>{item['cv']:.3f}</td>
            <td>{item['stability']}</td>
            <td><span class="badge badge-{item['risk'].lower()}">{item['risk']}</span></td>
        </tr>'''

    rotation_html += '</table>'

    profit_html = '<h3 style="margin-top: 40px;">💰 利益重視モード（トレンド重視）</h3><p style="margin-bottom: 15px;">売上トレンドを考慮した利益最大化戦略</p><table><tr><th>順位</th><th>ブランド</th><th>駆動方式</th><th>販売数</th><th>中央値</th><th>仕入れ上限</th><th>トレンド</th><th>リスク</th></tr>'

    for i, item in enumerate(profit[:30], 1):
        profit_html += f'''<tr>
            <td>{i}</td>
            <td><strong>{item['brand']}</strong></td>
            <td>{item['movement']}</td>
            <td>{item['count']}</td>
            <td>${item['median']:.0f}</td>
            <td>¥{item['breakeven']:,.0f}</td>
            <td>{item['trend']}</td>
            <td><span class="badge badge-{item['risk'].lower()}">{item['risk']}</span></td>
        </tr>'''

    profit_html += '</table>'

    html = f'''
        <div class="tab-content" id="recommendations">
            <h2 class="section-title">🎯 おすすめ出品順序</h2>
            {rotation_html}
            {profit_html}
        </div>
    '''
    return html

# JavaScriptセクション
def generate_javascript():
    full = full_data
    deep = deepdive_data

    # ブランド別チャート
    brands = full['brand_stats']
    brand_names = [b['brand'] for b in brands]
    brand_counts = [b['count'] for b in brands]

    # 駆動方式別チャート
    movements = full['movement_types']
    movement_names = list(movements.keys())
    movement_counts = [movements[m]['count'] for m in movement_names]

    # 月別推移
    monthly = full['monthly_trend']
    months = [m['month'] for m in monthly]

    # SEIKOライン別
    seiko_lines = deep['seiko_lines']
    seiko_line_names = list(seiko_lines.keys())
    seiko_line_counts = [seiko_lines[l]['count'] for l in seiko_line_names]

    # CASIOライン別
    casio_lines = deep['casio_lines']
    casio_line_names = list(casio_lines.keys())
    casio_line_counts = [casio_lines[l]['count'] for l in casio_line_names]

    # CITIZENライン別
    citizen_lines = deep['citizen_lines']
    citizen_line_names = list(citizen_lines.keys())
    citizen_line_counts = [citizen_lines[l]['count'] for l in citizen_line_names]

    js = f'''
        <script>
            function showTab(tabName) {{
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));

                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }}

            // Brand chart
            Plotly.newPlot('brand_chart', [{{
                x: {brand_names},
                y: {brand_counts},
                type: 'bar',
                marker: {{color: '#667eea'}}
            }}], {{
                title: 'ブランド別販売数Top20',
                xaxis: {{title: 'ブランド'}},
                yaxis: {{title: '販売数'}}
            }});

            // Movement chart
            Plotly.newPlot('movement_chart', [{{
                labels: {movement_names},
                values: {movement_counts},
                type: 'pie',
                marker: {{colors: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']}}
            }}], {{
                title: '駆動方式別分布'
            }});

            // SEIKO lines chart
            Plotly.newPlot('seiko_lines_chart', [{{
                x: {seiko_line_names},
                y: {seiko_line_counts},
                type: 'bar',
                marker: {{color: '#4169e1'}}
            }}], {{
                title: 'SEIKOライン別販売数',
                xaxis: {{title: 'ライン'}},
                yaxis: {{title: '販売数'}}
            }});

            // CASIO lines chart
            Plotly.newPlot('casio_lines_chart', [{{
                x: {casio_line_names},
                y: {casio_line_counts},
                type: 'bar',
                marker: {{color: '#32cd32'}}
            }}], {{
                title: 'CASIOライン別販売数',
                xaxis: {{title: 'ライン'}},
                yaxis: {{title: '販売数'}}
            }});

            // CITIZEN lines chart
            Plotly.newPlot('citizen_lines_chart', [{{
                x: {citizen_line_names},
                y: {citizen_line_counts},
                type: 'bar',
                marker: {{color: '#ff8c00'}}
            }}], {{
                title: 'CITIZENライン別販売数',
                xaxis: {{title: 'ライン'}},
                yaxis: {{title: '販売数'}}
            }});
        </script>
    '''
    return js

# HTML生成
print("📄 HTML生成中...")

html_content = html_header
html_content += generate_overview_tab()
html_content += generate_seiko_lines_tab()
html_content += generate_casio_lines_tab()
html_content += generate_citizen_lines_tab()
html_content += generate_gshock_tab()
html_content += generate_movement_tab('自動巻', 'auto', '⚙️')
html_content += generate_movement_tab('クォーツ', 'quartz', '🔋')
html_content += generate_movement_tab('ソーラー', 'solar', '☀️')
html_content += generate_parts_tab()
html_content += generate_bundles_tab()
html_content += generate_recommendations_tab()
html_content += '''
        </div>
    </div>
'''
html_content += generate_javascript()
html_content += '''
</body>
</html>
'''

# 保存
output_path = '/Users/naokijodan/Desktop/watch-market-analysis/index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

file_size = os.path.getsize(output_path)
print(f"✅ HTML生成完了！ {output_path}")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
