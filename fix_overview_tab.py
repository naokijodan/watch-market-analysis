#!/usr/bin/env python3
"""
overview tabの問題を修正
1. 重複セクション削除（完品データ統計、月別販売数推移）
2. ブランド別グラフデータをCSVから再生成
3. 価格帯グラフデータをCSVから再生成
4. 月別推移の重複削除
"""

import pandas as pd
import json
from datetime import datetime

print("=== overview tab修正開始 ===\n")

# CSVデータ読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()

print(f"総データ数: {len(df):,}件")
print(f"完品データ数: {len(df_complete):,}件\n")

# ===== 1. ブランド別データ集計 =====
print("=== ブランド別データ集計 ===")
brand_counts = df_complete['ブランド'].value_counts()
print(f"ブランド数: {len(brand_counts)}件")
print(f"Tissot完品データ: {brand_counts.get('Tissot', 0)}件\n")

# Top20ブランド（棒グラフ用）
top20_brands = brand_counts.head(20)
brand_bar_data = {
    "y": top20_brands.index.tolist(),
    "x": top20_brands.values.tolist(),
    "type": "bar",
    "orientation": "h",
    "marker": {"color": "#0D47A1"}
}

# Top10ブランド（円グラフ用）
top10_brands = brand_counts.head(10)
brand_pie_data = {
    "labels": top10_brands.index.tolist(),
    "values": top10_brands.values.tolist(),
    "type": "pie"
}

print(f"✅ ブランド別Top20: {top20_brands.head(3).to_dict()}")
print(f"✅ ブランド別Top10: {top10_brands.head(3).to_dict()}\n")

# ===== 2. 価格帯データ集計 =====
print("=== 価格帯データ集計 ===")
price_bins = list(range(0, 1000, 50)) + [float('inf')]
price_labels = [f'${i}-{i+49}' for i in range(0, 950, 50)] + ['$1000+']
df_complete['価格帯'] = pd.cut(df_complete['価格'], bins=price_bins, labels=price_labels, right=False)
price_dist = df_complete['価格帯'].value_counts().reindex(price_labels, fill_value=0)

price_dist_data = {
    "x": price_labels,
    "y": price_dist.values.tolist(),
    "type": "bar",
    "marker": {"color": "#1976D2"}
}

print(f"✅ 価格帯分布: {len(price_dist)}区分")
print(f"   $0-49: {price_dist['$0-49']}件")
print(f"   $100-149: {price_dist['$100-149']}件")
print(f"   $1000+: {price_dist['$1000+']}件\n")

# ===== 3. 月別販売数推移（駆動方式別）=====
print("=== 月別販売数推移集計 ===")

# 販売日から年月を抽出
df_complete['年月'] = pd.to_datetime(df_complete['販売日'], errors='coerce').dt.strftime('%Y-%m')
monthly_movement = df_complete.groupby(['年月', '駆動方式']).size().unstack(fill_value=0)

# 月のリスト
months = sorted(df_complete['年月'].dropna().unique())
print(f"✅ 月数: {len(months)}ヶ月")
print(f"   期間: {months[0]} 〜 {months[-1]}")

# 月別データをJSON形式で作成
monthly_data_json = []
for month in months:
    if month in monthly_movement.index:
        month_data = monthly_movement.loc[month].to_dict()
        monthly_data_json.append({
            "month": month,
            "data": month_data
        })

print(f"✅ 月別データ: {len(monthly_data_json)}件\n")

# ===== 4. 完品データ統計 =====
print("=== 完品データ統計 ===")
complete_count = len(df_complete)
complete_total = df_complete['価格'].sum()
complete_avg = df_complete['価格'].mean()
complete_median = df_complete['価格'].median()

print(f"完品販売数: {complete_count:,}件")
print(f"完品総売上: ${complete_total:,.0f}")
print(f"完品平均価格: ${complete_avg:.2f}")
print(f"完品中央値: ${complete_median:.2f}\n")

