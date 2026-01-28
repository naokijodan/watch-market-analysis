#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7つの空タブに雛形（8セクション構造）を追加
データは「準備中」として、構造のみ先に作成
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ===== ブランドごとの設定 =====
brands_config = [
    {
        'name': 'Swatch',
        'name_lower': 'swatch',
        'emoji': '🇨🇭',
        'color_primary': '#FF6B35',
        'color_accent': '#FFA500',
        'sales_count': 49,
    },
    {
        'name': 'BREITLING',
        'name_lower': 'breitling',
        'emoji': '✈️',
        'color_primary': '#000000',
        'color_accent': '#FFD700',
        'sales_count': 40,
    },
    {
        'name': 'NIXON',
        'name_lower': 'nixon',
        'emoji': '🏄',
        'color_primary': '#1E90FF',
        'color_accent': '#00CED1',
        'sales_count': 40,
    },
    {
        'name': 'ISSEY MIYAKE',
        'name_lower': 'isseymiyake',
        'emoji': '🗾',
        'color_primary': '#2C3E50',
        'color_accent': '#E74C3C',
        'sales_count': 34,
        'tab_id': 'ISSEY_MIYAKE',  # タブIDはアンダースコア
    },
    {
        'name': 'Tissot',
        'name_lower': 'tissot',
        'emoji': '🇨🇭',
        'color_primary': '#C41E3A',
        'color_accent': '#FFD700',
        'sales_count': 33,
    },
    {
        'name': 'DIOR',
        'name_lower': 'dior',
        'emoji': '💎',
        'color_primary': '#000000',
        'color_accent': '#D4AF37',
        'sales_count': 31,
    },
    {
        'name': 'SAINT LAURENT',
        'name_lower': 'saintlaurent',
        'emoji': '👔',
        'color_primary': '#000000',
        'color_accent': '#C0C0C0',
        'sales_count': 29,
        'tab_id': 'SAINT_LAURENT',  # タブIDはアンダースコア
    },
]

# ===== 雛形HTML生成関数 =====
def generate_template_html(config):
    """ブランドごとの雛形HTMLを生成"""
    brand_name = config['name']
    brand_lower = config['name_lower']
    emoji = config['emoji']
    color_primary = config['color_primary']
    color_accent = config['color_accent']
    sales_count = config['sales_count']
    tab_id = config.get('tab_id', brand_name)  # タブIDはデフォルトでブランド名

    template = f'''
    <div id="{tab_id}" class="tab-content">
        <h2 class="section-title {brand_lower}-primary">{emoji} {brand_name} 詳細分析</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{sales_count}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">準備中</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">準備中</div>
            </div>
            <div class="stat-card">
                <div class="label">型番抽出率</div>
                <div class="value {brand_lower}-accent">準備中</div>
            </div>
        </div>

        <div class="insight-box" style="border-left: 5px solid {color_primary};">
            <h3 class="{brand_lower}-primary">🎯 仕入れ戦略（実践ガイド）</h3>
            <div style="display: grid; gap: 15px;">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid {color_primary};">
                    <h4 style="color: {color_primary}; margin-bottom: 10px;">✅ 狙い目条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>データ分析中...</li>
                    </ul>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid {color_accent};">
                    <h4 style="color: #ff6b35; margin-bottom: 10px;">⚠️ 避けるべき条件</h4>
                    <ul style="margin-left: 20px;">
                        <li>データ分析中...</li>
                    </ul>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #7b1fa2;">
                    <h4 style="color: #7b1fa2; margin-bottom: 10px;">💰 仕入れ価格目安</h4>
                    <p style="margin: 0;"><strong>通常モデル:</strong> データ分析中</p>
                    <p style="margin: 5px 0 0 0;"><strong class="{brand_lower}-accent">人気ライン:</strong> データ分析中</p>
                </div>
            </div>
        </div>

        <h3 class="section-title {brand_lower}-primary">📊 市場分析グラフ</h3>
        <div class="{brand_lower}-grid">
            <div class="{brand_lower}-chart-container">
                <h4 class="{brand_lower}-primary">価格帯別分析（50ドル刻み）</h4>
                <div id="{brand_lower}_price_chart" style="height: 350px;"></div>
            </div>
            <div class="{brand_lower}-chart-container">
                <h4 class="{brand_lower}-primary">駆動方式別分布</h4>
                <div id="{brand_lower}_movement_chart" style="height: 350px;"></div>
            </div>
            <div class="{brand_lower}-chart-container">
                <h4 class="{brand_lower}-primary">性別・カテゴリー別分布</h4>
                <div id="{brand_lower}_gender_chart" style="height: 300px;"></div>
            </div>
            <div class="{brand_lower}-chart-container">
                <h4 class="{brand_lower}-primary">ライン別売上比率</h4>
                <div id="{brand_lower}_line_chart" style="height: 350px;"></div>
            </div>
        </div>

        <h3 class="section-title {brand_lower}-primary">🎭 特別版・限定モデル 分析</h3>
        <p style="color: #666; margin-bottom: 15px;">データ分析中...</p>

        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="label">特別版商品数</div>
                <div class="value {brand_lower}-accent">準備中</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">準備中</div>
            </div>
            <div class="stat-card">
                <div class="label">全体比率</div>
                <div class="value {brand_lower}-accent">準備中</div>
            </div>
        </div>

        <h3 class="section-title {brand_lower}-primary">📌 各ラインの人気モデル（実データより）Top15</h3>
        <p style="color: #666; margin-bottom: 20px;">データ分析中...</p>

        <h3 class="section-title {brand_lower}-primary">🔵 ライン別詳細分析</h3>
        <p style="color: #666; margin-bottom: 20px;">データ分析中...</p>

        <h3 class="section-title {brand_lower}-primary">🏆 全ライン横断 型番分析Top30</h3>
        <p style="color: #666; margin-bottom: 20px;">データ分析中...</p>

    </div>
'''

    # CSS生成
    css = f'''
    .{brand_lower}-primary {{ color: {color_primary}; }}
    .{brand_lower}-accent {{ color: {color_accent}; font-weight: bold; }}
    .{brand_lower}-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 20px 0;
    }}
    .{brand_lower}-chart-container {{
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .{brand_lower}-chart-container h4 {{
        margin-bottom: 10px;
        font-size: 16px;
    }}

    @media (max-width: 768px) {{
        .{brand_lower}-grid {{
            grid-template-columns: 1fr;
        }}
    }}
'''

    # グラフスクリプト生成（ダミーデータ）
    graph_script = f'''
        <script>
        const {brand_lower}Primary = '{color_primary}';
        const {brand_lower}Accent = '{color_accent}';
        const {brand_lower}Gradient = ['{color_primary}', '#7b68ee', '#9370db', '#ba55d3', '#da70d6'];

        // 準備中のダミーグラフ
        Plotly.newPlot('{brand_lower}_price_chart', [{{
            x: ['~$100', '$100-200', '$200-300', '$300-500', '$500-1K', '$1K+'],
            y: [0, 0, 0, 0, 0, 0],
            type: 'bar',
            marker: {{
                color: {brand_lower}Primary,
                line: {{color: {brand_lower}Accent, width: 1}}
            }},
            text: ['データ<br>準備中', '', '', '', '', ''],
            textposition: 'inside',
            hovertemplate: '<b>%{{x}}</b><br>データ準備中<extra></extra>'
        }}], {{
            xaxis: {{title: '価格帯', tickangle: -45}},
            yaxis: {{title: '販売数'}},
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_lower}_movement_chart', [{{
            labels: ['データ準備中'],
            values: [1],
            type: 'pie',
            marker: {{colors: {brand_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label',
            hovertemplate: 'データ準備中<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_lower}_gender_chart', [{{
            labels: ['データ準備中'],
            values: [1],
            type: 'pie',
            marker: {{colors: {brand_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label',
            hovertemplate: 'データ準備中<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});

        Plotly.newPlot('{brand_lower}_line_chart', [{{
            labels: ['データ準備中'],
            values: [1],
            type: 'pie',
            marker: {{colors: {brand_lower}Gradient}},
            textposition: 'inside',
            textinfo: 'label',
            hovertemplate: 'データ準備中<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
'''

    return template, css, graph_script

