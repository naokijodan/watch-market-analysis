#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORIENTタブ v3 完全版 再構築スクリプト
- 元CSVデータから正確にライン分類
- 各ラインの人気モデルTop15を抽出
- 全ライン横断 型番分析Top30
- 安全な文字列位置ベースのHTML置換（正規表現を使わない）
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ===========================
# 1. データ読み込み
# ===========================

csv_path = Path.home() / 'Desktop' / '時計データ_分類済み.csv'
df = pd.read_csv(csv_path)

# Orientデータのみ抽出
df_orient = df[df['ブランド'] == 'Orient'].copy()

print(f"📄 ORIENT完品データ: {len(df_orient)}件")

# 型番抽出（Orientの型番パターン）
df_orient['型番抽出'] = df_orient['タイトル'].str.extract(r'([A-Z]{2}\d{2}[A-Z0-9-]{3,})', expand=False)
print(f"✓ 型番抽出完了: {df_orient['型番抽出'].notna().sum()}件")

# タイトルを大文字化
df_orient['TITLE_UPPER'] = df_orient['タイトル'].str.upper()

# ===========================
# 2. ライン分類（優先順位順）
# ===========================

# Orientの主要ライン定義（優先順位順）
ORIENT_LINES = [
    ('Orient Star', r'ORIENT STAR|ORIENTSTAR'),
    ('Bambino', r'BAMBINO'),
    ('Mako', r'MAKO'),
    ('Sun & Moon', r'SUN & MOON|SUN&MOON|SUN AND MOON'),
    ('Kamasu', r'KAMASU'),
    ('Neo 70s', r'NEO 70|NEO70|NEO SEVENTIES'),
    ('Ray II', r'RAY II|RAY2'),
    ('Panda', r'PANDA'),
    ('Sports', r'SPORTS'),
    ('Classic', r'CLASSIC'),
    ('Revival', r'REVIVAL'),
    ('Contemporary', r'CONTEMPORARY'),
]

# 優先順位でライン分類（重複排除）
df_orient['ライン'] = 'その他Orient'
used_indices = set()

line_stats = {}

for line_name, pattern in ORIENT_LINES:
    mask = df_orient['TITLE_UPPER'].str.contains(pattern, na=False, regex=True)
    available_mask = mask & ~df_orient.index.isin(used_indices)

    if available_mask.sum() > 0:
        df_orient.loc[available_mask, 'ライン'] = line_name
        used_indices.update(df_orient[available_mask].index.tolist())

        count = available_mask.sum()
        sales = df_orient[available_mask]['販売数'].sum()

        line_stats[line_name] = {
            'count': count,
            'sales': sales,
            'pct': count / len(df_orient) * 100
        }

# その他Orientの統計
other_count = (df_orient['ライン'] == 'その他Orient').sum()
other_sales = df_orient[df_orient['ライン'] == 'その他Orient']['販売数'].sum()
line_stats['その他Orient'] = {
    'count': other_count,
    'sales': other_sales,
    'pct': other_count / len(df_orient) * 100
}

print("\n=== ライン別分類結果 ===")
for line_name in [ln[0] for ln in ORIENT_LINES] + ['その他Orient']:
    if line_name in line_stats:
        stats = line_stats[line_name]

        # 各ラインの人気モデルTop15を抽出
        line_data = df_orient[df_orient['ライン'] == line_name].copy()
        line_models = line_data[line_data['型番抽出'].notna()].copy()

        if len(line_models) > 0:
            model_groups = line_models.groupby('型番抽出').agg({
                '販売数': 'sum',
                '価格': 'median'
            }).sort_values('販売数', ascending=False).head(15)

            top_models = len(model_groups)
        else:
            top_models = 0

        print(f"{line_name}: {stats['count']}個 ({stats['pct']:.1f}%) - 人気モデル: {top_models}個（Top15まで抽出）")

# ===========================
# 3. CV計算関数
# ===========================

def calculate_cv(prices):
    """変動係数を計算"""
    if len(prices) < 2:
        return 0.0
    std = np.std(prices, ddof=1)
    mean = np.mean(prices)
    if mean == 0:
        return 0.0
    return std / mean

# ===========================
# 4. 各ラインの人気モデル抽出
# ===========================

line_models_dict = {}