# ===== HTMLファイル読み込み =====
print("=== HTMLファイル読み込み ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"ファイルサイズ: {len(html):,}文字\n")

# ===== 修正1: 重複した完品データ統計セクションを削除 =====
print("=== 修正1: 重複セクション削除 ===")

# 1つ目の完品データ統計セクション（Line 927-949付近）を探す
first_complete_stats_start = html.find('<h2 class="section-title">📦 完品データ統計</h2>')
if first_complete_stats_start != -1:
    # セクションの終了位置を探す（次のh2タグまで）
    next_section_start = html.find('<h2 class="section-title">', first_complete_stats_start + 1)
    if next_section_start != -1:
        # 2つ目の完品データ統計セクションを探す
        second_complete_stats_start = html.find('<h2 class="section-title">📦 完品データ統計</h2>', first_complete_stats_start + 1)
        if second_complete_stats_start != -1 and second_complete_stats_start < html.find('<h2 class="section-title">🏷️ ブランド別分析（Top20）</h2>'):
            # 2つ目のセクションの終了位置を探す
            second_section_end = html.find('<h2 class="section-title">', second_complete_stats_start + 1)
            # 2つ目のセクションを削除
            html = html[:second_complete_stats_start] + html[second_section_end:]
            print("✅ 重複した完品データ統計セクションを削除")

# ===== 修正2: 重複した月別販売数推移セクションを削除 =====
# 1つ目の月別販売数推移セクションを探す
first_monthly_start = html.find('<h2 class="section-title">📅 月別販売数推移</h2>')
if first_monthly_start != -1:
    # 2つ目の月別販売数推移セクションを探す
    second_monthly_start = html.find('<h2 class="section-title">📅 月別販売数推移</h2>', first_monthly_start + 1)
    if second_monthly_start != -1:
        # 2つ目のセクションの終了位置を探す（次のh2タグまで）
        second_monthly_end = html.find('<h2 class="section-title">', second_monthly_start + 1)
        # 2つ目のセクションを削除
        html = html[:second_monthly_start] + html[second_monthly_end:]
        print("✅ 重複した月別販売数推移セクションを削除\n")

# ===== 修正3: 完品データ統計の値を更新 =====
print("=== 修正3: 完品データ統計の値を更新 ===")

# 新しい完品データ統計セクション
new_complete_stats = f'''        <h2 class="section-title">📦 完品データ統計</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="label">完品販売数</div>
                <div class="value">{complete_count:,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="label">完品総売上</div>
                <div class="value">${complete_total:,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">完品平均価格</div>
                <div class="value">${complete_avg:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📈</div>
                <div class="label">完品中央値</div>
                <div class="value">${complete_median:.2f}</div>
            </div>
        </div>

        '''

# 既存のセクションを新しい値で置換
old_stats_start = html.find('<h2 class="section-title">📦 完品データ統計</h2>')
old_stats_end = html.find('<h2 class="section-title">', old_stats_start + 1)
html = html[:old_stats_start] + new_complete_stats + html[old_stats_end:]
print("✅ 完品データ統計の値を更新\n")

# ===== 修正4: ブランド別グラフデータを更新 =====
print("=== 修正4: ブランド別グラフデータを更新 ===")

# ブランド別棒グラフ
old_brand_bar = 'function drawBrandBarChart() {'
brand_bar_pos = html.find(old_brand_bar)
if brand_bar_pos != -1:
    # 関数の終了位置を探す
    brand_bar_end = html.find('}\n', brand_bar_pos) + 2

    # 新しい関数
    new_brand_bar_func = f'''function drawBrandBarChart() {{
        const data = [{json.dumps(brand_bar_data, ensure_ascii=False)}];
        const layout = {{...plotlyLayout, title: 'ブランド別販売数（Top20）', xaxis: {{title: '販売数'}}, height: 500}};
        Plotly.newPlot('brandBarChart', data, layout, plotlyConfig);
    }}
'''
    html = html[:brand_bar_pos] + new_brand_bar_func + html[brand_bar_end:]
    print(f"✅ ブランド別棒グラフを更新（Tissot: {brand_counts.get('Tissot', 0)}件）")

# ブランド別円グラフ
old_brand_pie = 'function drawBrandPieChart() {'
brand_pie_pos = html.find(old_brand_pie)
if brand_pie_pos != -1:
    brand_pie_end = html.find('}\n', brand_pie_pos) + 2

    new_brand_pie_func = f'''function drawBrandPieChart() {{
        const data = [{json.dumps(brand_pie_data, ensure_ascii=False)}];
        const layout = {{...plotlyLayout, title: 'ブランド別シェア（Top10）'}};
        Plotly.newPlot('brandPieChart', data, layout, plotlyConfig);
    }}
'''
    html = html[:brand_pie_pos] + new_brand_pie_func + html[brand_pie_end:]
    print(f"✅ ブランド別円グラフを更新\n")

# ===== 修正5: 価格帯グラフデータを更新 =====
print("=== 修正5: 価格帯グラフデータを更新 ===")

old_price_dist = 'function drawPriceDistChart() {'
price_dist_pos = html.find(old_price_dist)
if price_dist_pos != -1:
    price_dist_end = html.find('}\n', price_dist_pos) + 2

    new_price_dist_func = f'''function drawPriceDistChart() {{
        const data = [{json.dumps(price_dist_data, ensure_ascii=False)}];
        const layout = {{...plotlyLayout, title: '価格帯分布（完品のみ・50ドル刻み）', xaxis: {{title: '価格帯'}}, yaxis: {{title: '件数'}}}};
        Plotly.newPlot('priceDistChart', data, layout, plotlyConfig);
    }}
'''
    html = html[:price_dist_pos] + new_price_dist_func + html[price_dist_end:]
    print("✅ 価格帯グラフを更新\n")

# ===== 修正6: 月別販売数推移の重複削除と更新 =====
print("=== 修正6: 月別販売数推移の重複削除と更新 ===")

# 1つ目のdrawMonthlyTrendChart関数を探す
first_monthly_func_start = html.find('function drawMonthlyTrendChart() {')
if first_monthly_func_start != -1:
    # 関数の終了位置を探す（次の関数定義または</script>まで）
    first_monthly_func_end = html.find('\n    function ', first_monthly_func_start + 1)
    if first_monthly_func_end == -1:
        first_monthly_func_end = html.find('\n    </script>', first_monthly_func_start)

    # 2つ目の関数を探す
    second_monthly_func_start = html.find('function drawMonthlyTrendChart() {', first_monthly_func_end)
    if second_monthly_func_start != -1:
        # 2つ目の関数の終了位置
        second_monthly_func_end = html.find('\n    function ', second_monthly_func_start + 1)
        if second_monthly_func_end == -1:
            second_monthly_func_end = html.find('\n    </script>', second_monthly_func_start)

        # 2つ目の関数を削除
        html = html[:second_monthly_func_start] + html[second_monthly_func_end:]
        print("✅ 重複したdrawMonthlyTrendChart関数を削除")

# 新しい月別販売数推移関数
new_monthly_func = f'''    // 月別販売数推移
    function drawMonthlyTrendChart() {{
        const months = {json.dumps(months, ensure_ascii=False)};
        const movementData = {{}};

        // 各駆動方式ごとのデータを準備
        {json.dumps(monthly_data_json, ensure_ascii=False)}.forEach(item => {{
            Object.keys(item.data).forEach(movement => {{
                if (!movementData[movement]) movementData[movement] = [];
            }});
        }});

        Object.keys(movementData).forEach(movement => {{
            {json.dumps(monthly_data_json, ensure_ascii=False)}.forEach(item => {{
                movementData[movement].push(item.data[movement] || 0);
            }});
        }});

        const traces = Object.keys(movementData).map(movement => ({{
            x: months,
            y: movementData[movement],
            name: movement,
            type: 'scatter',
            mode: 'lines+markers',
            stackgroup: 'one'
        }}));

        const layout = {{...plotlyLayout, title: '月別販売数推移（完品のみ）', xaxis: {{title: '年月'}}, yaxis: {{title: '販売数'}}}};
        Plotly.newPlot('monthlyTrendChart', traces, layout, plotlyConfig);
    }}

'''

# 1つ目の関数を新しい関数で置換
first_monthly_func_start = html.find('    // 月別販売数推移')
if first_monthly_func_start != -1:
    # "// 価格帯分布"の直前まで削除
    price_dist_comment = html.find('    // 価格帯分布', first_monthly_func_start)
    html = html[:first_monthly_func_start] + new_monthly_func + html[price_dist_comment:]
    print("✅ 月別販売数推移関数を更新")

# 関数呼び出しの重複削除
init_charts_start = html.find('document.addEventListener(\'DOMContentLoaded\', function() {')
if init_charts_start != -1:
    init_section = html[init_charts_start:init_charts_start+500]
    if 'drawMonthlyTrendChart();\n        drawMonthlyTrendChart();' in init_section:
        html = html.replace('drawMonthlyTrendChart();\n        drawMonthlyTrendChart();', 'drawMonthlyTrendChart();')
        print("✅ 重複した関数呼び出しを削除\n")

# ===== HTMLファイル保存 =====
print("=== HTMLファイル保存 ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTMLファイルを保存（{len(html):,}文字）\n")

print("=== 修正完了 ===")
print("✅ 重複セクション削除")
print("✅ ブランド別グラフ更新（Tissotを含む）")
print("✅ 価格帯グラフ更新")
print("✅ 月別販売数推移更新")
print("✅ 完品データ統計更新")
