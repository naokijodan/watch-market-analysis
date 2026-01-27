#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADOタブ v3 完全版
- SEIKOタブの構造を完全模倣（Innovation禁止、Imitation絶対）
- 元CSVから正しくライン分類
- 素材・ヴィンテージ分析を追加
- 各ラインの人気モデルを正確に抽出
"""

import pandas as pd
import json
import re
import numpy as np

print("📄 RADOタブ v3 完全版再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# 元CSVを読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_rado = df[(df['ブランド']=='RADO') & (df['商品状態']=='完品')].copy()

print(f"✓ RADO完品データ: {len(df_rado)}件")

# 完全なライン定義（優先順位順）
RADO_LINES_COMPLETE = {
    # 主要ライン
    'DiaStar': ['DIASTAR', 'DIA STAR', 'DIA-STAR'],
    'Florence': ['FLORENCE'],
    'Golden Horse': ['GOLDEN HORSE', 'GREEN HORSE', 'PURPLE HORSE'],

    # サブライン
    'Balboa': ['BALBOA'],
    'Jubile': ['JUBILE', 'JUBILEE'],
    'Coupole': ['COUPOLE'],
    'Manchester': ['MANCHESTER'],
    'Voyager': ['VOYAGER'],

    # 現代ライン（データには少ないが定義）
    'Captain Cook': ['CAPTAIN COOK'],
    'Centrix': ['CENTRIX'],
    'True': ['TRUE THINLINE', 'TRUE SQUARE', 'TRUE '],
    'HyperChrome': ['HYPERCHROME', 'HYPER CHROME'],
    'Ceramica': ['CERAMICA'],
    'Integral': ['INTEGRAL'],
    'Original': ['ORIGINAL'],
}

def classify_rado_line(title_upper):
    """タイトルからライン名を抽出（優先順位順）"""
    for line_name, keywords in RADO_LINES_COMPLETE.items():
        for kw in keywords:
            if kw in title_upper:
                return line_name
    return 'その他RADO'

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
    """改善版：RADOの型番を抽出（8パターン対応）"""
    title_upper = str(title).upper()

    # パターン1: 5桁.4桁.1桁（例：68396.0068.3）
    pattern1 = r'\b\d{5}\.\d{4}\.\d\b'
    match1 = re.search(pattern1, title_upper)
    if match1:
        return match1.group()

    # パターン2: 2桁-3桁.4桁.1桁（例：67-396.0067.3）
    pattern2 = r'\b\d{2}-\d{3}\.\d{4}\.\d\b'
    match2 = re.search(pattern2, title_upper)
    if match2:
        return match2.group()

    # パターン3: 3桁.4桁.1桁+オプションアルファベット（例：152.0341.3、153.3606.2N）
    pattern3 = r'\b\d{3}\.\d{4}\.\d[A-Z]?\b'
    match3 = re.search(pattern3, title_upper)
    if match3:
        return match3.group()

    # パターン4: 5桁/数字（例：11675/1）
    pattern4 = r'\b\d{5}/\d+\b'
    match4 = re.search(pattern4, title_upper)
    if match4:
        return match4.group()

    # パターン5: R+8桁（例：R14061106）
    pattern5 = r'\bR\d{8}\b'
    match5 = re.search(pattern5, title_upper)
    if match5:
        return match5.group()

    # パターン6: 8桁+オプションアルファベット（例：20440794N）
    pattern6 = r'\b\d{8}[A-Z]?\b'
    match6 = re.search(pattern6, title_upper)
    if match6:
        candidate = match6.group()
        # 1900年代/2000年代の年号を除外
        if not candidate.startswith(('19', '20')):
            return candidate

    # パターン7: 5桁のみ（例：11006、11896）
    pattern7 = r'\b\d{5}\b'
    match7 = re.search(pattern7, title_upper)
    if match7:
        candidate = match7.group()
        # 1900年代/2000年代の年号を除外
        if not candidate.startswith(('19', '20')):
            return candidate

    # パターン8: 3桁.4桁のみ（例：332.7818）
    pattern8 = r'\b\d{3}\.\d{4}\b'
    match8 = re.search(pattern8, title_upper)
    if match8:
        return match8.group()

    return None

# ライン分類実行（通常）
df_rado['ライン'] = df_rado['タイトル_upper'].apply(classify_rado_line)

# 素材・ヴィンテージ判定（別視点）
RADO_FEATURES = {
    'Ceramic': ['CERAMIC', 'CERAMOS', 'HIGH-TECH CERAMIC', 'PLASMA'],
    'Vintage': ['VINTAGE', '70S', '80S', '90S', 'RETRO'],
    'Premium Metal': ['TUNGSTEN', 'TITANIUM'],
    'Sapphire': ['SAPPHIRE'],
    'Diamond': ['DIAMOND', 'JUBILEE'],
    'Limited': ['LIMITED', 'SPECIAL EDITION', 'ANNIVERSARY'],
}

def detect_rado_feature(title_upper):
    """素材・特徴を検出"""
    features = []
    for feature_name, keywords in RADO_FEATURES.items():
        for kw in keywords:
            if kw in title_upper:
                features.append(feature_name)
                break
    return ', '.join(features) if features else None

df_rado['素材・特徴'] = df_rado['タイトル_upper'].apply(detect_rado_feature)
df_rado['素材・特徴あり'] = df_rado['素材・特徴'].notna()

# 型番を抽出
df_rado['型番抽出'] = df_rado['タイトル'].apply(extract_model_number)

print(f"✓ 型番抽出完了: {df_rado['型番抽出'].notna().sum()}件")

# ライン別統計を計算
line_stats = {}
line_models_dict = {}

for line, group in df_rado.groupby('ライン'):
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
rado_brand = brand_detail['brands'].get('RADO', {
    'total_sales': int(df_rado['販売数'].sum()),
    'median_price': float(df_rado['価格'].median()),
    'cv': float(calculate_cv(df_rado['価格'].values)),
    'jdm_premium': 0.0,
    'model_stats': []
})

# 型番Top30を生成
all_models = []
model_group_all = df_rado[df_rado['型番抽出'].notna()].copy()
if len(model_group_all) > 0:
    for model, mg in model_group_all.groupby('型番抽出'):
        model_sales = mg['販売数'].sum()
        if model_sales >= 1:
            median = mg['価格'].median()
            all_models.append({
                'model': model,
                'count': int(model_sales),
                'median': float(median),
                'cv': float(calculate_cv(mg['価格'].values)),
                'breakeven': int(median * 155 * 0.65)
            })

all_models = sorted(all_models, key=lambda x: x['count'], reverse=True)[:30]

# CSSスタイル追加
additional_css = '''
<style>
.rado-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.rado-chart-container {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.rado-accent {
    color: #c77dff;
    font-weight: bold;
}

.rado-purple {
    color: #7b2cbf;
}

.model-sample {
    font-size: 0.85em;
    color: #666;
    font-style: italic;
}

@media (max-width: 768px) {
    .rado-grid {
        grid-template-columns: 1fr;
    }
}
</style>
'''

# 1. 基本統計カード
stats_html = f'''
    <div id="RADO" class="tab-content">
        <h2 class="section-title rado-purple">🟣 RADO 詳細分析</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{rado_brand['total_sales']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${rado_brand['median_price']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">{rado_brand['cv']:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">JDMプレミアム</div>
                <div class="value rado-accent">{rado_brand['jdm_premium']:+.1f}%</div>
            </div>
        </div>
'''

# 2. 仕入れ戦略
strategy_html = '''
        <div class="insight-box" style="border-left: 5px solid #c77dff;">
            <h3 class="rado-purple">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #7b2cbf;">
                    <h4 style="color: #7b2cbf; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li><strong class="rado-accent">DiaStar</strong>シリーズ（RADOの代表モデル）</li>
                        <li>型番が<strong>明確に記載</strong>されている商品</li>
                        <li><strong class="rado-accent">セラミック素材</strong>使用モデル（RADOの特徴）</li>
                        <li>ヴィンテージ商品で状態が良好なもの</li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #c77dff;">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>型番不明の「その他RADO」</li>
                        <li>状態不明・箱なし品</li>
                        <li>マイナーライン（販売実績が少ない）</li>
                        <li>修理歴不明のヴィンテージ品</li>
                    </ul>
                </div>
                <div style="background: #e1f5fe; padding: 15px; border-radius: 8px; border-left: 4px solid #0288d1;">
                    <h4 style="color: #0288d1; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> ¥25,000以下</p>
                    <p style="margin: 5px 0 0 0;"><strong class="rado-accent">DiaStar+セラミック:</strong> ¥35,000前後が上限</p>
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
    mask = (df_rado['価格'] >= price_bins[i]) & (df_rado['価格'] < price_bins[i+1])
    count = df_rado[mask]['販売数'].sum()
    price_distribution[bin_labels[i]] = int(count)

price_labels = list(price_distribution.keys())
price_values = list(price_distribution.values())

# 駆動方式分布を元CSVから計算
movement_dist_real = df_rado.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
movement_labels = [mv for mv in movement_dist_real.index if mv != '不明']
movement_values = [int(movement_dist_real[mv]) for mv in movement_labels]

# 性別分布を元CSVから計算
dept_dist_real = df_rado.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist_real.index if dept != '不明']
dept_values = [int(dept_dist_real[dept]) for dept in dept_labels]

# ライン別売上比率（上位7ライン + その他に集約）
line_sales = df_rado.groupby('ライン')['販売数'].sum().sort_values(ascending=False)
if len(line_sales) > 7:
    top_7_lines = line_sales.head(7)
    others_sum = line_sales.iloc[7:].sum()
    line_sales_final = pd.concat([top_7_lines, pd.Series({'その他': others_sum})])
else:
    line_sales_final = line_sales

line_labels = line_sales_final.index.tolist()
line_values = line_sales_final.values.tolist()

graphs_html = f'''
        <h3 class="section-title rado-purple">📊 市場分析グラフ</h3>
        <div class="rado-grid">
            <div class="rado-chart-container">
                <h4 class="rado-purple">価格帯別分析（50ドル刻み）</h4>
                <div id="rado_price_chart" style="height: 350px;"></div>
            </div>
            <div class="rado-chart-container">
                <h4 class="rado-purple">駆動方式別分布</h4>
                <div id="rado_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="rado-chart-container">
                <h4 class="rado-purple">性別・カテゴリー別分布</h4>
                <div id="rado_gender_chart" style="height: 300px;"></div>
            </div>
            <div class="rado-chart-container">
                <h4 class="rado-purple">ライン別売上比率</h4>
                <div id="rado_line_chart" style="height: 350px;"></div>
            </div>
        </div>
'''

# 6. ライン別分析（パーセンテージ追加）
total_line_sales = sum(data['count'] for data in line_stats.values())

lines_html = f'''
        <h3 class="section-title rado-purple">🔵 ライン別詳細分析（全{len(line_stats)}ライン）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th class="rado-accent">比率</th>
                        <th>中央値</th>
                        <th class="rado-accent">仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

for line_name, data in sorted(line_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    cv = data['cv']
    stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))
    line_ratio = data['count'] / total_line_sales * 100
    breakeven = int(data['median'] * 155 * 0.65)

    lines_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
                        <td class="rado-accent">{line_ratio:.1f}%</td>
                        <td>${data['median']:.0f}</td>
                        <td class="highlight rado-accent">¥{breakeven:,}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=RADO+{line_name.replace(' ', '+')}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=RADO%20{line_name.replace(' ', '%20')}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

lines_html += '''
                </tbody>
            </table>
        </div>
'''

# 6.5. 素材・ヴィンテージ分析（別視点）
feature_data = df_rado[df_rado['素材・特徴あり']==True].copy()
feature_sales = feature_data['販売数'].sum()
feature_median = feature_data['価格'].median() if len(feature_data) > 0 else 0

# 素材・特徴別集計
feature_breakdown = {}
for feature_name, keywords in RADO_FEATURES.items():
    count = 0
    prices = []
    for _, row in df_rado.iterrows():
        title_upper = row['タイトル_upper']
        for kw in keywords:
            if kw in title_upper:
                count += row['販売数']
                prices.append(row['価格'])
                break

    if count > 0:
        median_price = np.median(prices)
        feature_breakdown[feature_name] = {
            'count': int(count),
            'median': float(median_price),
            'breakeven': int(median_price * 155 * 0.65)
        }

feature_html = f'''
        <h3 class="section-title rado-purple">🎭 素材・ヴィンテージ分析（複数視点）</h3>
        <p style="color: #666; margin-bottom: 15px;">同じ商品を別の角度から分析 - 例：DiaStar Ceramicは「DiaStarライン」と「Ceramic素材」の両方に該当</p>

        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="label">特徴商品数</div>
                <div class="value rado-accent">{feature_sales:,}個</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${feature_median:.0f}</div>
            </div>
            <div class="stat-card">
                <div class="label">全体比率</div>
                <div class="value rado-accent">{feature_sales/total_line_sales*100:.1f}%</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>素材・特徴</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>中央値</th>
                        <th class="rado-accent">仕入上限(¥)</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

for feature_name, data in sorted(feature_breakdown.items(), key=lambda x: x[1]['count'], reverse=True):
    count = data['count']
    median = data['median']
    breakeven = data['breakeven']
    ratio = count / feature_sales * 100 if feature_sales > 0 else 0
    feature_html += f'''
                    <tr>
                        <td><strong>{feature_name}</strong></td>
                        <td>{count:,}</td>
                        <td class="rado-accent">{ratio:.1f}%</td>
                        <td>${median:.0f}</td>
                        <td class="highlight rado-accent">¥{breakeven:,}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=RADO+{feature_name.replace(' ', '+')}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=RADO%20{feature_name.replace(' ', '%20')}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
                        </td>
                    </tr>
    '''

feature_html += '''
                </tbody>
            </table>
        </div>
'''

# 7. 各ラインの人気モデル（CSVから再分類）
line_models_html = '<h3 class="section-title rado-purple">📌 各ラインの人気モデル（実データより）Top15</h3>'
line_models_html += '<p style="color: #666; margin-bottom: 20px;">元CSVデータから再分類した正確な人気モデルTop15</p>'

for line_name in sorted(line_stats.keys(), key=lambda x: line_stats[x]['count'], reverse=True):
    models = line_models_dict.get(line_name, [])[:15]

    if not models:
        continue

    line_models_html += f'''
        <h4 style="color: #7b2cbf; margin-top: 25px; border-bottom: 2px solid #7b2cbf; padding-bottom: 5px;">
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
                        <th class="rado-accent">仕入上限(¥)</th>
                        <th>CV値</th>
                        <th>商品例</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, model in enumerate(models, 1):
        model_breakeven = int(model['median'] * 155 * 0.65)
        line_models_html += f'''
                    <tr>
                        <td><strong class="rado-accent">{i}</strong></td>
                        <td><strong>{model['model']}</strong></td>
                        <td>{model['count']}</td>
                        <td>${model['median']:.0f}</td>
                        <td class="highlight rado-accent">¥{model_breakeven:,}</td>
                        <td>{model['cv']:.3f}</td>
                        <td class="model-sample">{model.get('title_sample', '')}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=RADO+{model['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=RADO%20{model['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
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
        <h3 class="section-title rado-purple">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th class="rado-accent">仕入上限(¥)</th>
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
                        <td><strong class="rado-accent">{i}</strong></td>
                        <td>{model_name}</td>
                        <td>{count}</td>
                        <td>${median:.2f}</td>
                        <td class="highlight rado-accent">¥{breakeven:,.0f}</td>
                        <td>{cv:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=RADO+{model_name}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="https://jp.mercari.com/search?keyword=RADO%20{model_name}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">
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
        const radoPurple = '#7b2cbf';
        const radoAccent = '#c77dff';
        const radoGradient = ['#7b2cbf', '#9d4edd', '#c77dff', '#e0aaff', '#f0d9ff'];

        Plotly.newPlot('rado_price_chart', [{{
            x: {price_labels},
            y: {price_values},
            type: 'bar',
            marker: {{
                color: radoPurple,
                line: {{color: radoAccent, width: 1}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('rado_movement_chart', [{{
            labels: {movement_labels},
            values: {movement_values},
            type: 'pie',
            marker: {{colors: radoGradient}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('rado_gender_chart', [{{
            labels: {dept_labels},
            values: {dept_values},
            type: 'pie',
            marker: {{colors: [radoPurple, radoAccent, '#e0aaff', '#f0d9ff', '#dda0dd']}},
            textinfo: 'label+percent',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('rado_line_chart', [{{
            labels: {json.dumps(line_labels, ensure_ascii=False)},
            values: {json.dumps(line_values, ensure_ascii=False)},
            type: 'pie',
            marker: {{colors: radoGradient.concat(['#e0aaff', '#f0d9ff', '#dda0dd', '#d8bfd8', '#E6E6E6'])}},
            textinfo: 'label+percent',
            textposition: 'outside',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
'''

# 完全なRADOタブHTMLを構築
new_rado_tab = (
    additional_css +
    stats_html +
    strategy_html +
    graphs_html +
    lines_html +
    feature_html +  # ← 素材・ヴィンテージ分析追加
    line_models_html +
    top30_html +
    '    </div>\n' +
    graph_js
)

# 既存のRADOタブを置換（ネストカウント方式）
def find_tab_position(html, brand_name):
    """タブ位置をネストカウントで特定"""
    tab_start_tag = f'<div id="{brand_name}" class="tab-content">'
    tab_start = html.find(tab_start_tag)

    if tab_start == -1:
        raise ValueError(f"{brand_name}タブが見つかりません")

    # ネストカウント
    div_count = 1
    search_pos = tab_start + len(tab_start_tag)

    while div_count > 0 and search_pos < len(html):
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            raise ValueError(f"{brand_name}タブの閉じタグが見つかりません")

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                return (tab_start, next_close + 6)
            search_pos = next_close + 6

start_pos, end_pos = find_tab_position(html, 'RADO')
html = html[:start_pos] + new_rado_tab + html[end_pos:]

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html.encode('utf-8'))
print(f"\n✅ RADOタブ v3 完全版完成！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"🎯 改善内容:")
print(f"  ✓ 元CSVから正確にライン分類")
print(f"  ✓ {len(line_stats)}ラインを認識（DiaStar、Florence、Golden Horse等）")
print(f"  ✓ 各ラインの実際の人気モデルTop15を抽出")
print(f"  ✓ 素材・ヴィンテージ分析を追加（RADOの価値軸）")
print(f"  ✓ 商品タイトルサンプルを表示")
print(f"  ✓ 全セクションに検索リンク + チェックボックス追加")
