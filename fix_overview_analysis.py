#!/usr/bin/env python3
"""
全体分析セクションの改修
1. 月別販売数推移 → 削除（データが1ヶ月分のみで意味がない）
2. 価格帯分布 → 50ドル刻みに変更
"""

import pandas as pd
import re

# CSVデータ読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()

# 価格帯分布を50ドル刻みで計算
print("=== 価格帯分布を計算中（50ドル刻み） ===")
price_bins_data = {}
labels = []

for i in range(0, 1000, 50):
    label = f'${i}-{i+49}'
    labels.append(label)
    count = len(df_complete[(df_complete['価格'] >= i) & (df_complete['価格'] < i + 50)])
    price_bins_data[label] = count

# $1000以上
label = '$1000+'
labels.append(label)
count = len(df_complete[df_complete['価格'] >= 1000])
price_bins_data[label] = count

print("\n価格帯分布:")
for label in labels:
    print(f"{label}: {price_bins_data[label]}件")

# HTMLファイル読み込み
print("\n=== HTMLファイル読み込み ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"HTMLファイルサイズ: {len(html)}文字")

# 1. 月別販売数推移セクションを削除
print("\n=== 月別販売数推移セクションを削除 ===")
monthly_section_start = html.find('<h2 class="section-title">📅 月別販売数推移（季節性分析）</h2>')
if monthly_section_start == -1:
    print("❌ 月別販売数推移セクションが見つかりません")
else:
    # 次のセクション（価格帯分布）の開始位置を探す
    price_section_start = html.find('<h2 class="section-title">💰 価格帯分布</h2>', monthly_section_start)
    if price_section_start == -1:
        print("❌ 価格帯分布セクションが見つかりません")
    else:
        # 月別販売数推移セクションを削除
        html = html[:monthly_section_start] + html[price_section_start:]
        print(f"✅ 月別販売数推移セクションを削除しました")

# 2. drawMonthlyTrendChart関数を削除
print("\n=== drawMonthlyTrendChart関数を削除 ===")
function_start = html.find('// 月別販売数推移')
if function_start == -1:
    print("❌ drawMonthlyTrendChart関数が見つかりません")
else:
    # 関数の終了位置を探す（次の関数の開始まで）
    function_end = html.find('// 価格帯分布', function_start)
    if function_end == -1:
        print("❌ 価格帯分布関数が見つかりません")
    else:
        html = html[:function_start] + html[function_end:]
        print(f"✅ drawMonthlyTrendChart関数を削除しました")

# 3. initCharts関数からdrawMonthlyTrendChart()の呼び出しを削除
print("\n=== initCharts関数からdrawMonthlyTrendChart()呼び出しを削除 ===")
call_pattern = r'\s*drawMonthlyTrendChart\(\);\s*\n'
if re.search(call_pattern, html):
    html = re.sub(call_pattern, '\n', html)
    print("✅ drawMonthlyTrendChart()呼び出しを削除しました")
else:
    print("⚠️ drawMonthlyTrendChart()呼び出しが見つかりませんでした")

# 4. 価格帯分布のデータを50ドル刻みに変更
print("\n=== 価格帯分布を50ドル刻みに変更 ===")

# 既存の価格帯分布関数を探す
price_func_start = html.find('// 価格帯分布')
price_func_end = html.find('</script>', price_func_start)

if price_func_start == -1:
    print("❌ 価格帯分布関数が見つかりません")
else:
    # 新しい価格帯分布関数を作成
    x_labels = labels
    y_values = [price_bins_data[label] for label in labels]

    new_price_function = f'''// 価格帯分布（50ドル刻み）
    function drawPriceDistChart() {{
        const data = [{{
            x: {x_labels},
            y: {y_values},
            type: 'bar',
            marker: {{color: '#1976D2'}}
        }}];
        const layout = {{...plotlyLayout, title: '価格帯分布（50ドル刻み）', xaxis: {{title: '価格帯'}}, yaxis: {{title: '件数'}}}};
        Plotly.newPlot('priceDistChart', data, layout, plotlyConfig);
    }}
    '''

    # 次の関数またはスクリプト終了を探す
    next_function_start = html.find('</script>', price_func_start)

    # 既存の関数を置換
    old_function_end = html.find('}', html.find('function drawPriceDistChart()', price_func_start))
    if old_function_end != -1:
        old_function_end = html.find('\n', old_function_end) + 1
        html = html[:price_func_start] + new_price_function + html[old_function_end:]
        print("✅ 価格帯分布を50ドル刻みに変更しました")
    else:
        print("❌ 既存の価格帯分布関数の終了位置が見つかりません")

# HTMLファイルを保存
print("\n=== HTMLファイルを保存 ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTMLファイルを保存しました（{len(html)}文字）")

print("\n=== 完了 ===")
print("✅ 月別販売数推移セクションを削除")
print("✅ 価格帯分布を50ドル刻みに変更")
