#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブ レイアウト改善版（GPT提案反映）
- 2カラムグリッド
- SEIKOブルー＋オレンジアクセント
- インタラクティブ最小限
"""

import json
import re

print("📄 SEIKOタブ v2 レイアウト改善版...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# SEIKOデータ抽出
seiko_brand = brand_detail['brands']['SEIKO']
seiko_lines = deepdive['seiko_lines']
all_models = seiko_brand.get('model_stats', [])

# ライン定義
SEIKO_LINES = {
    'Grand Seiko': ['GRAND SEIKO', 'GS ', 'SBGR', 'SBGA', 'SBGM', 'SBGX'],
    'SEIKO 5': ['SEIKO 5', 'SEIKO5', '5 SPORTS', 'SNZG', 'SNK', 'SRPD'],
    'Prospex': ['PROSPEX', 'SBDC', 'SBDN', 'SPB', 'SRP'],
    'Presage': ['PRESAGE', 'SARY', 'SRPB', 'SSA', 'SRPE'],
    'Astron': ['ASTRON', 'SSE'],
    'King Seiko': ['KING SEIKO'],
    'Lord Marvel': ['LORD MARVEL'],
    'Dolce': ['DOLCE'],
    'Chariot': ['CHARIOT'],
}

def classify_model_to_line(model_name):
    """型番をラインに分類"""
    model_upper = model_name.upper()
    for line_name, keywords in SEIKO_LINES.items():
        for kw in keywords:
            if kw in model_upper:
                return line_name
    return 'その他SEIKO'

# 各ラインに型番を振り分け
line_models = {line: [] for line in SEIKO_LINES.keys()}
line_models['その他SEIKO'] = []

for model in all_models[:100]:
    line = classify_model_to_line(model['model'])
    line_models[line].append(model)

# CSSスタイル追加（2カラムグリッド）
additional_css = '''
<style>
.seiko-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.seiko-chart-container {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.seiko-accent {
    color: #ff6b35;
    font-weight: bold;
}

.seiko-blue {
    color: #0051a5;
}

@media (max-width: 768px) {
    .seiko-grid {
        grid-template-columns: 1fr;
    }
}
</style>
'''

# 1. 基本統計カード
stats_html = f'''
    <div id="SEIKO" class="tab-content">
        <h2 class="section-title seiko-blue">📊 SEIKO 詳細分析</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{seiko_brand['total_sales']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${seiko_brand['median_price']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">{seiko_brand['cv']:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">JDMプレミアム</div>
                <div class="value seiko-accent">{seiko_brand['jdm_premium']:+.1f}%</div>
            </div>
        </div>
'''

# 2. 仕入れ戦略（オレンジアクセント強調）
strategy_html = '''
        <div class="insight-box" style="border-left: 5px solid #ff6b35;">
            <h3 class="seiko-blue">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #0051a5;">
                    <h4 style="color: #0051a5; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong class="seiko-accent">JDM表記</strong>の国内限定モデル（<span class="seiko-accent">+23.6%</span>プレミアム）</li>
                        <li>型番が<strong>明確に記載</strong>されている商品</li>
                        <li><strong class="seiko-accent">箱・保証書付き</strong>（<span class="seiko-accent">+10.0%</span>プレミアム）</li>
                        <li>人気ライン：<strong>Prospex, Presage, Grand Seiko</strong></li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff6b35;">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>ヴィンテージのみを理由にした高値仕入れ（<span style="color: #d32f2f;">-4.8%</span>逆プレミアム）</li>
                        <li>海外輸出用モデル（JDMではない）</li>
                        <li>箱なし・状態不明品</li>
                    </ul>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #7b1fa2;">
                    <h4 style="color: #7b1fa2; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> ¥35,000以下</p>
                    <p style="margin: 5px 0 0 0;"><strong class="seiko-accent">JDM+箱付き:</strong> $230前後が上限（中央値$180 + プレミアム）</p>
                </div>
            </div>
        </div>
'''

# 3-5. グラフエリア（2カラムグリッド）
# 価格帯データ
price_bins = list(range(0, 651, 50))
price_distribution = {f'${i}-{i+50}': 0 for i in price_bins[:-1]}

for model in all_models:
    price = model['median']
    for i in range(len(price_bins) - 1):
        if price_bins[i] <= price < price_bins[i+1]:
            price_distribution[f'${price_bins[i]}-{price_bins[i+1]}'] += model['count']
            break

price_labels = list(price_distribution.keys())
price_values = list(price_distribution.values())

# 駆動方式データ
movement_dist = seiko_brand.get('movement_distribution', {})
sorted_movements = sorted(movement_dist.items(), key=lambda x: x[1], reverse=True)
movement_labels = [m[0] for m in sorted_movements if m[0] != '不明']
movement_values = [m[1] for m in sorted_movements if m[0] != '不明']

# 性別データ
department_dist = seiko_brand.get('department_distribution', {})
sorted_depts = sorted(department_dist.items(), key=lambda x: x[1], reverse=True)
dept_labels = [d[0] for d in sorted_depts if d[0] != '不明']
dept_values = [d[1] for d in sorted_depts if d[0] != '不明']

graphs_html = f'''
        <h3 class="section-title seiko-blue">📊 市場分析グラフ</h3>
        <div class="seiko-grid">
            <div class="seiko-chart-container">
                <h4 class="seiko-blue">価格帯別分析（50ドル刻み）</h4>
                <div id="seiko_price_chart" style="height: 350px;"></div>
            </div>
            <div class="seiko-chart-container">
                <h4 class="seiko-blue">駆動方式別分布</h4>
                <div id="seiko_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="seiko-chart-container">
                <h4 class="seiko-blue">性別・カテゴリー別分布</h4>
                <div id="seiko_gender_chart" style="height: 300px;"></div>
            </div>
        </div>
'''

# 6. ライン別分析（パーセンテージ＋オレンジアクセント）
total_line_sales = sum(data['count'] for data in seiko_lines.values())

lines_html = '''
        <h3 class="section-title seiko-blue">🔵 ライン別詳細分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th class="seiko-accent">比率</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>JDM比率</th>
                        <th class="seiko-accent">JDMプレミアム</th>
                    </tr>
                </thead>
                <tbody>
'''

for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'
    line_ratio = data['count'] / total_line_sales * 100

    premium_color = 'seiko-accent' if data['jdm_premium'] > 10 else ''

    lines_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td class="seiko-accent">{line_ratio:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>{jdm_ratio}</td>
                        <td class="{premium_color}">{data['jdm_premium']:+.1f}%</td>
                    </tr>
    '''

lines_html += '''
                </tbody>
            </table>
        </div>
'''

# 7. 各ラインの人気モデル
line_models_html = '<h3 class="section-title seiko-blue">📌 各ラインの人気モデル</h3>'

for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    models = line_models.get(line_name, [])[:5]

    if not models:
        continue

    line_models_html += f'''
        <h4 style="color: #0051a5; margin-top: 25px; border-bottom: 2px solid #0051a5; padding-bottom: 5px;">{line_name}</h4>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, model in enumerate(models, 1):
        line_models_html += f'''
                    <tr>
                        <td><strong class="seiko-accent">{i}</strong></td>
                        <td>{model['model']}</td>
                        <td>{model['count']}</td>
                        <td>${model['median']:.0f}</td>
                        <td>{model['cv']:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=SEIKO+{model['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=SEIKO%20{model['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
        '''

    line_models_html += '''
                </tbody>
            </table>
        </div>
    '''

# 8. 型番分析30種
top_models = all_models[:30]

top30_html = '''
        <h3 class="section-title seiko-blue">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th class="seiko-accent">仕入上限(¥)</th>
                        <th>CV</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

for i, model in enumerate(top_models, 1):
    model_name = model['model']
    count = model['count']
    median = model['median']
    breakeven = model['breakeven']
    cv = model['cv']

    top30_html += f'''
                    <tr>
                        <td><strong class="seiko-accent">{i}</strong></td>
                        <td>{model_name}</td>
                        <td>{count}</td>
                        <td>${median:.2f}</td>
                        <td class="highlight seiko-accent">¥{breakeven:,.0f}</td>
                        <td>{cv:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=SEIKO+{model_name}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=SEIKO%20{model_name}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
    '''

top30_html += '''
                </tbody>
            </table>
        </div>
'''

# JavaScript用グラフコード（SEIKOブルー＋オレンジアクセント）
graph_js = f'''
        <script>
        // SEIKOブランドカラー定義
        const seikoBlue = '#0051a5';
        const seikoOrange = '#ff6b35';
        const seikoGradient = ['#0051a5', '#0066cc', '#0080ff', '#3399ff', '#66b3ff'];

        // 価格帯棒グラフ
        Plotly.newPlot('seiko_price_chart', [{{
            x: {price_labels},
            y: {price_values},
            type: 'bar',
            marker: {{
                color: seikoBlue,
                line: {{color: seikoOrange, width: 1}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        // 駆動方式円グラフ
        Plotly.newPlot('seiko_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: seikoGradient}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        // 性別円グラフ
        Plotly.newPlot('seiko_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: [seikoBlue, seikoOrange, '#66b3ff', '#ffa366', '#99ccff']}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
'''

# 完全なSEIKOタブHTMLを構築
new_seiko_tab = (
    additional_css +
    stats_html +
    strategy_html +
    graphs_html +
    lines_html +
    line_models_html +
    top30_html +
    '    </div>\n' +
    graph_js
)

# 既存のSEIKOタブを置換
pattern = r'<div id="SEIKO" class="tab-content">.*?</div>\s*(?=<div id="|</div>\s*<script>)'
html = re.sub(pattern, new_seiko_tab, html, flags=re.DOTALL, count=1)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html.encode('utf-8'))
print(f"✅ SEIKOタブ v2 完成！（レイアウト改善版）")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"🎨 改善内容:")
print(f"  ✓ 2カラムグリッドレイアウト（グラフ横並び）")
print(f"  ✓ SEIKOブルー（#0051a5）基調")
print(f"  ✓ オレンジアクセント（#ff6b35）で重要情報強調")
print(f"  ✓ ホバー情報を最小限に")
print(f"  ✓ レスポンシブデザイン対応")
