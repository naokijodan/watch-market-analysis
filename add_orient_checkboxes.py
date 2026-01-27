#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orientタブにチェックボックスを追加（既存コンテンツ保持）
CITIZEN仕様に準拠：Top30 + ライン別詳細分析 + キャラクター/コラボ分析
"""
import re
from utils.common import generate_search_link_html

print("🔄 Orientタブにチェックボックスを追加中...")
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


# Orientタブを抽出
print("\n📍 Orientタブを抽出中...")
start_pos, end_pos = find_tab_position(html, 'Orient')
orient_html = html[start_pos:end_pos]
print(f"✓ 抽出完了: {len(orient_html):,}文字")

# 1. Top30セクション: 既存の検索リンクの後ろにチェックボックスを追加
print("\n🔵 1. Top30セクションにチェックボックス追加中...")
# eBayリンクの後ろにチェックボックスを追加
ebay_pattern = r'(<a href="https://www\.ebay\.com/[^"]*" target="_blank" class="link-btn link-ebay">eBay</a>)'
orient_html = re.sub(
    ebay_pattern,
    r'\1\n                            <input type="checkbox" class="search-checkbox">',
    orient_html
)

# メルカリリンクの後ろにチェックボックスを追加
mercari_pattern = r'(<a href="https://jp\.mercari\.com/[^"]*" target="_blank" class="link-btn link-mercari">メルカリ</a>)'
orient_html = re.sub(
    mercari_pattern,
    r'\1\n                            <input type="checkbox" class="search-checkbox">',
    orient_html
)
print("✓ Top30にチェックボックス追加完了")

# 2. ライン別詳細分析: 検索リンク + チェックボックス列を追加
print("\n🔵 2. ライン別詳細分析に検索列追加中...")

# テーブルヘッダーに「検索」列を追加（中央値の後）
# Orientはライン別詳細分析のテーブル構造が異なる可能性があるので調整
line_header_pattern = r'(<th>中央値</th>)\s*</tr>'
line_header_replacement = r'\1\n                        <th>検索</th>\n                    </tr>'
orient_html = re.sub(line_header_pattern, line_header_replacement, orient_html)

# Orientの主要ライン（rebuild_orient_v3_complete.pyから抽出）
lines = [
    ('Orient Star', 'Orient Star'),
    ('Bambino', 'Bambino'),
    ('Mako', 'Mako'),
    ('Sun & Moon', 'Sun & Moon'),
    ('Kamasu', 'Kamasu'),
    ('Sports', 'Sports'),
    ('その他Orient', 'Orient'),
]

for line_display, line_search_key in lines:
    # 各ラインの行末（中央値の後）に検索セルを追加
    line_row_pattern = rf'(<td><strong>{re.escape(line_display)}</strong></td>.*?<td>\$[^<]*</td>)\s*</tr>'

    search_links = generate_search_link_html('Orient', line_search_key, link_type='line', include_checkbox=True)

    line_row_replacement = rf'''\1
                        <td>
                            {search_links}
                        </td>
    </tr>'''

    orient_html = re.sub(line_row_pattern, line_row_replacement, orient_html, flags=re.DOTALL)

print("✓ ライン別詳細分析に検索列追加完了")

# 3. キャラクター/コラボ分析: 検索リンク + チェックボックス列を追加
print("\n🔵 3. キャラクター/コラボ分析に検索列追加中...")

# キャラクター/コラボセクションのテーブルヘッダーを特定
collab_section_start = orient_html.find('🎭 キャラクター/コラボ分析')
if collab_section_start != -1:
    # このセクション内のテーブルヘッダーを見つける
    collab_table_start = orient_html.find('<thead>', collab_section_start)
    if collab_table_start != -1:
        collab_header_end = orient_html.find('</tr>', collab_table_start)

        # テーブルヘッダーに「検索」列を追加（比率の後）
        collab_before = orient_html[:collab_header_end]
        collab_after = orient_html[collab_header_end:]

        orient_html = collab_before + '\n                        <th>検索</th>\n                    ' + collab_after

# Orientのキャラクター/コラボ（主要なものを抽出）
characters = [
    ('DISNEY', 'DISNEY'),
    ('MARVEL', 'MARVEL'),
    ('STAR WARS', 'STAR WARS'),
    ('HELLO KITTY', 'HELLO KITTY'),
    ('SNOOPY', 'SNOOPY'),
    ('EVANGELION', 'EVANGELION'),
    ('GUNDAM', 'GUNDAM'),
]

for char_display, char_search_key in characters:
    # 各キャラクター行の末尾（比率の後）に検索セルを追加
    # Orientのアクセントカラークラス名を使用
    char_row_pattern = rf'(<td><strong>{re.escape(char_display)}</strong></td>.*?<td style="color: #FF6B35;">[^<]*</td>)\s*</tr>'

    search_links = generate_search_link_html('Orient', char_search_key, link_type='character', include_checkbox=True)

    char_row_replacement = rf'''\1
                        <td>
                            {search_links}
                        </td>
    </tr>'''

    orient_html = re.sub(char_row_pattern, char_row_replacement, orient_html, flags=re.DOTALL)

print("✓ キャラクター/コラボ分析に検索列追加完了")

# Orientタブを置換
print("\n🔄 Orientタブを置換中...")
html = html[:start_pos] + orient_html + html[end_pos:]
print("✓ 置換完了")

# 保存
print("\n💾 index.htmlを保存中...")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 保存完了: {len(html) / 1024:.1f} KB")
print("\n" + "=" * 60)
print("✅ Orientタブにチェックボックス追加完了")
print("=" * 60)
print("\n📝 ブラウザで確認:")
print("   - Top30テーブル: 各リンクの横にチェックボックス")
print("   - ライン別詳細分析: 検索列追加")
print("   - キャラクター/コラボ分析: 検索列追加")
