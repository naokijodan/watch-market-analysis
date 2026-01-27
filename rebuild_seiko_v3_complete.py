#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブ v3 完全版
- 元CSVから正しくライン分類
- キャラクターウォッチ、Credor、Spirit、Exce line等を追加
- 各ラインの人気モデルを正確に抽出
"""

import pandas as pd
import json
import re
import numpy as np

print("📄 SEIKOタブ v3 完全版再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_seiko = df[(df['ブランド']=='SEIKO') & (df['商品状態']=='完品')].copy()

print(f"✓ SEIKO完品データ: {len(df_seiko)}件")

# 完全なライン定義（優先順位順）
SEIKO_LINES_COMPLETE = {
    # 高級ライン
    'Grand Seiko': ['GRAND SEIKO', 'GS ', ' GS', 'SBGR', 'SBGA', 'SBGM', 'SBGX', 'SBGE', 'SBGC'],
    'Credor': ['CREDOR'],
    'King Seiko': ['KING SEIKO'],

    # メインライン
    'Prospex': ['PROSPEX', 'SBDC', 'SBDN', 'SPB', 'SBDL', 'SBDY', 'SBDX', 'SBBN', 'SBEP'],
    'Presage': ['PRESAGE', 'COCKTAIL', 'SARY', 'SRPB', 'SSA', 'SRPE', 'SRPC', 'SRPH', 'SRRX'],
    'Astron': ['ASTRON', 'SSE', 'SSH'],
    'SEIKO 5': ['SEIKO 5', 'SEIKO5', '5 SPORTS', 'SNZG', 'SNK', 'SRPD', 'SRPE'],

    # サブブランド・特殊ライン
    'ALBA': ['ALBA', 'AIGN', 'AQPS', 'AQGK', 'AEFN'],
    'Spirit': ['SPIRIT', 'SCVE', 'SCXP', 'SBPX', 'SBPY'],
    'Selection': ['SELECTION', 'SBTR', 'SBPX'],
    'Dolce': ['DOLCE', 'SACL', 'SACM', 'SADZ', 'SCXK'],
    'Exceline': ['EXCELINE', 'SWCW', 'SWCP'],
    'Lukia': ['LUKIA', 'SSVW', 'SSQV', 'SSVR'],
    'Brightz': ['BRIGHTZ', 'SAGA', 'SAGZ'],
    'Wired': ['WIRED', 'AGAW', 'AGAV'],

    # ヴィンテージライン
    'Lord Marvel': ['LORD MARVEL'],
    'Lord Matic': ['LORD MATIC', 'LORDMATIC'],
    'Chariot': ['CHARIOT'],
    'Bellmatic': ['BELLMATIC', 'BELL MATIC'],
    'Sportsmatic': ['SPORTSMATIC', 'SPORTS MATIC'],
    'King-Matic': ['KING MATIC', 'KINGMATIC', 'KM'],

    # 特殊カテゴリ
    'キャラクターウォッチ': ['DISNEY', 'MICKEY', 'HELLO KITTY', 'MARVEL', 'STAR WARS',
                       'POKEMON', 'GUNDAM', 'ONE PIECE', 'DORAEMON', 'DEMON SLAYER',
                       'CHARACTER', 'COLLABORATION'],
    'Kinetic': ['KINETIC', 'AUTO RELAY'],
    'Velatura': ['VELATURA'],
    'Ananta': ['ANANTA'],
}

def classify_seiko_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in SEIKO_LINES_COMPLETE.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return 'その他SEIKO'

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
    """タイトルから型番を抽出"""
    title_upper = str(title).upper()

    # SEIKOの型番パターン
    # パターン1: 4桁-4桁（例：5740-8000、7731-5120）
    pattern1 = r'\b\d{4}-\d{4}\b'
    match1 = re.search(pattern1, title_upper)
    if match1:
        return match1.group()

    # パターン2: アルファベット+数字（SBGA211、SRPD51、SNK809等）
    pattern2 = r'\b[A-Z]{2,4}\d{3,5}[A-Z]{0,2}\b'
    match2 = re.search(pattern2, title_upper)
    if match2:
        candidate = match2.group()
        # 除外ワード（ブランド名等）
        exclude = ['SEIKO', 'JAPAN', 'MINT', 'RARE', 'VINTAGE', 'GRAND']
        if candidate not in exclude:
            return candidate

    return None

# ライン分類実行
df_seiko['ライン'] = df_seiko['タイトル_upper'].apply(classify_seiko_line)

# 型番を抽出
df_seiko['型番抽出'] = df_seiko['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_seiko['型番抽出'].notna().sum()}件")

# ライン別統計を計算
line_stats = {}
line_models_dict = {}

for line, group in df_seiko.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    # 型番別Top5を抽出
    model_stats = []
    model_group = group[group['型番抽出'].notna()].copy()
    model_group = model_group[model_group['型番抽出'] != '']

    if len(model_group) > 0:
        for model, mg in model_group.groupby('型番抽出'):
            model_sales = mg['販売数'].sum()
            if model_sales >= 2:
                model_stats.append({
                    'model': model,
                    'count': int(model_sales),
                    'median': float(mg['価格'].median()),
                    'cv': float(calculate_cv(mg['価格'].values)),
                    'title_sample': mg.iloc[0]['タイトル'][:60]
                })

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:5]

    line_stats[line] = {
        'count': int(sales),
        'median': float(np.median(prices)),
        'cv': float(calculate_cv(prices)),
    }

    line_models_dict[line] = model_stats

# 結果表示
print("\n=== ライン別分類結果 ===")
total_sales = sum(s['count'] for s in line_stats.values())
for line, stats in sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    ratio = stats['count'] / total_sales * 100
    print(f"{line}: {stats['count']}個 ({ratio:.1f}%) - 人気モデル: {len(line_models_dict.get(line, []))}個")

# HTMLに統合するデータを取得
seiko_brand = brand_detail['brands']['SEIKO']
seiko_lines = deepdive['seiko_lines']
all_models = seiko_brand.get('model_stats', [])

# CSSスタイル追加
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

.model-sample {
    font-size: 0.85em;
    color: #666;
    font-style: italic;
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

# 2. 仕入れ戦略
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
                        <li>人気ライン：<strong>Prospex, Presage, Grand Seiko, Spirit</strong></li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff6b35;">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>ヴィンテージのみを理由にした高値仕入れ（<span style="color: #d32f2f;">-4.8%</span>逆プレミアム）</li>
                        <li>海外輸出用モデル（JDMではない）</li>
                        <li>箱なし・状態不明品</li>
                        <li>「その他SEIKO」で型番不明の商品</li>
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

# 3-5. グラフエリア（価格帯・駆動方式・性別）
# 価格帯分布を元CSVから正確に計算
price_bins = list(range(0, 651, 50))
bin_labels = [f'${i}-{i+50}' for i in price_bins[:-1]]

price_distribution = {}
for i in range(len(price_bins) - 1):
    mask = (df_seiko['価格'] >= price_bins[i]) & (df_seiko['価格'] < price_bins[i+1])
    count = df_seiko[mask]['販売数'].sum()
    price_distribution[bin_labels[i]] = int(count)

price_labels = list(price_distribution.keys())
price_values = list(price_distribution.values())

# 駆動方式分布を元CSVから計算
movement_dist_real = df_seiko.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
movement_labels = [mv for mv in movement_dist_real.index if mv != '不明']
movement_values = [int(movement_dist_real[mv]) for mv in movement_labels]

# 性別分布を元CSVから計算
dept_dist_real = df_seiko.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist_real.index if dept != '不明']
dept_values = [int(dept_dist_real[dept]) for dept in dept_labels]

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

# 6. ライン別分析（パーセンテージ追加）
total_line_sales = sum(data['count'] for data in seiko_lines.values())

lines_html = '''
        <h3 class="section-title seiko-blue">🔵 ライン別詳細分析（全{ライン数}ライン）</h3>
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

# 7. 各ラインの人気モデル（CSVから再分類）
line_models_html = '<h3 class="section-title seiko-blue">📌 各ラインの人気モデル（実データより）</h3>'
line_models_html += '<p style="color: #666; margin-bottom: 20px;">元CSVデータから再分類した正確な人気モデルTop5</p>'

for line_name in sorted(line_stats.keys(), key=lambda x: line_stats[x]['count'], reverse=True):
    models = line_models_dict.get(line_name, [])[:5]

    if not models:
        continue

    line_models_html += f'''
        <h4 style="color: #0051a5; margin-top: 25px; border-bottom: 2px solid #0051a5; padding-bottom: 5px;">
            {line_name} <span style="font-size: 0.9em; color: #666;">（販売数: {line_stats[line_name]['count']:,}個）</span>
        </h4>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>商品例</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, model in enumerate(models, 1):
        line_models_html += f'''
                    <tr>
                        <td><strong class="seiko-accent">{i}</strong></td>
                        <td><strong>{model['model']}</strong></td>
                        <td>{model['count']}</td>
                        <td>${model['median']:.0f}</td>
                        <td>{model['cv']:.3f}</td>
                        <td class="model-sample">{model.get('title_sample', '')}</td>
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

# 8. 型番Top30
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

# JavaScript用グラフコード
graph_js = f'''
        <script>
        const seikoBlue = '#0051a5';
        const seikoOrange = '#ff6b35';
        const seikoGradient = ['#0051a5', '#0066cc', '#0080ff', '#3399ff', '#66b3ff'];

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
print(f"\n✅ SEIKOタブ v3 完全版完成！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"🎯 改善内容:")
print(f"  ✓ 元CSVから正確にライン分類")
print(f"  ✓ {len(line_stats)}ラインを認識（キャラクターウォッチ、Credor、Spirit等を追加）")
print(f"  ✓ 各ラインの実際の人気モデルTop5を抽出")
print(f"  ✓ 商品タイトルサンプルを表示")
