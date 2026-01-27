#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CITIZENタブ v3 完全版（SEIKOタブ・CASIOタブを雛形に作成）
- 元CSVから正確にライン分類
- キャラクター/コラボ分析（複数視点）
- 各ラインの人気モデルTop15を抽出
"""

import pandas as pd
import json
import re
import numpy as np

print("📄 CITIZENタブ v3 完全版再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_citizen = df[(df['ブランド']=='CITIZEN') & (df['商品状態']=='完品')].copy()

print(f"✓ CITIZEN完品データ: {len(df_citizen)}件")

# 完全なライン定義（優先順位順）
CITIZEN_LINES_COMPLETE = {
    # ===== メインライン =====
    'Promaster': [
        'PROMASTER', 'PRO MASTER',
        'SKY', 'LAND', 'MARINE',
        'BN0', 'BJ7', 'BN2', 'BN4', 'JY8', 'CB5', 'AS7',
        'PMV', 'PMD', 'PMK',
    ],

    'Eco-Drive': [
        'ECO-DRIVE', 'ECO DRIVE',
        'ECODRIVE',
        'E870', 'E168', 'E111',
        'AT8', 'AT0', 'AW1', 'BM6', 'BM7', 'BM8',
    ],

    'Attesa': [
        'ATTESA',
        'AT8040', 'AT8185', 'AT8144',
        'CC', 'CB', 'AT',
    ],

    'Exceed': [
        'EXCEED',
        'AS7', 'ES9', 'ES8', 'EB',
        'EBG', 'EBD',
    ],

    'Campanola': [
        'CAMPANOLA',
        'CTR', 'AH7', 'AH4', 'BZ',
    ],

    'The CITIZEN': [
        'THE CITIZEN',
        'AQ4', 'AQ1', 'CTQ',
    ],

    # ===== 特殊シリーズ =====
    'ANA-DIGI TEMP': [
        'ANA-DIGI TEMP', 'ANA DIGI TEMP',
        'ANADIGI TEMP', 'ANADIGITEMP',
        'JG2', 'JM0',
    ],

    'Tsuyosa': [
        'TSUYOSA',
        'NK0', 'NJ0', 'C7',
    ],

    'Nighthawk': [
        'NIGHTHAWK', 'NIGHT HAWK',
        'BJ7', 'CA4', 'CB5',
    ],

    'Chronomaster': [
        'CHRONOMASTER', 'CHRONO MASTER',
        'AQ4', 'AV0',
    ],

    'Satellite Wave': [
        'SATELLITE WAVE', 'SATELLITE-WAVE',
        'CC3', 'CC9', 'F100', 'F150', 'F900',
    ],

    # ===== ヴィンテージ/その他 =====
    'Seven Star': [
        'SEVEN STAR', 'SEVEN-STAR',
        'SEVENSTAR', '7-STAR',
    ],

    'Cosmotron': [
        'COSMOTRON',
    ],

    'Leopard': [
        'LEOPARD',
    ],

    'Homer Date': [
        'HOMER DATE', 'HOMERDATE',
        'HOMER',
    ],

    'OXY': [
        'OXY',
        '5508', '5509',
    ],

    'Crystron': [
        'CRYSTRON',
    ],

    'FORMA': [
        'FORMA',
        'FRA', 'FRD',
    ],

    'xC': [
        'XC ', ' XC', 'X-C',
        'EC1', 'ES9',
    ],

    'wicca': [
        'WICCA',
        'KL0', 'KP2', 'KS1',
    ],
}

def classify_citizen_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in CITIZEN_LINES_COMPLETE.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return 'その他CITIZEN'

def extract_model_number(title):
    """タイトルから型番を抽出（CITIZEN用）"""
    title_upper = str(title).upper()

    # CITIZENの型番パターン
    # パターン1: アルファベット+数字+ハイフン+数字（BN0151-09L、JY8074-11X等）
    pattern1 = r'\b[A-Z]{2,3}\d{4}-\d{2}[A-Z]{0,2}\b'
    match1 = re.search(pattern1, title_upper)
    if match1:
        candidate = match1.group()
        exclude = ['CITIZEN']
        if candidate not in exclude:
            return candidate

    # パターン2: 4桁-5桁（ヴィンテージ用）
    pattern2 = r'\b\d{4}-\d{5,6}\b'
    match2 = re.search(pattern2, title_upper)
    if match2:
        return match2.group()

    return None

def calculate_cv(prices):
    """変動係数を計算"""
    if len(prices) < 2:
        return 0
    mean = np.mean(prices)
    if mean == 0:
        return 0
    std = np.std(prices, ddof=1)
    return std / mean

# ライン分類実行（通常）
df_citizen['ライン'] = df_citizen['タイトル_upper'].apply(classify_citizen_line)

# キャラクター/コラボ判定（別視点）
CHARACTER_KEYWORDS = [
    # コラボ一般
    'COLLABORATION', 'COLLAB',
    # 企業コラボ（最重要）
    ' ANA ', 'ANA-', 'ANA ORIGINAL', 'ANA COCKPIT',  # ANA関連（198個！）- スペース前後でマッチ
    'HONDA', 'TOYOTA', 'NISSAN', 'MAZDA',
    'BLUE ANGELS',  # Promaster限定
    # キャラクター
    'DISNEY', 'MICKEY', 'MINNIE',
    'HELLO KITTY', 'KITTY', 'SANRIO',
    'SNOOPY', 'PEANUTS', 'WOODSTOCK',
    # アニメ・ゲーム
    'FINAL FANTASY', 'FFXIV', 'FF14',
    'GUNDAM',
    'EVANGELION', ' EVA ',
    'ONE PIECE', 'NARUTO',
    ' 86 ', 'EIGHTY SIX', '86 COLLABORATION',  # アニメ86
    # その他
    'MARVEL', 'STAR WARS',
    # 限定モデル（幅広く検出）
    'LIMITED EDITION', 'SPECIAL EDITION', 'EXCLUSIVE',
]

def is_character_collab(title_upper):
    """キャラクター/コラボ商品かどうか判定"""
    for kw in CHARACTER_KEYWORDS:
        if kw in title_upper:
            return True
    return False

df_citizen['キャラクター/コラボ'] = df_citizen['タイトル_upper'].apply(is_character_collab)

# 型番を抽出
df_citizen['型番抽出'] = df_citizen['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_citizen['型番抽出'].notna().sum()}件")

# ライン別統計を計算
line_stats = {}
line_models_dict = {}

for line, group in df_citizen.groupby('ライン'):
    if len(group) < 2:
        continue

    prices = group['価格'].values
    sales = group['販売数'].sum()

    # 型番別Top15を抽出
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

    model_stats = sorted(model_stats, key=lambda x: x['count'], reverse=True)[:15]

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
    model_count = len(line_models_dict.get(line, []))
    print(f"{line}: {stats['count']}個 ({ratio:.1f}%) - 人気モデル: {model_count}個（Top15まで抽出）")

# HTMLに統合するデータを取得
citizen_brand = brand_detail['brands']['CITIZEN']
citizen_lines = deepdive['citizen_lines']
all_models = citizen_brand.get('model_stats', [])

# CSSスタイル追加
additional_css = '''
<style>
.citizen-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.citizen-chart-container {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.citizen-accent {
    color: #e63946;
    font-weight: bold;
}

.citizen-blue {
    color: #1565c0;
}

.model-sample {
    font-size: 0.85em;
    color: #666;
    font-style: italic;
}

@media (max-width: 768px) {
    .citizen-grid {
        grid-template-columns: 1fr;
    }
}
</style>
'''

# 1. 基本統計カード
stats_html = f'''
    <div id="CITIZEN" class="tab-content">
        <h2 class="section-title citizen-blue">📊 CITIZEN 詳細分析</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{citizen_brand['total_sales']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${citizen_brand['median_price']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">{citizen_brand['cv']:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">JDMプレミアム</div>
                <div class="value citizen-accent">{citizen_brand['jdm_premium']:+.1f}%</div>
            </div>
        </div>
'''

# 2. 仕入れ戦略
strategy_html = '''
        <div class="insight-box" style="border-left: 5px solid #e63946;">
            <h3 class="citizen-blue">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #1565c0;">
                    <h4 style="color: #1565c0; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong class="citizen-accent">Promaster Sky</strong>（Blue Angels等の限定モデル）</li>
                        <li><strong class="citizen-accent">ANA-DIGI TEMP</strong>（コラボモデル・限定色）</li>
                        <li><strong>Eco-Drive</strong>高機能モデル（ソーラー電波）</li>
                        <li><strong>Attesa</strong>チタンモデル</li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #f57c00;">
                    <h4 style="color: #f57c00; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>動作未確認のクォーツモデル</li>
                        <li>型番不明の中古品</li>
                        <li>ベルトのみ・文字盤のみ</li>
                    </ul>
                </div>
                <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 4px solid #388e3c;">
                    <h4 style="color: #388e3c; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>Promaster:</strong> ¥25,000-40,000</p>
                    <p style="margin: 5px 0 0 0;"><strong class="citizen-accent">ANA-DIGI TEMP:</strong> ¥15,000-30,000</p>
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
    mask = (df_citizen['価格'] >= price_bins[i]) & (df_citizen['価格'] < price_bins[i+1])
    count = df_citizen[mask]['販売数'].sum()
    price_distribution[bin_labels[i]] = int(count)

price_labels = list(price_distribution.keys())
price_values = list(price_distribution.values())

# 駆動方式分布を元CSVから計算
movement_dist_real = df_citizen.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
movement_labels = [mv for mv in movement_dist_real.index if mv != '不明']
movement_values = [int(movement_dist_real[mv]) for mv in movement_labels]

# 性別分布を元CSVから計算
dept_dist_real = df_citizen.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist_real.index if dept != '不明']
dept_values = [int(dept_dist_real[dept]) for dept in dept_labels]

graphs_html = f'''
        <h3 class="section-title citizen-blue">📊 市場分析グラフ</h3>
        <div class="citizen-grid">
            <div class="citizen-chart-container">
                <h4 class="citizen-blue">価格帯別分析（50ドル刻み）</h4>
                <div id="citizen_price_chart" style="height: 350px;"></div>
            </div>
            <div class="citizen-chart-container">
                <h4 class="citizen-blue">駆動方式別分布</h4>
                <div id="citizen_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="citizen-chart-container">
                <h4 class="citizen-blue">性別・カテゴリー別分布</h4>
                <div id="citizen_gender_chart" style="height: 300px;"></div>
            </div>
        </div>
'''

# 6. ライン別分析
total_line_sales = sum(data['count'] for data in citizen_lines.values())

lines_html = '''
        <h3 class="section-title citizen-blue">🔵 ライン別詳細分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th class="citizen-accent">比率</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>JDM比率</th>
                        <th class="citizen-accent">JDMプレミアム</th>
                    </tr>
                </thead>
                <tbody>
'''

for line_name, data in sorted(citizen_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'
    line_ratio = data['count'] / total_line_sales * 100
    premium_color = 'citizen-accent' if data['jdm_premium'] > 10 else ''

    lines_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td class="citizen-accent">{line_ratio:.1f}%</td>
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

# 6.5. キャラクター/コラボ分析（別視点）
character_data = df_citizen[df_citizen['キャラクター/コラボ']==True].copy()
character_sales = character_data['販売数'].sum()
character_median = character_data['価格'].median() if len(character_data) > 0 else 0

# キャラクター別集計
character_breakdown = {}
char_keywords_display = {
    'ANA': 'ANA（全日空コラボ）',
    'HONDA': 'ホンダ',
    'BLUE ANGELS': 'Blue Angels',
    'SNOOPY': 'スヌーピー',
    'PEANUTS': 'ピーナッツ',
    'DISNEY': 'ディズニー',
    'HELLO KITTY': 'ハローキティ',
    'FINAL FANTASY': 'ファイナルファンタジー',
    '86': '86（アニメ）',
    'GUNDAM': 'ガンダム',
    'EVANGELION': 'エヴァンゲリオン',
    'STAR WARS': 'スターウォーズ',
    'TOYOTA': 'トヨタ',
    'NISSAN': '日産',
}

for kw_en, kw_jp in char_keywords_display.items():
    mask = character_data['タイトル_upper'].str.contains(kw_en, na=False)
    count = character_data[mask]['販売数'].sum()
    if count > 0:
        character_breakdown[kw_jp] = int(count)

character_html = f'''
        <h3 class="section-title citizen-blue">🤝 キャラクター/コラボ分析（複数視点）</h3>
        <p style="color: #666; margin-bottom: 15px;">同じ商品を別の角度から分析 - 例：ANA-DIGI TEMPは「ANA-DIGI TEMPライン」と「ANAコラボ」の両方に該当</p>

        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="label">コラボ商品数</div>
                <div class="value citizen-accent">{character_sales:,}個</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${character_median:.0f}</div>
            </div>
            <div class="stat-card">
                <div class="label">全体比率</div>
                <div class="value citizen-accent">{character_sales/total_line_sales*100:.1f}%</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>コラボ/キャラクター</th>
                        <th>販売数</th>
                        <th>比率</th>
                    </tr>
                </thead>
                <tbody>
'''

for char_name, count in sorted(character_breakdown.items(), key=lambda x: x[1], reverse=True):
    ratio = count / character_sales * 100 if character_sales > 0 else 0
    character_html += f'''
                    <tr>
                        <td><strong>{char_name}</strong></td>
                        <td>{count:,}</td>
                        <td class="citizen-accent">{ratio:.1f}%</td>
                    </tr>
    '''

character_html += '''
                </tbody>
            </table>
        </div>
'''

# 7. 各ラインの人気モデル（CSVから再分類）
line_models_html = '<h3 class="section-title citizen-blue">📌 各ラインの人気モデル（実データより）</h3>'
line_models_html += '<p style="color: #666; margin-bottom: 20px;">元CSVデータから再分類した正確な人気モデルTop15</p>'

for line_name in sorted(line_stats.keys(), key=lambda x: line_stats[x]['count'], reverse=True):
    models = line_models_dict.get(line_name, [])[:15]

    if not models:
        continue

    line_models_html += f'''
        <h4 style="color: #1565c0; margin-top: 25px; border-bottom: 2px solid #1565c0; padding-bottom: 5px;">
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
                        <td><strong class="citizen-accent">{i}</strong></td>
                        <td><strong>{model['model']}</strong></td>
                        <td>{model['count']}</td>
                        <td>${model['median']:.0f}</td>
                        <td>{model['cv']:.3f}</td>
                        <td class="model-sample">{model.get('title_sample', '')}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=CITIZEN+{model['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=CITIZEN%20{model['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
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
        <h3 class="section-title citizen-blue">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th class="citizen-accent">仕入上限(¥)</th>
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
                        <td><strong class="citizen-accent">{i}</strong></td>
                        <td>{model_name}</td>
                        <td>{count}</td>
                        <td>${median:.2f}</td>
                        <td class="highlight citizen-accent">¥{breakeven:,.0f}</td>
                        <td>{cv:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=CITIZEN+{model_name}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=CITIZEN%20{model_name}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
    '''

top30_html += '''
                </tbody>
            </table>
        </div>
'''

# JavaScript用グラフコード（CITIZENブルー＋レッドアクセント）
graph_js = f'''
        <script>
        const citizenBlue = '#1565c0';
        const citizenRed = '#e63946';
        const citizenGradient = ['#1565c0', '#1976d2', '#42a5f5', '#64b5f6', '#90caf9'];

        Plotly.newPlot('citizen_price_chart', [{{
            x: {price_labels},
            y: {price_values},
            type: 'bar',
            marker: {{
                color: citizenBlue,
                line: {{color: citizenRed, width: 1}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('citizen_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: citizenGradient}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('citizen_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: [citizenBlue, citizenRed, '#64b5f6', '#42a5f5', '#90caf9']}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
'''

# 完全なCITIZENタブHTMLを構築
new_citizen_tab = (
    additional_css +
    stats_html +
    strategy_html +
    graphs_html +
    lines_html +
    character_html +
    line_models_html +
    top30_html +
    '    </div>\n' +
    graph_js
)

# 既存のCITIZENタブを置換
# **重要**: CITIZENタブは最後のタブなので、</body>の直前まで
pattern = r'<div id="CITIZEN" class="tab-content">.*?</div>(?=\s*</body>)'
html = re.sub(pattern, new_citizen_tab, html, flags=re.DOTALL, count=1)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html.encode('utf-8'))
print(f"\n✅ CITIZENタブ v3 完全版完成！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"🎯 改善内容:")
print(f"  ✓ 元CSVから正確にライン分類")
print(f"  ✓ {len(line_stats)}ラインを認識")
print(f"  ✓ 各ラインの実際の人気モデルTop15を抽出")
print(f"  ✓ キャラクター/コラボ分析を追加（複数視点）")
print(f"  ✓ 商品タイトルサンプルを表示")