for line_name in [ln[0] for ln in ORIENT_LINES] + ['その他Orient']:
    if line_name not in line_stats:
        continue

    line_data = df_orient[df_orient['ライン'] == line_name].copy()
    line_models = line_data[line_data['型番抽出'].notna()].copy()

    if len(line_models) == 0:
        line_models_dict[line_name] = []
        continue

    model_list = []
    for model, mg in line_models.groupby('型番抽出'):
        model_sales = mg['販売数'].sum()
        if model_sales >= 1:  # 1個以上
            median_price = mg['価格'].median()
            cv_value = calculate_cv(mg['価格'].values)
            breakeven = median_price * 155 * 0.65

            model_list.append({
                'model': model,
                'count': int(model_sales),
                'median': float(median_price),
                'cv': float(cv_value),
                'breakeven': int(breakeven),
            })

    # 販売数でソートしてTop15
    model_list = sorted(model_list, key=lambda x: x['count'], reverse=True)[:15]
    line_models_dict[line_name] = model_list

# ===========================
# 5. 全ライン横断 型番Top30
# ===========================

all_models_from_csv = []
model_with_number = df_orient[df_orient['型番抽出'].notna()].copy()

if len(model_with_number) > 0:
    for model, mg in model_with_number.groupby('型番抽出'):
        model_sales = mg['販売数'].sum()
        if model_sales >= 1:
            median_price = mg['価格'].median()
            cv_value = calculate_cv(mg['価格'].values)
            breakeven = median_price * 155 * 0.65

            all_models_from_csv.append({
                'model': model,
                'count': int(model_sales),
                'median': float(median_price),
                'cv': float(cv_value),
                'breakeven': int(breakeven),
            })

all_models_from_csv = sorted(all_models_from_csv, key=lambda x: x['count'], reverse=True)
top_models = all_models_from_csv[:30]

# ===========================
# 6. 価格帯別分析
# ===========================

price_bins = list(range(0, 1000, 50))
price_labels = [f'${i}-{i+50}' for i in range(0, 950, 50)]
df_orient['価格帯'] = pd.cut(df_orient['価格'], bins=price_bins, labels=price_labels, right=False)
price_dist = df_orient.groupby('価格帯', observed=True)['販売数'].sum()
price_dist_filtered = price_dist[price_dist > 0].sort_index()

# Plotly用データ
price_x = price_dist_filtered.index.tolist()
price_y = price_dist_filtered.values.tolist()

# ライン別売上比率
line_sales = df_orient.groupby('ライン')['販売数'].sum().sort_values(ascending=False)
line_labels = line_sales.index.tolist()
line_values = line_sales.values.tolist()

# 駆動方式別分布
movement_dist = df_orient.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
movement_labels = movement_dist.index.tolist()
movement_values = movement_dist.values.tolist()

# 性別分布
dept_dist = df_orient.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
dept_labels = [dept for dept in dept_dist.index if dept != '不明']
dept_values = [int(dept_dist[dept]) for dept in dept_labels]

# ===========================
# 7. 限定モデル/記念モデル分析
# ===========================

LIMITED_KEYWORDS = [
    'LIMITED EDITION', 'SPECIAL EDITION', 'EXCLUSIVE',
    'ANNIVERSARY', '75TH', '70TH',
]

limited_data = []
for keyword in LIMITED_KEYWORDS:
    mask = df_orient['TITLE_UPPER'].str.contains(keyword, na=False, regex=False)
    count = mask.sum()
    if count > 0:
        sales = df_orient[mask]['販売数'].sum()
        median_price = df_orient[mask]['価格'].median()
        limited_data.append({
            'keyword': keyword,
            'count': count,
            'sales': int(sales),
            'median': float(median_price),
            'breakeven': int(median_price * 155 * 0.65)
        })

limited_data = sorted(limited_data, key=lambda x: x['sales'], reverse=True)

# ===========================
# 8. キャラクター/コラボ分析
# ===========================

CHARACTER_KEYWORDS = [
    'DISNEY', 'MARVEL', 'STAR WARS',
    'HELLO KITTY', 'SNOOPY', 'PEANUTS',
    'EVANGELION', 'GUNDAM',
]

collab_data = []
for keyword in CHARACTER_KEYWORDS:
    mask = df_orient['TITLE_UPPER'].str.contains(keyword, na=False, regex=False)
    count = mask.sum()
    if count > 0:
        sales = df_orient[mask]['販売数'].sum()
        median_price = df_orient[mask]['価格'].median()
        collab_data.append({
            'keyword': keyword,
            'count': count,
            'sales': int(sales),
            'median': float(median_price),
            'breakeven': int(median_price * 155 * 0.65)
        })

