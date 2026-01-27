#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合再構築スクリプト v1 - 骨組み
各ブランドタブを順番に置換して、1回のファイル書き込みで完了
"""
import pandas as pd
from datetime import datetime

print("🔄 統合再構築スクリプト v1")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# データ読み込み
print("\n📄 データ読み込み中...")
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()
print(f"✓ 完品データ: {len(df_complete)}件")

# 各ブランドのデータを抽出
brands_data = {
    'SEIKO': df_complete[df_complete['ブランド'] == 'SEIKO'].copy(),
    'CASIO': df_complete[df_complete['ブランド'] == 'CASIO'].copy(),
    'CITIZEN': df_complete[df_complete['ブランド'] == 'CITIZEN'].copy(),
    'Orient': df_complete[df_complete['ブランド'] == 'Orient'].copy()
}

# タイトル大文字化
for brand_name, brand_df in brands_data.items():
    brand_df['TITLE_UPPER'] = brand_df['タイトル'].str.upper()
    print(f"  {brand_name}: {len(brand_df)}件")

print("\n" + "=" * 60)

# HTML読み込み
print("\n📖 index.html読み込み中...")
html_path = 'index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()
print(f"✓ 読み込み完了: {len(html):,}文字")


def find_tab_position(html, brand_name):
    """
    ブランドタブの開始・終了位置をネストカウントで特定

    Args:
        html: HTML文字列
        brand_name: ブランド名

    Returns:
        (start_pos, end_pos) タプル
    """
    tab_start_tag = f'<div id="{brand_name}" class="tab-content">'
    tab_start = html.find(tab_start_tag)

    if tab_start == -1:
        raise ValueError(f"{brand_name}タブが見つかりません")

    print(f"  ✓ {brand_name}タブ開始位置: {tab_start}")

    # ネストカウントで終了位置を特定
    div_count = 1
    search_pos = tab_start + len(tab_start_tag)
    tab_end = -1

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
                tab_end = next_close + 6  # 6 = len('</div>')
                break
            else:
                search_pos = next_close + 6

    if tab_end == -1:
        raise ValueError(f"{brand_name}タブの終了位置が見つかりません")

    print(f"  ✓ {brand_name}タブ終了位置: {tab_end}")
    print(f"  ✓ タブサイズ: {tab_end - tab_start:,}文字")

    return (tab_start, tab_end)


def generate_dummy_tab(brand_name, data_count):
    """
    ダミータブHTMLを生成（テスト用）

    Args:
        brand_name: ブランド名
        data_count: データ件数

    Returns:
        HTML文字列
    """
    html = f'''<div id="{brand_name}" class="tab-content">
        <h2 style="color: #333; margin-bottom: 20px;">{brand_name} 分析（v1 骨組みテスト）</h2>

        <div class="stats-grid" style="margin-bottom: 30px;">
            <div class="stat-card">
                <div class="label">データ件数</div>
                <div class="value">{data_count:,}件</div>
            </div>
            <div class="stat-card">
                <div class="label">ステータス</div>
                <div class="value">骨組み完成</div>
            </div>
        </div>

        <p style="color: #666; margin: 20px 0;">
            ✅ 統合スクリプトの骨組みが正常に動作しています。<br>
            次のステップで詳細なHTML生成ロジックを実装します。
        </p>
    </div>'''

    return html


# 各ブランドタブの位置を特定
print("\n📍 各ブランドタブの位置を特定中...")
tab_positions = {}
for brand_name in ['SEIKO', 'CASIO', 'CITIZEN', 'Orient']:
    try:
        tab_positions[brand_name] = find_tab_position(html, brand_name)
    except ValueError as e:
        print(f"  ❌ {e}")

print("\n" + "=" * 60)

# 各ブランドタブを置換（後ろから順番に置換）
print("\n🔄 各ブランドタブを置換中...")
brands_order = ['Orient', 'CITIZEN', 'CASIO', 'SEIKO']  # 後ろから置換

for brand_name in brands_order:
    if brand_name not in tab_positions:
        print(f"  ⚠️  {brand_name}: スキップ（位置未特定）")
        continue

    print(f"\n  🔵 {brand_name}タブを置換中...")

    # ダミータブHTML生成
    data_count = len(brands_data[brand_name])
    new_tab_html = generate_dummy_tab(brand_name, data_count)

    # 置換
    start_pos, end_pos = tab_positions[brand_name]
    html = html[:start_pos] + new_tab_html + html[end_pos:]

    print(f"    ✓ 置換完了: {len(new_tab_html):,}文字")

print("\n" + "=" * 60)

# HTMLを保存
print("\n💾 index.htmlを保存中...")
output_path = 'index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

new_size = len(html) / 1024
print(f"✓ 保存完了: {output_path} ({new_size:.1f} KB)")

print("\n" + "=" * 60)
print("✅ 統合再構築スクリプト v1 完了")
print("=" * 60)
print("\n📝 次のステップ:")
print("  1. ブラウザで index.html を開いて各タブを確認")
print("  2. 骨組みが正常なら、詳細なHTML生成ロジックを実装")
