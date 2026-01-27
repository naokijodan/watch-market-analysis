#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CITIZENタブの重複したscriptタグを削除
"""
import re

print("🔄 CITIZENタブの重複scriptタグ削除中...")

# index.html読み込み
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"✓ 読み込み完了: {len(html):,}文字")

# CITIZENタブ内のscriptブロックを探す
citizen_script_pattern = r'<script>\s*const citizenBlue = \'#1565c0\'.*?</script>'

# 重複回数を確認
matches = re.findall(citizen_script_pattern, html, re.DOTALL)
print(f"✓ CITIZEN scriptブロック数: {len(matches)}個")

if len(matches) > 1:
    print(f"⚠️  重複を検出: {len(matches) - 1}個削除します")

    # 最初のscriptブロックを残して、残りを削除
    first_script = matches[0]

    # 全てのCITIZEN scriptブロックを削除
    html = re.sub(citizen_script_pattern, '', html, flags=re.DOTALL)

    # CITIZENタブの終了位置を見つける
    citizen_tab_start = html.find('<div id="CITIZEN" class="tab-content">')

    # CITIZENタブの終了位置をネストカウントで特定
    div_count = 1
    search_pos = citizen_tab_start + len('<div id="CITIZEN" class="tab-content">')

    while div_count > 0 and search_pos < len(html):
        next_open = html.find('<div', search_pos)
        next_close = html.find('</div>', search_pos)

        if next_close == -1:
            break

        if next_open != -1 and next_open < next_close:
            div_count += 1
            search_pos = next_open + 4
        else:
            div_count -= 1
            if div_count == 0:
                citizen_tab_end = next_close
                break
            search_pos = next_close + 6

    # CITIZENタブの終了直前に1つだけscriptを挿入
    html = html[:citizen_tab_end] + '\n\n    ' + first_script + '\n    ' + html[citizen_tab_end:]

    print(f"✓ 重複削除完了")
else:
    print("✓ 重複なし")

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 保存完了: {len(html) / 1024:.1f} KB")
print("✅ 完了")
