#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Master検証スクリプト
新しく生成されたHTMLとGolden Masterを比較
"""
import os
import re
from difflib import unified_diff

def analyze_tab_structure(html_content, brand_name):
    """タブHTMLの構造を分析"""
    stats = {
        'brand': brand_name,
        'size': len(html_content),
        'sections': {},
        'tables': 0,
        'graph_containers': 0,
        'search_links': {
            'ebay': 0,
            'mercari': 0
        }
    }

    # セクション検出
    section_patterns = {
        '基本統計': r'<h3[^>]*>📊.*?基本統計',
        'Top30': r'<h3[^>]*>🏆.*?Top30',
        '価格帯別': r'<h3[^>]*>📈.*?価格帯別',
        'ライン別売上': r'<h3[^>]*>📊.*?ライン別売上',
        'ライン別詳細': r'<h3[^>]*>.*?ライン別詳細分析',
        'キャラクター': r'<h3[^>]*>.*?キャラクター',
        '限定モデル': r'<h3[^>]*>.*?限定モデル',
        '駆動方式': r'<h3[^>]*>.*?駆動方式',
        'カテゴリ': r'<h3[^>]*>.*?カテゴリ'
    }

    for section_name, pattern in section_patterns.items():
        if re.search(pattern, html_content, re.IGNORECASE):
            stats['sections'][section_name] = True

    # テーブル数
    stats['tables'] = html_content.count('<table>')

    # グラフコンテナ数
    stats['graph_containers'] = len(re.findall(r'<div id="[^"]*chart"', html_content))

    # 検索リンク数
    stats['search_links']['ebay'] = html_content.count('ebay.com')
    stats['search_links']['mercari'] = html_content.count('mercari.com')

    return stats

def compare_structures(golden_stats, new_stats):
    """構造を比較"""
    issues = []

    # サイズ比較（±10%まで許容）
    size_diff_pct = abs(new_stats['size'] - golden_stats['size']) / golden_stats['size'] * 100
    if size_diff_pct > 10:
        issues.append(f"⚠️ サイズ差が大きい: {size_diff_pct:.1f}% (Golden: {golden_stats['size']:,}, New: {new_stats['size']:,})")

    # セクション比較
    golden_sections = set(golden_stats['sections'].keys())
    new_sections = set(new_stats['sections'].keys())

    missing = golden_sections - new_sections
    if missing:
        issues.append(f"❌ 欠落セクション: {missing}")

    extra = new_sections - golden_sections
    if extra:
        issues.append(f"➕ 追加セクション: {extra}")

    # テーブル数比較
    if new_stats['tables'] != golden_stats['tables']:
        issues.append(f"⚠️ テーブル数不一致: Golden {golden_stats['tables']} → New {new_stats['tables']}")

    # グラフコンテナ数比較
    if new_stats['graph_containers'] != golden_stats['graph_containers']:
        issues.append(f"⚠️ グラフコンテナ数不一致: Golden {golden_stats['graph_containers']} → New {new_stats['graph_containers']}")

    return issues

def verify_brand(brand_name):
    """ブランドタブを検証"""
    print(f"\n{'='*60}")
    print(f"🔍 {brand_name}タブ検証")
    print(f"{'='*60}")

    golden_path = f'{brand_name.lower()}_tab.html'

    if not os.path.exists(golden_path):
        print(f"❌ Golden Masterが見つかりません: {golden_path}")
        return False

    # Golden Master読み込み
    with open(golden_path, 'r', encoding='utf-8') as f:
        golden_html = f.read()

    golden_stats = analyze_tab_structure(golden_html, brand_name)

    print(f"\n📊 Golden Master統計:")
    print(f"  サイズ: {golden_stats['size']:,}文字")
    print(f"  セクション: {list(golden_stats['sections'].keys())}")
    print(f"  テーブル数: {golden_stats['tables']}")
    print(f"  グラフコンテナ: {golden_stats['graph_containers']}")
    print(f"  検索リンク: eBay {golden_stats['search_links']['ebay']}, メルカリ {golden_stats['search_links']['mercari']}")

    return True

if __name__ == '__main__':
    print("🔍 Golden Master検証開始")

    brands = ['SEIKO', 'CASIO', 'CITIZEN', 'Orient']

    for brand in brands:
        verify_brand(brand)

    print(f"\n{'='*60}")
    print("✅ Golden Master検証完了")
    print(f"{'='*60}")
