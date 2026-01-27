#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通ユーティリティ関数
全ブランドで使用される汎用関数
"""
import pandas as pd
import numpy as np
from urllib.parse import quote


def format_price(price):
    """
    価格を$記号付きでフォーマット

    Args:
        price: 価格（数値）

    Returns:
        フォーマットされた価格文字列（例: "$1,234"）
    """
    if pd.isna(price):
        return "$0"
    return f"${int(price):,}"


def calculate_cv(values):
    """
    変動係数（Coefficient of Variation）を計算

    Args:
        values: 数値のリストまたはSeries

    Returns:
        CV値（標準偏差 / 平均）
    """
    if len(values) == 0:
        return 0.0

    mean_val = np.mean(values)
    if mean_val == 0:
        return 0.0

    std_val = np.std(values)
    cv = std_val / mean_val

    return round(cv, 3)


def cv_to_stability(cv_value):
    """
    CV値を安定度表示に変換

    Args:
        cv_value: CV値

    Returns:
        安定度（☆の数）
    """
    if cv_value < 0.5:
        return "☆☆☆"
    elif cv_value < 1.0:
        return "☆☆☆"
    elif cv_value < 2.0:
        return "☆☆"
    else:
        return "☆"


def aggregate_top_lines(series, top_n=7, others_label="その他"):
    """
    ライン別集計でTop N + その他を作成

    Args:
        series: 集計済みSeries（index=ライン名, values=販売数）
        top_n: 上位何件を個別表示するか
        others_label: その他のラベル

    Returns:
        集計済みSeries（Top N + その他）
    """
    if len(series) <= top_n:
        return series

    top_items = series.head(top_n)
    others_sum = series.iloc[top_n:].sum()

    result = pd.concat([top_items, pd.Series({others_label: others_sum})])

    return result


def generate_search_links(brand, keyword, link_type='model'):
    """
    eBayとメルカリの検索リンクを生成

    Args:
        brand: ブランド名（例: "SEIKO"）
        keyword: 検索キーワード（型番、ライン名、キャラクター名など）
        link_type: リンクタイプ（'model', 'line', 'character'）

    Returns:
        dict: {'ebay': URL, 'mercari': URL}
    """
    # キーワードのエンコーディング
    if link_type == 'model':
        # 型番検索: "SEIKO SMW006A Watch"
        ebay_query = f"{brand}+{keyword}+Watch"
        mercari_query = f"{brand} {keyword} 時計"

    elif link_type == 'line':
        # ライン検索: "SEIKO SEIKO 5 Watch"
        # ライン名がブランド名を含む場合（例: "SEIKO 5"）はそのまま使用
        ebay_query = f"{brand}+{keyword}+Watch"
        mercari_query = f"{brand} {keyword} 時計"

    elif link_type == 'character':
        # キャラクター検索: "SEIKO ジブリ Watch"
        ebay_query = f"{brand}+{keyword}+Watch"
        mercari_query = f"{brand} {keyword} 時計"

    else:
        raise ValueError(f"不明なlink_type: {link_type}")

    # URL生成
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={ebay_query}&LH_Sold=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={quote(mercari_query)}&status=on_sale"

    return {
        'ebay': ebay_url,
        'mercari': mercari_url
    }


def generate_search_link_html(brand, keyword, link_type='model', include_checkbox=True):
    """
    検索リンクのHTMLを生成

    Args:
        brand: ブランド名
        keyword: 検索キーワード
        link_type: リンクタイプ
        include_checkbox: チェックボックスを含めるか

    Returns:
        HTMLの文字列
    """
    links = generate_search_links(brand, keyword, link_type)

    if include_checkbox:
        html = f'''<a href="{links['ebay']}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <input type="checkbox" class="search-checkbox">
                            <a href="{links['mercari']}" target="_blank" class="link-btn link-mercari">メルカリ</a>
                            <input type="checkbox" class="search-checkbox">'''
    else:
        html = f'''<a href="{links['ebay']}" target="_blank" class="link-btn link-ebay">eBay</a>
                            <a href="{links['mercari']}" target="_blank" class="link-btn link-mercari">メルカリ</a>'''

    return html


def format_percentage(value, decimals=1):
    """
    パーセンテージをフォーマット

    Args:
        value: 値（0.0-1.0）
        decimals: 小数点以下の桁数

    Returns:
        フォーマットされた文字列（例: "12.3%"）
    """
    return f"{value * 100:.{decimals}f}%"


def safe_divide(numerator, denominator, default=0.0):
    """
    安全な除算（ゼロ除算を回避）

    Args:
        numerator: 分子
        denominator: 分母
        default: 分母が0の場合の返り値

    Returns:
        除算結果
    """
    if denominator == 0:
        return default
    return numerator / denominator


if __name__ == '__main__':
    print("✅ 共通ユーティリティ関数テスト")

    # format_price テスト
    assert format_price(1234.56) == "$1,234"
    assert format_price(0) == "$0"
    print("  ✓ format_price")

    # calculate_cv テスト
    cv = calculate_cv([100, 110, 90, 105])
    assert 0 < cv < 1
    print(f"  ✓ calculate_cv: {cv}")

    # cv_to_stability テスト
    assert cv_to_stability(0.3) == "☆☆☆"
    assert cv_to_stability(1.5) == "☆☆"
    print("  ✓ cv_to_stability")

    # aggregate_top_lines テスト
    series = pd.Series({'A': 100, 'B': 80, 'C': 60, 'D': 40, 'E': 20, 'F': 10, 'G': 5, 'H': 3, 'I': 2})
    result = aggregate_top_lines(series, top_n=7)
    assert len(result) == 8  # 7 + その他
    assert 'その他' in result.index
    print(f"  ✓ aggregate_top_lines: {len(result)}項目")

    # generate_search_links テスト
    links = generate_search_links('SEIKO', 'SKX007', 'model')
    assert 'ebay' in links
    assert 'mercari' in links
    assert 'SKX007' in links['ebay']
    print(f"  ✓ generate_search_links")

    # generate_search_link_html テスト
    html = generate_search_link_html('SEIKO', 'SEIKO 5', 'line')
    assert 'eBay' in html
    assert 'メルカリ' in html
    print(f"  ✓ generate_search_link_html")

    print("\n✅ すべてのテスト成功")
