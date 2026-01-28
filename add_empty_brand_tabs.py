#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7つの新ブランドのタブボタンとコンテンツ（空）を追加
販売数順: Swatch, BREITLING, NIXON, ISSEY MIYAKE, Tissot, DIOR, SAINT LAURENT
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 1. タブボタンの追加 =====
# RADOボタンの後に7つのブランドボタンを追加

rado_button = '<button class="tab" onclick="showTab(\'RADO\')">RADO</button>'
rado_button_pos = html.find(rado_button)

if rado_button_pos == -1:
    print("❌ エラー: RADOボタンが見つかりません")
    exit(1)

# 新しいタブボタン（販売数順）
new_buttons = '''
        <button class="tab" onclick="showTab('Swatch')">Swatch</button>
        <button class="tab" onclick="showTab('BREITLING')">BREITLING</button>
        <button class="tab" onclick="showTab('NIXON')">NIXON</button>
        <button class="tab" onclick="showTab('ISSEY_MIYAKE')">ISSEY MIYAKE</button>
        <button class="tab" onclick="showTab('Tissot')">Tissot</button>
        <button class="tab" onclick="showTab('DIOR')">DIOR</button>
        <button class="tab" onclick="showTab('SAINT_LAURENT')">SAINT LAURENT</button>'''

# RADOボタンの後に挿入
insert_pos = rado_button_pos + len(rado_button)
html = html[:insert_pos] + new_buttons + html[insert_pos:]

print("✓ タブボタン追加完了（7ブランド）")

# ===== 2. 空タブコンテンツの追加 =====
# Cartierタブの後に7つの空タブコンテンツを追加

# Cartierタブの終了位置を探す（ネストカウント方式）
cartier_start = html.find('<div id="Cartier" class="tab-content">')
if cartier_start == -1:
    print("❌ エラー: Cartierタブが見つかりません")
    exit(1)

# Cartierタブの終了</div>を探す（ネストを考慮）
div_count = 1
search_pos = cartier_start + len('<div id="Cartier" class="tab-content">')
body_pos = html.find('</body>')

while div_count > 0 and search_pos < body_pos:
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: Cartierタブの閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            cartier_end = next_close + 6  # 6 = len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✓ Cartierタブ終了位置: {cartier_end}")

# 7つの空タブコンテンツを作成
empty_tabs = '''

    <!-- Swatch タブ（未実装）-->
    <div id="Swatch" class="tab-content">
        <h2 class="section-title">🇨🇭 Swatch 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 49個
        </p>
    </div>

    <!-- BREITLING タブ（未実装）-->
    <div id="BREITLING" class="tab-content">
        <h2 class="section-title">✈️ BREITLING 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 40個
        </p>
    </div>

    <!-- NIXON タブ（未実装）-->
    <div id="NIXON" class="tab-content">
        <h2 class="section-title">🏄 NIXON 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 40個
        </p>
    </div>

    <!-- ISSEY MIYAKE タブ（未実装）-->
    <div id="ISSEY_MIYAKE" class="tab-content">
        <h2 class="section-title">🗾 ISSEY MIYAKE 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 34個
        </p>
    </div>

    <!-- Tissot タブ（未実装）-->
    <div id="Tissot" class="tab-content">
        <h2 class="section-title">🇨🇭 Tissot 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 33個
        </p>
    </div>

    <!-- DIOR タブ（未実装）-->
    <div id="DIOR" class="tab-content">
        <h2 class="section-title">💎 DIOR 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 31個
        </p>
    </div>

    <!-- SAINT LAURENT タブ（未実装）-->
    <div id="SAINT_LAURENT" class="tab-content">
        <h2 class="section-title">👔 SAINT LAURENT 詳細分析</h2>
        <p style="text-align: center; padding: 50px; color: #666;">
            準備中...<br>
            販売数: 29個
        </p>
    </div>
'''

# Cartierタブの後に挿入
html = html[:cartier_end] + empty_tabs + html[cartier_end:]

print("✓ 空タブコンテンツ追加完了（7ブランド）")

# HTMLファイルを保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ 7ブランドのタブ（空）追加完了！")
print("   - タブボタン: Swatch, BREITLING, NIXON, ISSEY MIYAKE, Tissot, DIOR, SAINT LAURENT")
print("   - タブコンテンツ: 準備中メッセージのみ")
print(f"   - ファイルサイズ: {len(html):,}文字")
