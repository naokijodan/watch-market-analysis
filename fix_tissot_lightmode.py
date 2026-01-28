#!/usr/bin/env python3
"""
Tissotタブのライトモード問題を修正
1. 仕入上限の.highlightクラスを削除（ライトモードで白文字になる問題）
2. 避けるべき条件セクションのボーダー色を修正
"""

print("=== Tissotタブのライトモード問題修正開始 ===\n")

# HTMLファイル読み込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTMLファイル読み込み: {len(html):,}文字\n")

# ===== 修正1: 仕入上限の.highlightクラスを削除 =====
print("=== 修正1: 仕入上限の.highlightクラスを削除 ===")

# Tissotセクションのみを対象に置換
# パターン: <td class="highlight tissot-accent">¥XX,XXX</td>
# 置換後: <td class="tissot-accent">¥XX,XXX</td>

# Tissotタブの開始位置を探す
tissot_start = html.find('<div id="Tissot" class="tab-content">')
if tissot_start == -1:
    print("❌ Tissotタブが見つかりません")
    exit(1)

# Tissotタブの終了位置を探す（次のタブまたはscriptタグ）
# 次のタブの開始位置を探す（より広い範囲で）
next_tab = html.find('\n    <div id="', tissot_start + 100)
if next_tab == -1:
    # scriptタグの開始を探す
    tissot_end = html.find('\n    <script>', tissot_start)
else:
    tissot_end = next_tab

print(f"Tissotタブ範囲: {tissot_start} 〜 {tissot_end}")

# Tissotセクションを抽出
tissot_section = html[tissot_start:tissot_end]

# highlightクラスを削除
original_section = tissot_section
tissot_section = tissot_section.replace('class="highlight tissot-accent"', 'class="tissot-accent"')

# 変更箇所をカウント
changes = original_section.count('class="highlight tissot-accent"')
print(f"✅ {changes}箇所のhighlightクラスを削除")

# HTMLに戻す
html = html[:tissot_start] + tissot_section + html[tissot_end:]

# ===== 修正2: 避けるべき条件セクションのボーダー色を修正 =====
print("\n=== 修正2: 避けるべき条件セクションのボーダー色を修正 ===")

# 白色ボーダーをオレンジ色に変更
if 'border-left: 4px solid #FFFFFF;' in html:
    html = html.replace('border-left: 4px solid #FFFFFF;', 'border-left: 4px solid #ff6b35;')
    print("✅ ボーダー色を白 → オレンジに変更")
else:
    print("⚠️ 白色ボーダーが見つかりませんでした")

# HTMLファイル保存
print("\n=== HTMLファイル保存 ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTMLファイルを保存（{len(html):,}文字）\n")

print("=== 修正完了 ===")
print("✅ 仕入上限のライトモード表示問題を修正")
print("✅ ボーダー色を修正")