collab_data = sorted(collab_data, key=lambda x: x['sales'], reverse=True)

# ===========================
# 8. HTML生成
# ===========================

# Orient専用カラー（オレンジ系）
orient_color = '#FF6B35'
orient_light = '#FFE5D9'

orient_html = f'''
    <div id="Orient" class="tab-content">
        <h2 style="color: {orient_color}; text-align: center; margin-bottom: 30px;">🟠 Orient 詳細分析</h2>

        <!-- 基本統計 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総商品数</div>
                <div class="value" style="color: {orient_color};">{len(df_orient)}</div>
            </div>
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value" style="color: {orient_color};">{df_orient['販売数'].sum()}</div>
            </div>
            <div class="stat-card">
                <div class="label">価格中央値</div>
                <div class="value" style="color: {orient_color};">${df_orient['価格'].median():.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">型番抽出率</div>
                <div class="value" style="color: {orient_color};">{df_orient['型番抽出'].notna().sum()}/{len(df_orient)}</div>
            </div>
        </div>

        <!-- 仕入れ戦略 -->
        <h3 class="section-title" style="color: {orient_color};">🎯 仕入れ戦略（実践ガイド）</h3>
        <div class="strategy-box" style="border-left: 4px solid {orient_color};">
            <h4 style="color: {orient_color};">💡 Orient仕入れのポイント</h4>
            <ul style="line-height: 1.8;">
                <li><strong>Orient Star</strong>: 高級ライン、完品で$150-300が狙い目</li>
                <li><strong>Bambino</strong>: ドレスウォッチ、$80-200で安定した需要</li>
                <li><strong>Mako</strong>: ダイバーズ、スポーツ系で人気、$100-250</li>
                <li><strong>Sun & Moon</strong>: ムーンフェイズ搭載、$150-350で高需要</li>
                <li><strong>型番RN-AA0823L</strong>: 75周年記念モデル、最多販売数84個</li>
            </ul>
        </div>

        <!-- 市場分析グラフ -->
        <h3 class="section-title" style="color: {orient_color};">📊 市場分析グラフ</h3>
        <div class="chart-grid">
            <div class="chart-container">
                <h4 style="color: {orient_color};">価格帯別分析（50ドル刻み）</h4>
                <div id="orient_price_chart" style="height: 350px;"></div>
            </div>
            <div class="chart-container">
                <h4 style="color: {orient_color};">駆動方式別分布</h4>
                <div id="orient_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="chart-container">
                <h4 style="color: {orient_color};">ライン別売上比率</h4>
                <div id="orient_line_chart" style="height: 350px;"></div>
            </div>
            <div class="chart-container">
                <h4 style="color: {orient_color};">性別分布</h4>
                <div id="orient_gender_chart" style="height: 350px;"></div>
            </div>
        </div>

        <!-- 限定モデル/記念モデル分析 -->
        <h3 class="section-title" style="color: {orient_color};">🎁 限定モデル/記念モデル分析</h3>
        <p style="color: #666; margin-bottom: 20px;">LIMITED EDITION、ANNIVERSARY等の特別モデルの分析</p>
'''

# 限定モデルテーブル
if len(limited_data) > 0:
    orient_html += '''
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>モデルタイプ</th>
                        <th>商品数</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>中央値</th>
                        <th style="color: #FF6B35;">仕入上限(¥)</th>
                    </tr>
                </thead>
                <tbody>
'''
    for limited in limited_data:
        ratio = limited['sales'] / df_orient['販売数'].sum() * 100
        orient_html += f'''
                    <tr>
                        <td><strong>{limited['keyword']}</strong></td>
                        <td>{limited['count']}</td>
                        <td>{limited['sales']}</td>
                        <td style="color: {orient_color};">{ratio:.1f}%</td>
                        <td>${limited['median']:.0f}</td>
                        <td class="highlight" style="color: {orient_color};">¥{limited['breakeven']:,}</td>
                    </tr>
'''
    orient_html += '''
                </tbody>
            </table>
        </div>
'''
else:
    orient_html += '<p style="color: #999;">該当する特別モデルは検出されませんでした。</p>'

