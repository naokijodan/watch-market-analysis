#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3 HTMLにライン別詳細分析を統合するスクリプト
"""

import json
import re

print("📄 v3 HTML拡張処理開始...")

# v3 HTMLを読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 深掘りJSONを読み込み
with open('時計分析_深掘り版.json', 'r', encoding='utf-8') as f:
    deepdive = json.load(f)

# アコーディオン用CSSを追加
accordion_css = '''
.accordion {
    background: #f8f9fa;
    cursor: pointer;
    padding: 18px;
    width: 100%;
    border: none;
    text-align: left;
    outline: none;
    font-size: 1.1em;
    font-weight: bold;
    transition: 0.3s;
    border-radius: 10px;
    margin: 5px 0;
    color: #667eea;
}

.accordion:hover {
    background: #e9ecef;
}

.accordion.active {
    background: #667eea;
    color: white;
}

.panel {
    padding: 0 18px;
    background: white;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
}

.panel.active {
    max-height: 2000px;
    padding: 18px;
}

.line-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 10px;
}

.line-nav a {
    padding: 8px 15px;
    background: white;
    border: 2px solid #667eea;
    border-radius: 5px;
    text-decoration: none;
    color: #667eea;
    font-weight: bold;
    transition: all 0.3s;
}

.line-nav a:hover {
    background: #667eea;
    color: white;
}

.gshock-special {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
    border: 3px solid #ff6b6b;
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
}

.gshock-special .accordion {
    background: #fff;
    color: #ff6b6b;
}

.gshock-special .accordion:hover {
    background: #ffe5e5;
}

.gshock-special .accordion.active {
    background: #ff6b6b;
    color: white;
}
'''

# CSSを</style>の前に挿入
html_content = html_content.replace('</style>', accordion_css + '\n</style>')

# アコーディオンJavaScript関数を追加
accordion_js = '''
function toggleAccordion(element) {
    element.classList.toggle("active");
    var panel = element.nextElementSibling;
    panel.classList.toggle("active");
}
'''

# JavaScriptを</script>の前に挿入（最後のscriptタグ）
html_content = re.sub(r'(</script>\s*</body>)', accordion_js + '\\1', html_content)

# SEIKO/CASIO/CITIZENのライン別詳細HTMLを生成
def generate_line_analysis_html(brand_name, lines_data, is_gshock_special=False):
    """ライン別詳細HTMLを生成"""

    # ライン別データを販売数でソート
    sorted_lines = sorted(lines_data.items(), key=lambda x: x[1]['count'], reverse=True)

    # ナビゲーション生成
    nav_html = '<div class="line-nav">'
    for line_name, _ in sorted_lines:
        safe_id = line_name.replace(' ', '_').replace('-', '_')
        nav_html += f'<a href="#line_{brand_name}_{safe_id}">{line_name}</a>'
    nav_html += '</div>'

    # 各ラインのアコーディオン生成
    accordions_html = ''

    for line_name, data in sorted_lines:
        safe_id = line_name.replace(' ', '_').replace('-', '_')

        # CV値バッジ
        cv = data['cv']
        cv_badge = 'badge-low' if cv <= 0.3 else ('badge-medium' if cv <= 0.5 else 'badge-high')

        # 安定度
        stability = '★★★' if cv <= 0.15 else ('★★☆' if cv <= 0.25 else ('★☆☆' if cv <= 0.30 else '☆☆☆'))

        # JDM/Eco-Drive情報
        extra_info = ''
        if 'jdm_premium' in data:
            jdm_ratio = f"{data['jdm_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'
            extra_info += f"<p><strong>JDM比率:</strong> {jdm_ratio} | <strong>JDMプレミアム:</strong> {data['jdm_premium']:+.1f}%</p>"

        if 'eco_drive_premium' in data:
            eco_ratio = f"{data['eco_drive_count'] / data['count'] * 100:.1f}%" if data['count'] > 0 else '0%'
            extra_info += f"<p><strong>Eco-Drive比率:</strong> {eco_ratio} | <strong>Eco-Driveプレミアム:</strong> {data['eco_drive_premium']:+.1f}%</p>"

        if 'collab_count' in data:
            extra_info += f"<p><strong>コラボモデル:</strong> {data.get('collab_count', 0)}個 | <strong>限定モデル:</strong> {data.get('limited_count', 0)}個</p>"

        # 駆動方式分布
        movement_html = '<p><strong>駆動方式:</strong> '
        for mv, count in data.get('movement_distribution', {}).items():
            movement_html += f'{mv}({count}) '
        movement_html += '</p>'

        # 人気モデルテーブル
        models_html = ''
        if data.get('top_models'):
            models_html = '<h4 style="margin-top: 15px;">📌 人気モデルTop' + str(len(data['top_models'])) + '</h4>'
            models_html += '<table style="font-size: 0.9em;"><tr><th>型番</th><th>販売数</th><th>中央値</th><th>CV</th></tr>'
            for model in data['top_models']:
                models_html += f"<tr><td><strong>{model['model']}</strong></td><td>{model['count']}</td><td>${model['median']:.0f}</td><td>{model['cv']:.3f}</td></tr>"
            models_html += '</table>'

        # アコーディオンボタンとパネル
        accordions_html += f'''
        <div id="line_{brand_name}_{safe_id}">
            <button class="accordion" onclick="toggleAccordion(this)">
                {line_name} - 販売数: {data['count']:,} | 中央値: ${data['median']:.0f} | 安定度: {stability}
            </button>
            <div class="panel">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div><strong>販売数:</strong> {data['count']:,}</div>
                    <div><strong>中央値:</strong> ${data['median']:.0f}</div>
                    <div><strong>平均値:</strong> ${data['mean']:.0f}</div>
                    <div><strong>CV値:</strong> <span class="badge {cv_badge}">{cv:.3f}</span></div>
                    <div><strong>最安値:</strong> ${data['min']:.0f}</div>
                    <div><strong>最高値:</strong> ${data['max']:.0f}</div>
                </div>
                {movement_html}
                {extra_info}
                {models_html}
            </div>
        </div>
        '''

    # 全体をラップ
    section_class = 'gshock-special' if is_gshock_special else ''
    section_title = 'G-SHOCK特区 ⚡' if is_gshock_special else f'{brand_name} ライン別詳細分析'

    full_html = f'''
    <div class="{section_class}">
        <h2 class="section-title">{section_title}</h2>
        <p style="margin-bottom: 20px;">各ラインをクリックして詳細を表示</p>
        {nav_html}
        {accordions_html}
    </div>
    '''

    return full_html

# SEIKOライン別HTML生成
seiko_lines_html = generate_line_analysis_html('SEIKO', deepdive['seiko_lines'])

# CASIOライン別HTML生成（G-SHOCKは特区扱い）
casio_lines = deepdive['casio_lines'].copy()
gshock_data = casio_lines.pop('G-SHOCK', None)

gshock_html = ''
if gshock_data:
    gshock_html = generate_line_analysis_html('GSHOCK', {'G-SHOCK': gshock_data}, is_gshock_special=True)

casio_lines_html = generate_line_analysis_html('CASIO', casio_lines)

# CITIZENライン別HTML生成
citizen_lines_html = generate_line_analysis_html('CITIZEN', deepdive['citizen_lines'])

# HTMLに挿入する箇所を探す
# v3ではブランド別タブはないので、駆動方式タブの後に新しいタブを追加する必要がある

# まず、タブボタンを追加
tabs_insert = '''
            <button class="tab" onclick="showTab('seiko_detail')">SEIKO詳細</button>
            <button class="tab" onclick="showTab('casio_detail')">CASIO詳細</button>
            <button class="tab" onclick="showTab('citizen_detail')">CITIZEN詳細</button>'''

# タブボタン領域を探して挿入（"パーツ"タブの前に挿入）
html_content = html_content.replace(
    '<button class="tab" onclick="showTab(\'parts\')">パーツ</button>',
    tabs_insert + '\n            <button class="tab" onclick="showTab(\'parts\')">パーツ</button>'
)

# タブコンテンツを追加
seiko_tab_content = f'''
        <div class="tab-content" id="seiko_detail">
            {seiko_lines_html}
        </div>
'''

casio_tab_content = f'''
        <div class="tab-content" id="casio_detail">
            {gshock_html}
            {casio_lines_html}
        </div>
'''

citizen_tab_content = f'''
        <div class="tab-content" id="citizen_detail">
            {citizen_lines_html}
        </div>
'''

# パーツタブの前に挿入
parts_tab_pattern = r'(<div class="tab-content" id="parts">)'
replacement = seiko_tab_content + casio_tab_content + citizen_tab_content + r'\1'
html_content = re.sub(parts_tab_pattern, replacement, html_content, count=1)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

file_size = len(html_content.encode('utf-8'))
print(f"✅ v3拡張完了！")
print(f"📦 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"📊 追加タブ:")
print(f"  - SEIKO詳細: {len(deepdive['seiko_lines'])}ライン")
print(f"  - CASIO詳細: {len(deepdive['casio_lines'])}ライン（G-SHOCK特区含む）")
print(f"  - CITIZEN詳細: {len(deepdive['citizen_lines'])}ライン")
