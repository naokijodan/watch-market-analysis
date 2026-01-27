#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全ブランドにチェックボックスを追加（動的ライン名抽出版）
HTMLから実際のライン名・キャラクター名を抽出して検索列を追加
"""
import re
from utils.common import generate_search_link_html

print("🔄 全ブランドにチェックボックスを追加中（動的抽出版）...")
print("=" * 60)

# index.html読み込み
print("\n📖 index.html読み込み中...")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
print(f"✓ 読み込み完了: {len(html):,}文字")


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


def extract_lines_from_html(brand_html):
    """HTMLからライン名を抽出"""
    line_section_start = brand_html.find('ライン別詳細分析')
    if line_section_start == -1:
        return []

    next_section = brand_html.find('<h3', line_section_start + 100)
    if next_section == -1:
        next_section = brand_html.find('<h4', line_section_start + 100)
    if next_section == -1:
        return []

    line_section = brand_html[line_section_start:next_section]
    lines = re.findall(r'<td><strong>([^<]+)</strong></td>', line_section)
    return lines


def extract_characters_from_html(brand_html):
    """HTMLからキャラクター名を抽出"""
    char_section_start = brand_html.find('キャラクター/コラボ分析')
    if char_section_start == -1:
        return []

    next_section = brand_html.find('<h3', char_section_start + 100)
    if next_section == -1:
        next_section = brand_html.find('</div>', char_section_start + 5000)
    if next_section == -1:
        return []

    char_section = brand_html[char_section_start:next_section]
    characters = re.findall(r'<td><strong>([^<]+)</strong></td>', char_section)
    return characters


def add_checkboxes_to_brand(html, brand_name, brand_color_class):
    """ブランドにチェックボックスを追加"""
    print(f"\n{'=' * 60}")
    print(f"🔵 {brand_name}タブを処理中...")
    print(f"{'=' * 60}")

    # タブを抽出
    start_pos, end_pos = find_tab_position(html, brand_name)
    brand_html = html[start_pos:end_pos]
    print(f"✓ タブ抽出完了: {len(brand_html):,}文字")

    # 1. Top30セクション: チェックボックス追加
    print("\n🔵 1. Top30セクションにチェックボックス追加中...")
    ebay_pattern = r'(<a href="https://www\.ebay\.com/[^"]*" target="_blank" class="link-btn link-ebay">eBay</a>)'
    brand_html = re.sub(ebay_pattern, r'\1\n                            <input type="checkbox" class="search-checkbox">', brand_html)

    mercari_pattern = r'(<a href="https://jp\.mercari\.com/[^"]*" target="_blank" class="link-btn link-mercari">メルカリ</a>)'
    brand_html = re.sub(mercari_pattern, r'\1\n                            <input type="checkbox" class="search-checkbox">', brand_html)
    print("✓ Top30にチェックボックス追加完了")

    # 2. ライン別詳細分析: HTMLからライン名を抽出して検索列追加
    print("\n🔵 2. ライン別詳細分析に検索列追加中...")
    lines = extract_lines_from_html(brand_html)
    print(f"✓ {len(lines)}個のラインを検出")

    if len(lines) > 0:
        # テーブルヘッダーに「検索」列を追加
        if brand_name == 'Orient':
            line_header_pattern = r'(<th style="color: #FF6B35;">仕入上限\(¥\)</th>)\s*</tr>'
        else:
            line_header_pattern = rf'(<th class="{brand_color_class}">JDMプレミアム</th>)\s*</tr>'

        line_header_replacement = r'\1\n                        <th>検索</th>\n                    </tr>'
        brand_html = re.sub(line_header_pattern, line_header_replacement, brand_html)

        # 各ライン行に検索リンク + チェックボックス追加
        added_count = 0
        for line_name in lines:
            # ライン名の検索キーワード（ブランド名含む場合はそのまま、含まない場合はブランド名を除く）
            if line_name.startswith(brand_name):
                search_key = line_name
            elif line_name.startswith('その他'):
                search_key = brand_name
            else:
                search_key = line_name

            # ライン行のパターン（行全体をキャプチャして検索セルを追加）
            line_row_pattern = rf'(<td><strong>{re.escape(line_name)}</strong></td>.*?)\s*</tr>'

            search_links = generate_search_link_html(brand_name, search_key, link_type='line', include_checkbox=True)

            line_row_replacement = rf'''\1
                        <td>
                            {search_links}
                        </td>
    </tr>'''

            # 置換実行
            new_brand_html = re.sub(line_row_pattern, line_row_replacement, brand_html, flags=re.DOTALL, count=1)
            if new_brand_html != brand_html:
                added_count += 1
                brand_html = new_brand_html

        print(f"✓ {added_count}/{len(lines)}個のラインに検索列追加完了")

    # 3. キャラクター/コラボ分析: HTMLからキャラクター名を抽出して検索列追加
    print("\n🔵 3. キャラクター/コラボ分析に検索列追加中...")
    characters = extract_characters_from_html(brand_html)
    print(f"✓ {len(characters)}個のキャラクターを検出")

    if len(characters) > 0:
        # テーブルヘッダーに「検索」列を追加
        collab_section_start = brand_html.find('キャラクター/コラボ分析')
        if collab_section_start != -1:
            collab_table_start = brand_html.find('<thead>', collab_section_start)
            if collab_table_start != -1:
                collab_header_end = brand_html.find('</tr>', collab_table_start)
                collab_before = brand_html[:collab_header_end]
                collab_after = brand_html[collab_header_end:]
                brand_html = collab_before + '\n                        <th>検索</th>\n                    ' + collab_after

        # 各キャラクター行に検索リンク + チェックボックス追加
        added_count = 0
        for char_name in characters:
            # キャラクター行のパターン（シンプル版: キャラクター名から</tr>まで）
            char_row_pattern = rf'(<td><strong>{re.escape(char_name)}</strong></td>.*?)\s*</tr>'

            search_links = generate_search_link_html(brand_name, char_name, link_type='character', include_checkbox=True)

            char_row_replacement = rf'''\1
                        <td>
                            {search_links}
                        </td>
    </tr>'''

            # 置換実行
            new_brand_html = re.sub(char_row_pattern, char_row_replacement, brand_html, flags=re.DOTALL, count=1)
            if new_brand_html != brand_html:
                added_count += 1
                brand_html = new_brand_html

        print(f"✓ {added_count}/{len(characters)}個のキャラクターに検索列追加完了")

    # タブを置換
    html = html[:start_pos] + brand_html + html[end_pos:]
    return html


# 全ブランドに適用
brands = [
    ('SEIKO', 'seiko-accent'),
    ('CASIO', 'casio-accent'),
    ('CITIZEN', 'citizen-accent'),
    ('Orient', 'orient-accent'),
    ('RADO', 'rado-accent')
]

for brand_name, brand_color_class in brands:
    html = add_checkboxes_to_brand(html, brand_name, brand_color_class)

# 保存
print("\n" + "=" * 60)
print("💾 index.htmlを保存中...")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 保存完了: {len(html) / 1024:.1f} KB")
print("\n" + "=" * 60)
print("✅ 全ブランドにチェックボックス追加完了（動的抽出版）")
print("=" * 60)
print("\n📝 ブラウザで確認:")
print("   - 全ブランド、全ライン、全キャラクターに検索列が追加されています")