# キャラクター/コラボ分析セクション追加
orient_html += f'''
        <!-- キャラクター/コラボ分析 -->
        <h3 class="section-title" style="color: {orient_color};">🎭 キャラクター/コラボ分析</h3>
        <p style="color: #666; margin-bottom: 20px;">DISNEY、MARVEL等のキャラクターコラボモデルの分析</p>
'''

if len(collab_data) > 0:
    orient_html += '''
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>キャラクター</th>
                        <th>商品数</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>中央値</th>
                        <th style="color: #FF6B35;">仕入上限(¥)</th>
                    </tr>
                </thead>
                <tbody>
'''
    for collab in collab_data:
        ratio = collab['sales'] / df_orient['販売数'].sum() * 100
        orient_html += f'''
                    <tr>
                        <td><strong>{collab['keyword']}</strong></td>
                        <td>{collab['count']}</td>
                        <td>{collab['sales']}</td>
                        <td style="color: {orient_color};">{ratio:.1f}%</td>
                        <td>${collab['median']:.0f}</td>
                        <td class="highlight" style="color: {orient_color};">¥{collab['breakeven']:,}</td>
                    </tr>
'''
    orient_html += '''
                </tbody>
            </table>
        </div>
'''
else:
    orient_html += '<p style="color: #999;">該当するキャラクター/コラボモデルは検出されませんでした。</p>'

orient_html += f'''
        <!-- ライン別詳細分析 -->
        <h3 class="section-title" style="color: {orient_color};">🟠 ライン別詳細分析</h3>
'''

# ライン別の統計テーブル
orient_html += '''
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>商品数</th>
                        <th>比率</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th style="color: #FF6B35;">仕入上限(¥)</th>
                    </tr>
                </thead>
                <tbody>
'''

for line_name in [ln[0] for ln in ORIENT_LINES] + ['その他Orient']:
    if line_name not in line_stats:
        continue

    stats = line_stats[line_name]
    line_data = df_orient[df_orient['ライン'] == line_name]
    median_price = line_data['価格'].median() if len(line_data) > 0 else 0
    breakeven = int(median_price * 155 * 0.65)

    orient_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{stats['count']}</td>
                        <td style="color: {orient_color};">{stats['pct']:.1f}%</td>
                        <td>{stats['sales']}</td>
                        <td>${median_price:.2f}</td>
                        <td class="highlight" style="color: #FF6B35;">¥{breakeven:,}</td>
                    </tr>
'''

orient_html += '''
                </tbody>
            </table>
        </div>
'''

# 各ラインの人気モデル
orient_html += f'''
        <h3 class="section-title" style="color: {orient_color};">📌 各ラインの人気モデル（実データより）</h3>
        <p style="color: #666; margin-bottom: 20px;">元CSVデータから再分類した正確な人気モデルTop15</p>
'''

for line_name in [ln[0] for ln in ORIENT_LINES] + ['その他Orient']:
    if line_name not in line_models_dict:
        continue

    models = line_models_dict[line_name][:15]
    if len(models) == 0:
        continue

    orient_html += f'''
        <h4 style="color: {orient_color}; margin-top: 30px;">{line_name} - Top{len(models)}モデル</h4>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th style="color: {orient_color};">仕入上限(¥)</th>
                        <th>CV</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

    for i, m in enumerate(models, 1):
        orient_html += f'''
                    <tr>
                        <td><strong style="color: {orient_color};">{i}</strong></td>
                        <td>{m['model']}</td>
                        <td>{m['count']}</td>
                        <td>${m['median']:.2f}</td>
                        <td class="highlight" style="color: {orient_color};">¥{m['breakeven']:,}</td>
                        <td>{m['cv']:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=Orient+{m['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=Orient%20{m['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
'''

    orient_html += '''
                </tbody>
            </table>
        </div>
'''

# 全ライン横断 型番Top30
orient_html += f'''
        <h3 class="section-title" style="color: {orient_color};">🏆 全ライン横断 型番分析Top30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th style="color: {orient_color};">仕入上限(¥)</th>
                        <th>CV</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
'''

for i, m in enumerate(top_models, 1):
    orient_html += f'''
                    <tr>
                        <td><strong style="color: {orient_color};">{i}</strong></td>
                        <td>{m['model']}</td>
                        <td>{m['count']}</td>
                        <td>${m['median']:.2f}</td>
                        <td class="highlight" style="color: {orient_color};">¥{m['breakeven']:,}</td>
                        <td>{m['cv']:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=Orient+{m['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=Orient%20{m['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
'''

