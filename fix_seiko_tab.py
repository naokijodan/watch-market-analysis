#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブにライン別詳細分析を追加するスクリプト
"""

import json
import re

print("📄 SEIKOタブ修正開始...")

# HTMLを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 深掘りJSONを読み込み
with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

# ブランド詳細JSONも読み込み（人気モデルTop30用）
with open('/Users/naokijodan/Desktop/ブランド詳細分析.json', 'r', encoding='utf-8') as f:
    brand_detail = json.load(f)

# SEIKOライン別分析HTMLを生成
seiko_lines = deepdive['seiko_lines']

lines_html = '''
        <h3 class="section-title">🔵 ライン別詳細分析</h3>
        <p style="margin-bottom: 20px;">SEIKOの各ラインの市場動向を分析</p>

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

        <h4 class="section-title" style="margin-top: 30px;">各ラインの人気モデル</h4>
'''

# 各ラインの人気モデルTop5を表示
for line_name, data in sorted(seiko_lines.items(), key=lambda x: x[1]['count'], reverse=True):
    if not data.get('top_models'):
        continue

    lines_html += f'''
        <h5 style="color: #667eea; margin-top: 20px;">{line_name}</h5>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for model in data['top_models']:
        lines_html += f'''
                    <tr>
                        <td><strong>{model['model']}</strong></td>
                        <td>{model['count']}</td>
                        <td>${model['median']:.0f}</td>
                        <td>{model['cv']:.3f}</td>
                        <td>
                            <a href="https://www.ebay.com/sch/i.html?_nkw=SEIKO+{model['model']}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="https://jp.mercari.com/search?keyword=SEIKO%20{model['model']}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        </td>
                    </tr>
        '''

    lines_html += '''
                </tbody>
            </table>
        </div>
    '''

# 人気モデルTop30を生成
seiko_brand_data = brand_detail.get('SEIKO', {})
top_models = seiko_brand_data.get('model_stats', [])[:30]

top30_html = '''
        <h3 class="section-title">🏆 全ライン横断 人気モデルTop30</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値($)</th>
                        <th>仕入上限</th>
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

# SEIKOタブの「人気モデルTop10」セクションを探して、その直後に挿入
pattern = r'(<h3 class="section-title">🏆 人気モデルTop10</h3>.*?</tbody>\s*</table>\s*</div>)'
replacement = top30_html + '\n\n' + lines_html

html = re.sub(pattern, replacement, html, flags=re.DOTALL, count=1)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

file_size = len(html.encode('utf-8'))
print(f"✅ SEIKOタブ修正完了！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"📊 追加内容:")
print(f"  - ライン別分析: {len(seiko_lines)}ライン")
print(f"  - 人気モデル: Top30に拡張")
print(f"  - 各ラインの人気モデル表示")
