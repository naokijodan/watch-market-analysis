#!/usr/bin/env python3
"""
CASIOタブのライン別詳細分析・キャラクター/コラボ分析に検索リンクを追加
"""
from urllib.parse import quote

html_path = '/Users/naokijodan/Desktop/watch-market-analysis/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

def make_search_td(brand, keyword):
    """検索リンクのtdを生成"""
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(brand)}+{quote(keyword)}+Watch&LH_Sold=1&LH_Complete=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={quote(brand)}%20{quote(keyword)}%20時計&status=on_sale"
    return f'''                        <td style="white-space: nowrap;">
                            <a href="{ebay_url}" target="_blank" class="link-btn link-ebay" style="font-size: 0.75em; padding: 4px 8px;">eBay</a>
                            <input type="checkbox" class="search-checkbox" style="margin: 0 4px;">
                            <a href="{mercari_url}" target="_blank" class="link-btn link-mercari" style="font-size: 0.75em; padding: 4px 8px;">メルカリ</a>
                            <input type="checkbox" class="search-checkbox" style="margin: 0 4px;">
                        </td>'''

# === 1. ライン別詳細分析 ===
# ヘッダーに検索列追加
old_line_header = '''                        <th class="casio-accent">JDMプレミアム</th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <td><strong>G-SHOCK</strong></td>'''

new_line_header = '''                        <th class="casio-accent">JDMプレミアム</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <td><strong>G-SHOCK</strong></td>'''

html = html.replace(old_line_header, new_line_header, 1)
print("✓ ライン別ヘッダーに検索列追加")

# 各ライン行にリンク追加
lines = ['G-SHOCK', 'その他CASIO', 'PRO TREK', 'BABY-G', 'LINEAGE', 'OCEANUS', 'EDIFICE', 'SHEEN']

for line_name in lines:
    # このラインの行末</tr>を見つけて、その前にtdを挿入
    # パターン: JDMプレミアムの値の後の</tr>
    marker = f'<td><strong>{line_name}</strong></td>'
    pos = html.find(marker)
    if pos == -1:
        print(f"  ⚠️ {line_name} が見つかりません")
        continue

    # この行の</tr>を探す
    tr_end = html.find('</tr>', pos)
    if tr_end == -1:
        print(f"  ⚠️ {line_name} の</tr>が見つかりません")
        continue

    search_td = make_search_td('CASIO', line_name)
    html = html[:tr_end] + '\n' + search_td + '\n                    ' + html[tr_end:]
    print(f"  ✓ {line_name} にリンク追加")

# === 2. キャラクター/コラボ分析 ===
# ヘッダーに検索列追加
old_collab_header = '''                        <th class="casio-accent">仕入上限(¥)</th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <td><strong>コラボ一般</strong></td>'''

new_collab_header = '''                        <th class="casio-accent">仕入上限(¥)</th>
                        <th>検索</th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <td><strong>コラボ一般</strong></td>'''

# キャラクター/コラボセクション内のヘッダーを特定（ライン別と区別するため位置で制限）
collab_section_start = html.find('🎬 キャラクター/コラボ分析')
if collab_section_start == -1:
    print("❌ キャラクター/コラボ分析セクションが見つかりません")
else:
    # このセクション以降で置換
    before = html[:collab_section_start]
    after = html[collab_section_start:]
    after = after.replace(old_collab_header, new_collab_header, 1)
    html = before + after
    print("✓ コラボヘッダーに検索列追加")

    collabs = [
        ('コラボ一般', 'collaboration'),
        ('バック・トゥ・ザ・フューチャー', 'Back to the Future'),
        ('バービー', 'Barbie'),
        ('ストレンジャー・シングス', 'Stranger Things'),
        ('エヴァンゲリオン', 'Evangelion'),
        ('ITZY', 'ITZY'),
        ('ガンダム', 'Gundam'),
        ('トランスフォーマー', 'Transformers'),
        ('ポケモン', 'Pokemon'),
        ('ドラゴンボール', 'Dragon Ball'),
    ]

    for jp_name, en_name in collabs:
        marker = f'<td><strong>{jp_name}</strong></td>'
        # コラボセクション以降で探す
        pos = html.find(marker, collab_section_start)
        if pos == -1:
            print(f"  ⚠️ {jp_name} が見つかりません")
            continue

        tr_end = html.find('</tr>', pos)
        if tr_end == -1:
            print(f"  ⚠️ {jp_name} の</tr>が見つかりません")
            continue

        search_td = make_search_td('CASIO', en_name)
        html = html[:tr_end] + '\n' + search_td + '\n                    ' + html[tr_end:]
        print(f"  ✓ {jp_name} にリンク追加")

# 保存
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ 完了: {html_path}")
