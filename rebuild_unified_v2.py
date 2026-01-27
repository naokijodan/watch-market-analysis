#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合再構築スクリプト v2 - CITIZEN実装
"""
import pandas as pd
from datetime import datetime
import sys

# ストラテジーをインポート
from strategies.citizen import CITIZENStrategy

print("🔄 統合再構築スクリプト v2 - CITIZEN実装")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# データ読み込み
print("\n📄 データ読み込み中...")
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()

# CITIZENデータ抽出
df_citizen = df_complete[df_complete['ブランド'] == 'CITIZEN'].copy()
df_citizen['TITLE_UPPER'] = df_citizen['タイトル'].str.upper()
print(f"✓ CITIZEN完品データ: {len(df_citizen)}件")

# CITIZENストラテジー実行
print("\n🔵 CITIZENストラテジー実行中...")
citizen_strategy = CITIZENStrategy(
    brand_name='CITIZEN',
    df_brand=df_citizen,
    brand_color='#1565c0',
    brand_color_light='#e3f2fd'
)

# データ処理
citizen_strategy.process_data()

# HTML生成
citizen_html = citizen_strategy.generate_html()
print(f"✓ CITIZEN HTML生成完了: {len(citizen_html):,}文字")

# HTML読み込み
print("\n📖 index.html読み込み中...")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
print(f"✓ 読み込み完了: {len(html):,}文字")


def find_tab_position(html, brand_name):
    """タブ位置を特定"""
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


# CITIZENタブを置換
print("\n🔄 CITIZENタブを置換中...")
start_pos, end_pos = find_tab_position(html, 'CITIZEN')
html = html[:start_pos] + citizen_html + html[end_pos:]
print(f"✓ 置換完了")

# 保存
print("\n💾 index.htmlを保存中...")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 保存完了: {len(html) / 1024:.1f} KB")
print("\n" + "=" * 60)
print("✅ CITIZEN実装完了")
print("=" * 60)
print("\n📝 ブラウザでCITIZENタブを確認してください")
print("   - 基本統計セクション")
print("   - Top30テーブル（検索リンク＋チェックボックス付き）")