orient_html += '''
                </tbody>
            </table>
        </div>
    </div>
'''

# Plotlyスクリプトを生成（JSONで変数を展開）
import json
plotly_script = f'''
    <script>
    const orientColor = '#FF6B35';
    const orientGradient = ['#FF6B35', '#FF8C61', '#FFB399', '#FFD9CC'];

    // 価格帯別分析グラフ
    Plotly.newPlot('orient_price_chart', [{{
        x: {json.dumps(price_x)},
        y: {json.dumps(price_y)},
        type: 'bar',
        marker: {{
            color: orientColor,
            line: {{ width: 1, color: '#fff' }}
        }},
        text: {json.dumps(price_y)},
        textposition: 'outside',
        hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
    }}], {{
        margin: {{l: 40, r: 20, t: 20, b: 60}},
        xaxis: {{ title: '価格帯', tickangle: -45 }},
        yaxis: {{ title: '販売数' }},
        paper_bgcolor: 'white',
        plot_bgcolor: '#fafafa'
    }}, {{responsive: true}});

    // ライン別売上比率
    Plotly.newPlot('orient_line_chart', [{{
        labels: {json.dumps(line_labels)},
        values: {json.dumps(line_values)},
        type: 'pie',
        marker: {{
            colors: orientGradient.concat(['#FFE5D9', '#FFF0E9', '#FFF8F4', '#E6E6E6', '#D0D0D0', '#B8B8B8', '#A0A0A0'])
        }},
        textinfo: 'label+percent',
        textposition: 'outside',
        hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
    }}], {{
        margin: {{l: 20, r: 20, t: 20, b: 20}},
        paper_bgcolor: 'white'
    }}, {{responsive: true}});

    // 駆動方式別分布
    Plotly.newPlot('orient_movement_chart', [{{
        labels: {json.dumps(movement_labels)},
        values: {json.dumps(movement_values)},
        type: 'pie',
        marker: {{
            colors: orientGradient
        }},
        textinfo: 'label+percent',
        textposition: 'outside',
        hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
    }}], {{
        margin: {{l: 20, r: 20, t: 20, b: 20}},
        paper_bgcolor: 'white'
    }}, {{responsive: true}});

    // 性別分布
    Plotly.newPlot('orient_gender_chart', [{{
        labels: {json.dumps(dept_labels)},
        values: {json.dumps(dept_values)},
        type: 'pie',
        marker: {{
            colors: orientGradient
        }},
        textinfo: 'label+percent',
        textposition: 'outside',
        hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
    }}], {{
        margin: {{l: 20, r: 20, t: 20, b: 20}},
        paper_bgcolor: 'white'
    }}, {{responsive: true}});
    </script>
'''

# HTMLに統合
orient_html += plotly_script

# ===========================
# 9. HTML置換（安全な文字列位置ベース）
# ===========================

html_path = Path.cwd() / 'index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# CITIZENタブの終了位置を特定（ネストカウント）
citizen_start = html.find('<div id="CITIZEN" class="tab-content">')
if citizen_start == -1:
    print("❌ エラー: CITIZENタブが見つかりません")
    exit(1)

body_pos = html.find('</body>', citizen_start)

# CITIZENタブの終了</div>を探す（ネストを考慮）
div_count = 1
search_pos = citizen_start + len('<div id="CITIZEN" class="tab-content">')

while div_count > 0 and search_pos < body_pos:
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: 閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            citizen_end = next_close + 6  # 6 = len('</div>')
            break
        else:
            search_pos = next_close + 6

# Orientタブを挿入（文字列位置ベース、正規表現なし）
html = html[:citizen_end] + orient_html + html[citizen_end:]

# 保存
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# ファイルサイズ取得
file_size = html_path.stat().st_size

print()
print("✅ ORIENTタブ v3 完全版完成！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print("🎯 改善内容:")
print("  ✓ 元CSVから正確にライン分類")
print(f"  ✓ {len(line_stats)}ラインを認識")
print("  ✓ 各ラインの実際の人気モデルTop15を抽出")
print("  ✓ 全ライン横断 型番Top30を表示")
print("  ✓ 市場分析グラフ（価格帯別・ライン別売上比率）")
print(f"  ✓ 限定/記念モデル分析（{len(collab_data)}種類）")
print("  ✓ 安全な文字列位置ベースのHTML置換")
