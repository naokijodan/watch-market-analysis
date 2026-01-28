#!/usr/bin/env python3
"""
OMEGA タブ修正スクリプト
問題:
1. Chart.js ライブラリが読み込まれていない → グラフが表示されない
2. 価格表示が¥記号になっている → CSV は USD なので $ に修正
"""

import re

# HTML ファイルを読み込む
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("🔧 OMEGA タブ修正開始...\n")

# ===== 修正1: Chart.js CDN を追加 =====
print("1. Chart.js ライブラリを追加中...")

# plotly の次の行に Chart.js を追加
plotly_line = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
chartjs_cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'

if chartjs_cdn in html:
    print("   ⚠️  Chart.js は既に追加されています")
else:
    html = html.replace(plotly_line, f'{plotly_line}\n    {chartjs_cdn}')
    print("   ✅ Chart.js CDN を追加しました")

# ===== 修正2: OMEGA セクションの価格表示を ¥ から $ に変更 =====
print("\n2. OMEGA セクションの価格表示を修正中...")

# OMEGA タブの開始位置を特定
omega_start = html.find('<div id="OMEGA" class="tab-content">')
if omega_start == -1:
    print("   ❌ OMEGA タブが見つかりません")
    exit(1)

# OMEGA タブの終了位置を特定（ネストカウント）
div_count = 1
search_pos = omega_start + len('<div id="OMEGA" class="tab-content">')
omega_end = -1

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("   ❌ OMEGA タブの終了タグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            omega_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

if omega_end == -1:
    print("   ❌ OMEGA タブの終了位置が特定できません")
    exit(1)

# OMEGA セクション内の ¥ を $ に置換
omega_section = html[omega_start:omega_end]
original_omega = omega_section

# 平均落札価格の ¥ を $ に変更
omega_section = omega_section.replace('<div style="font-size: 32px; font-weight: bold;">¥1,075</div>',
                                      '<div style="font-size: 32px; font-weight: bold;">$1,075</div>')

# ライン別・特徴別分析のテーブル内の ¥ を $ に変更（OMEGA セクション内のみ）
# パターン: <td style="padding: 12px; text-align: right;">¥数値</td>
omega_section = re.sub(
    r'(<td style="padding: 12px; text-align: right;">)¥(\d{1,3}(?:,\d{3})*)',
    r'\1$\2',
    omega_section
)

# 変更があったかチェック
if omega_section != original_omega:
    html = html[:omega_start] + omega_section + html[omega_end:]

    # 変更数をカウント
    yen_count = original_omega.count('¥')
    dollar_count = omega_section.count('$')
    print(f"   ✅ OMEGA セクション内の価格表示を修正: ¥ → $ ({yen_count} 箇所)")
else:
    print("   ⚠️  価格表示は既に修正されています")

# ===== 保存 =====
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ 修正完了！")
print(f"   - Chart.js ライブラリ追加")
print(f"   - OMEGA 価格表示修正 (¥ → $)")
print(f"\n📝 ブラウザで index.html を開いて OMEGA タブのグラフを確認してください")
