#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CASIOタブにチェックボックスを追加（既存コンテンツ保持）
"""
import re

print("🔄 CASIOタブにチェックボックスを追加中...")
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


# CASIOタブを抽出
print("\n📍 CASIOタブを抽出中...")
start_pos, end_pos = find_tab_position(html, 'CASIO')
casio_html = html[start_pos:end_pos]
print(f"✓ 抽出完了: {len(casio_html):,}文字")

# 全ての検索リンクの後ろにチェックボックスを追加
print("\n🔵 検索リンクにチェックボックス追加中...")

# eBayリンクの後ろにチェックボックスを追加
ebay_pattern = r'(<a href="https://www\.ebay\.com/[^"]*" target="_blank" class="link-btn link-ebay">eBay</a>)'
casio_html = re.sub(
    ebay_pattern,
    r'\1\n                            <input type="checkbox" class="search-checkbox">',
    casio_html
)

# メルカリリンクの後ろにチェックボックスを追加
mercari_pattern = r'(<a href="https://jp\.mercari\.com/[^"]*" target="_blank" class="link-btn link-mercari">メルカリ</a>)'
casio_html = re.sub(
    mercari_pattern,
    r'\1\n                            <input type="checkbox" class="search-checkbox">',
    casio_html
)

# 変更数をカウント
checkbox_count = casio_html.count('class="search-checkbox"')
print(f"✓ チェックボックス追加完了: {checkbox_count}個")

# CASIOタブを置換
print("\n🔄 CASIOタブを置換中...")
html = html[:start_pos] + casio_html + html[end_pos:]
print("✓ 置換完了")

# 保存
print("\n💾 index.htmlを保存中...")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 保存完了: {len(html) / 1024:.1f} KB")
print("\n" + "=" * 60)
print("✅ CASIOタブにチェックボックス追加完了")
print("=" * 60)
