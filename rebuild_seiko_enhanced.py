#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブをグラフ付きで完全再構築
"""

import json
import re

print("📄 SEIKOタブ拡張版再構築開始...")

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

# ライン定義（スクリプトから）
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

for model in all_models[:100]:  # Top100から振り分け
    line = classify_model_to_line(model['model'])
    line_models[line].append(model)

# 1. 基本統計カード
stats_html = f'''
    <div id="SEIKO" class="tab-content">
        <h2 class="section-title">📊 SEIKO 詳細分析</h2>

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
                <div class="value" style="color: var(--positive)">{seiko_brand['jdm_premium']:+.1f}%</div>
            </div>
        </div>
'''

# 2. 仕入れ戦略
strategy_html = '''
        <div class="insight-box">
            <h3>🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <h4 style="color: #1976d2; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong>JDM表記</strong>の国内限定モデル（+23.6%プレミアム）</li>
                        <li>型番が<strong>明確に記載</strong>されている商品</li>
                        <li><strong>箱・保証書付き</strong>（+10.0%プレミアム）</li>
                        <li>人気ライン：<strong>Prospex, Presage, Grand Seiko</strong></li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px;">
                    <h4 style="color: #f57c00; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>ヴィンテージのみを理由にした高値仕入れ（-4.8%逆プレミアム）</li>
                        <li>海外輸出用モデル（JDMではない）</li>
                        <li>箱なし・状態不明品</li>
                    </ul>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px;">
                    <h4 style="color: #7b1fa2; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> ¥35,000以下</p>
                    <p style="margin: 5px 0 0 0;"><strong>JDM+箱付き:</strong> $230前後が上限（中央値$180 + プレミアム）</p>
                </div>
            </div>
        </div>
'''

# 3. 価格帯別分析（50ドル刻み + 棒グラフ）
# 価格帯を50ドル刻みで計算（全モデルから）
price_bins = list(range(0, 651, 50))  # 0-650を50刻み
price_distribution = {f'${i}-{i+50}': 0 for i in price_bins[:-1]}

for model in all_models:
    price = model['median']
    for i in range(len(price_bins) - 1):
        if price_bins[i] <= price < price_bins[i+1]:
            price_distribution[f'${price_bins[i]}-{price_bins[i+1]}'] += model['count']
            break

# グラフ用データ
price_labels = list(price_distribution.keys())
price_values = list(price_distribution.values())

type_html = f'''
        <h3 class="section-title">📊 価格帯別分析（50ドル刻み）</h3>
        <div class="chart" id="seiko_price_chart"></div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>価格帯</th>
                        <th>販売数</th>
                        <th>比率</th>
                    </tr>
                </thead>
                <tbody>
'''

total_price_sales = sum(price_values)
for label, value in zip(price_labels, price_values):
    ratio = value / total_price_sales * 100 if total_price_sales > 0 else 0
    type_html += f'''
                    <tr>
                        <td><strong>{label}</strong></td>
                        <td>{value:,}</td>
                        <td>{ratio:.1f}%</td>
                    </tr>
    '''

type_html += '''
                </tbody>
            </table>
        </div>
'''

# 4. 駆動方式別分析 + 円グラフ
movement_dist = seiko_brand.get('movement_distribution', {})
sorted_movements = sorted(movement_dist.items(), key=lambda x: x[1], reverse=True)

movement_labels = [m[0] for m in sorted_movements if m[0] != '不明']
movement_values = [m[1] for m in sorted_movements if m[0] != '不明']

movement_html = f'''
        <h3 class="section-title">⚙️ 駆動方式別分析</h3>
        <div class="chart" id="seiko_movement_chart"></div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>駆動方式</th>
                        <th>商品数</th>
                        <th>比率</th>
                        <th>市場評価</th>
                    </tr>
                </thead>
                <tbody>
'''

total_movement = sum(movement_values)
for i, (movement, count) in enumerate(sorted_movements):
    if movement == '不明':
        continue
    ratio = count / total_movement * 100

    if movement == '自動巻':
        comment = '高需要・高価格帯'
    elif movement == 'クォーツ':
        comment = 'エントリー層に人気'
    elif movement == 'ソーラー':
        comment = '実用性高・安定需要'
    elif movement == '手巻き':
        comment = 'ヴィンテージ中心'
    else:
        comment = '-'

    movement_html += f'''
                    <tr>
                        <td><strong>{movement}</strong></td>
                        <td>{count:,}</td>
                        <td>{ratio:.1f}%</td>
                        <td>{comment}</td>
                    </tr>
    '''

movement_html += '''
                </tbody>
            </table>
        </div>
'''

# 5. 性別分析 + 円グラフ
department_dist = seiko_brand.get('department_distribution', {})
sorted_depts = sorted(department_dist.items(), key=lambda x: x[1], reverse=True)

dept_labels = [d[0] for d in sorted_depts if d[0] != '不明']
dept_values = [d[1] for d in sorted_depts if d[0] != '不明']

gender_html = f'''
        <h3 class="section-title">👥 性別・カテゴリー別分析</h3>
        <div class="chart" id="seiko_gender_chart" style="height: 300px;"></div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>カテゴリー</th>
                        <th>商品数</th>
                        <th>比率</th>
                        <th>市場特性</th>
                    </tr>
                </thead>
                <tbody>
'''

total_dept = sum(dept_values)
for dept, count in sorted_depts:
    if dept == '不明':
        continue
    ratio = count / total_dept * 100

    if dept == 'メンズ':
        comment = '主力市場・高回転'
    elif dept == 'レディース':
        comment = 'ギフト需要あり'
    elif dept == 'ユニセックス':
        comment = 'トレンド層に人気'
    else:
        comment = '-'

    gender_html += f'''
                    <tr>
                        <td><strong>{dept}</strong></td>
                        <td>{count:,}</td>
                        <td>{ratio:.1f}%</td>
                        <td>{comment}</td>
                    </tr>
    '''

gender_html += '''
                </tbody>
            </table>
        </div>
'''

# 6. ライン別分析（パーセンテージ追加）
total_line_sales = sum(data['count'] for data in seiko_lines.values())

lines_html = '''
        <h3 class="section-title">🔵 ライン別詳細分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>JDM比率</th>
                        <th>JDMプレミアム</th>
                    </tr>
                </thead>
                <tbody>
'''

for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'
    line_ratio = data['count'] / total_line_sales * 100

    lines_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td>{line_ratio:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>{jdm_ratio}</td>
                        <td>{data['jdm_premium']:+.1f}%</td>
                    </tr>
    '''

lines_html += '''
                </tbody>
            </table>
        </div>
'''

# 7. 各ラインの人気モデル（再振り分けデータから）
line_models_html = '<h3 class="section-title">📌 各ラインの人気モデル</h3>'

for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    models = line_models.get(line_name, [])[:5]  # Top5

    if not models:
        continue

    line_models_html += f'''
        <h4 style="color: #667eea; margin-top: 25px; border-bottom: 2px solid #667eea; padding-bottom: 5px;">{line_name}</h4>
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
                        <td><strong>{i}</strong></td>
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
        <h3 class="section-title">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th>仕入上限(¥)</th>
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
                        <td><strong>{i}</strong></td>
                        <td>{model_name}</td>
                        <td>{count}</td>
                        <td>${median:.2f}</td>
                        <td class="highlight">¥{breakeven:,.0f}</td>
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

# JavaScript用グラフコード生成
graph_js = f'''
        <script>
        // 価格帯棒グラフ
        Plotly.newPlot('seiko_price_chart', [{{
            x: {price_labels},
            y: {price_values},
            type: 'bar',
            marker: {{color: '#667eea'}}
        }}], {{
            title: '価格帯別販売数分布（50ドル刻み）',
            xaxis: {{title: '価格帯'}},
            yaxis: {{title: '販売数'}},
            height: 400
        }});

        // 駆動方式円グラフ
        Plotly.newPlot('seiko_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#feca57']}}
        }}], {{
            title: '駆動方式別分布',
            height: 400
        }});

        // 性別円グラフ（小さめ）
        Plotly.newPlot('seiko_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: ['#667eea', '#f093fb', '#43e97b', '#feca57', '#ff6b6b']}}
        }}], {{
            title: '性別・カテゴリー別分布',
            height: 300
        }});
        </script>
'''

# 完全なSEIKOタブHTMLを構築
new_seiko_tab = (
    stats_html +
    strategy_html +
    type_html +
    movement_html +
    gender_html +
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
print(f"✅ SEIKOタブ拡張版完成！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"📊 追加内容:")
print(f"  - 価格帯50ドル刻み棒グラフ")
print(f"  - 駆動方式円グラフ")
print(f"  - 性別円グラフ（小）")
print(f"  - ライン別にパーセンテージ追加")
print(f"  - 各ラインの人気モデル（データ再振り分け）")
