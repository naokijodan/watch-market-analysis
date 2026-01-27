#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブを完全再構築するスクリプト
"""

import json
import re

print("📄 SEIKOタブ完全再構築開始...")

# データを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

with open('/Users/naokijodan/Desktop/時計分析_完全版.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# SEIKOデータ抽出
seiko_brand = brand_detail['brands']['SEIKO']
seiko_lines = deepdive['seiko_lines']

# 1. 基本統計カード（既存維持）
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

# 2. 仕入れ戦略（改善版）
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

# 3. タイプ別分析（価格帯セグメント）
price_segments = seiko_brand.get('price_segments', {})
type_html = f'''
        <h3 class="section-title">📊 価格帯別分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>価格帯</th>
                        <th>商品数</th>
                        <th>比率</th>
                        <th>特徴</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>エントリー ($0-300)</strong></td>
                        <td>{price_segments.get('エントリー', 0):,}</td>
                        <td>{price_segments.get('エントリー', 0) / seiko_brand['total_records'] * 100:.1f}%</td>
                        <td>SEIKO 5、クォーツモデル中心</td>
                    </tr>
                    <tr>
                        <td><strong>ミドル ($300-600)</strong></td>
                        <td>{price_segments.get('ミドル', 0):,}</td>
                        <td>{price_segments.get('ミドル', 0) / seiko_brand['total_records'] * 100:.1f}%</td>
                        <td>Prospex、Presage、自動巻</td>
                    </tr>
                    <tr>
                        <td><strong>ハイエンド ($600+)</strong></td>
                        <td>{price_segments.get('ハイエンド', 0):,}</td>
                        <td>{price_segments.get('ハイエンド', 0) / seiko_brand['total_records'] * 100:.1f}%</td>
                        <td>Grand Seiko、限定モデル</td>
                    </tr>
                </tbody>
            </table>
        </div>
'''

# 4. 駆動方式別分析
movement_dist = seiko_brand.get('movement_distribution', {})
sorted_movements = sorted(movement_dist.items(), key=lambda x: x[1], reverse=True)

movement_html = '''
        <h3 class="section-title">⚙️ 駆動方式別分析</h3>
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

for movement, count in sorted_movements:
    if movement == '不明':
        continue
    ratio = count / seiko_brand['total_records'] * 100

    # 市場評価コメント
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

# 5. 性別分析
department_dist = seiko_brand.get('department_distribution', {})
sorted_depts = sorted(department_dist.items(), key=lambda x: x[1], reverse=True)

gender_html = '''
        <h3 class="section-title">👥 性別・カテゴリー別分析</h3>
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

for dept, count in sorted_depts:
    if dept == '不明':
        continue
    ratio = count / seiko_brand['total_records'] * 100

    # 市場特性コメント
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

# 6. ライン別分析
lines_html = '''
        <h3 class="section-title">🔵 ライン別詳細分析</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
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

    lines_html += f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{data['count']:,}</td>
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

# 7. ラインごとのモデル別分析
line_models_html = '<h3 class="section-title">📌 各ラインの人気モデル</h3>'

for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    if not data.get('top_models'):
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

    for i, model in enumerate(data['top_models'], 1):
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
top_models = seiko_brand.get('model_stats', [])[:30]

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
    </div>
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
    top30_html
)

# 既存のSEIKOタブを置換
pattern = r'<div id="SEIKO" class="tab-content">.*?</div>\s*(?=<div id="|</div>\s*<script>)'
html = re.sub(pattern, new_seiko_tab, html, flags=re.DOTALL, count=1)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html.encode('utf-8'))
print(f"✅ SEIKOタブ完全再構築完了！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"📊 新構成:")
print(f"  1. 仕入れ戦略（改善）")
print(f"  2. 価格帯別分析")
print(f"  3. 駆動方式別分析（{len(movement_dist)}種）")
print(f"  4. 性別別分析（{len(department_dist)}種）")
print(f"  5. ライン別分析（{len(seiko_lines)}ライン）")
print(f"  6. 各ラインの人気モデル")
print(f"  7. 型番分析Top30")
