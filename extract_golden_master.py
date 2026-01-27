#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Master抽出スクリプト
既存のindex.htmlから各ブランドタブのHTMLセクションを抽出
"""
import os

print("🔍 Golden Master抽出開始...")

# HTMLファイルを読み込み
html_path = 'index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"✓ HTMLファイル読み込み完了: {len(html):,}文字")

# 各ブランドのタブを抽出
brands = ['SEIKO', 'CASIO', 'CITIZEN', 'Orient']

for brand in brands:
    print(f"\n📋 {brand}タブを抽出中...")

    # タブの開始位置を検索
    tab_start_tag = f'<div id="{brand}" class="tab-content">'
    tab_start = html.find(tab_start_tag)

    if tab_start == -1:
        print(f"  ❌ {brand}タブが見つかりません")
        continue

    print(f"  ✓ 開始位置: {tab_start}")

    # ネストカウントで終了位置を特定
    div_count = 1
    search_pos = tab_start + len(tab_start_tag)
    tab_end = -1

    while div_count > 0 and search_pos < len(html):
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            print(f"  ❌ 閉じタグが見つかりません")
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                tab_end = next_close + 6  # 6 = len('</div>')
                break
            else:
                search_pos = next_close + 6

    if tab_end == -1:
        print(f"  ❌ 終了位置が見つかりません")
        continue

    print(f"  ✓ 終了位置: {tab_end}")

    # タブHTMLを抽出
    tab_html = html[tab_start:tab_end]
    print(f"  ✓ 抽出サイズ: {len(tab_html):,}文字")

    # golden_masterディレクトリに保存
    output_path = f'golden_master/{brand.lower()}_tab.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tab_html)

    print(f"  ✅ 保存完了: {output_path}")

    # グラフ数をカウント
    graph_count = tab_html.count('Plotly.newPlot')
    print(f"  📊 グラフ数: {graph_count}個")

    # Top30行数をカウント（概算）
    top30_marker = 'Top30' if brand != 'Orient' else 'Top30'
    if top30_marker in tab_html:
        # <tbody>内の<tr>をカウント
        tbody_start = tab_html.find('<tbody>')
        if tbody_start != -1:
            tbody_end = tab_html.find('</tbody>', tbody_start)
            if tbody_end != -1:
                tbody_section = tab_html[tbody_start:tbody_end]
                row_count = tbody_section.count('<tr>')
                print(f"  📋 Top30行数: {row_count}行")

print("\n" + "="*60)
print("✅ Golden Master抽出完了")
print("="*60)