# ===== 各ブランドの雛形を置換 =====
print("📄 7ブランドのタブに雛形を追加開始...")

for config in brands_config:
    brand_name = config['name']
    tab_id = config.get('tab_id', brand_name)

    # 既存の空タブを検索
    old_tab_start = html.find(f'<div id="{tab_id}" class="tab-content">')
    if old_tab_start == -1:
        print(f"❌ エラー: {brand_name} タブが見つかりません")
        continue

    # タブの終了位置を探す（ネストカウント）
    div_count = 1
    search_pos = old_tab_start + len(f'<div id="{tab_id}" class="tab-content">')
    body_pos = html.find('</body>')

    while div_count > 0 and search_pos < body_pos:
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            print(f"❌ エラー: {brand_name} タブの閉じタグが見つかりません")
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                old_tab_end = next_close + 6
                break
            else:
                search_pos = next_close + 6

    # 雛形HTMLを生成
    template_html, css, graph_script = generate_template_html(config)

    # 既存の空タブを雛形で置換
    html = html[:old_tab_start] + template_html + html[old_tab_end:]

    print(f"✓ {brand_name} タブに雛形追加")

# ===== CSS追加 =====
style_end = html.find('</style>')
if style_end != -1:
    all_css = ''
    for config in brands_config:
        _, css, _ = generate_template_html(config)
        all_css += css + '\n'

    html = html[:style_end] + all_css + html[style_end:]
    print(f"✓ CSS追加完了（7ブランド）")

# ===== グラフスクリプト追加 =====
body_end = html.find('</body>')
if body_end != -1:
    all_scripts = ''
    for config in brands_config:
        _, _, graph_script = generate_template_html(config)
        all_scripts += graph_script + '\n'

    html = html[:body_end] + all_scripts + html[body_end:]
    print(f"✓ グラフスクリプト追加完了（7ブランド）")

# HTMLファイルを保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ 7ブランドのタブに雛形追加完了！")
print(f"   - 各タブ: 8セクション構造（データは「準備中」）")
print(f"   - Plotlyグラフ: ダミーデータで表示")
print(f"   - ファイルサイズ: {len(html):,}文字")
