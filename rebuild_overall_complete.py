#!/usr/bin/env python3
"""
全体分析タブ完全再構築スクリプト
元のHTMLの7セクション構成を完全に再現
"""

import pandas as pd
import json

# Excelファイル読み込み
print("📊 Excelファイルを読み込み中...")
df_basic = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='1_基本統計')
df_brands = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='2_ブランド別統計')
df_drive = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='3_駆動方式別統計')
df_monthly = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='7_月別推移')
df_price = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='8_価格帯分布')

# CSVファイルも読み込み（完品データ用）
print("📄 CSVファイルを読み込み中...")
df_csv = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# 1. 基本統計
basic_stats = {}
for _, row in df_basic.iterrows():
    basic_stats[row['項目']] = row['値']

total_sales = int(basic_stats['総販売数'].replace(' 個', '').replace(',', ''))
total_revenue = df_csv['価格'].sum() * df_csv['販売数'].sum() / len(df_csv)  # 総売上の概算
avg_price = float(basic_stats['平均価格'].replace('$', ''))
median_price = float(basic_stats['中央値価格'].replace('$', ''))

# 総売上の正確な計算
total_revenue = (df_csv['価格'] * df_csv['販売数']).sum()

# 2. 完品データ統計
complete_df = df_csv[df_csv['商品状態'] == '完品'].copy()
complete_sales = int(complete_df['販売数'].sum())
complete_revenue = (complete_df['価格'] * complete_df['販売数']).sum()
complete_avg = complete_df['価格'].mean()
complete_median = complete_df['価格'].median()

# 3. 駆動方式データ
drive_labels = df_drive['駆動方式'].tolist()
drive_sales = df_drive['販売数'].tolist()

# 4. ブランドデータ（Top20とTop10）
top20_brands = df_brands.head(20)
brand_labels_20 = top20_brands['ブランド'].tolist()
brand_sales_20 = top20_brands['販売数'].tolist()

top10_brands = df_brands.head(10)
brand_labels_10 = top10_brands['ブランド'].tolist()
brand_sales_10 = top10_brands['販売数'].tolist()

# 5. 月別データ
monthly_data = []
for _, row in df_monthly.iterrows():
    month = row['販売月']
    # 駆動方式別の販売数を集計（完品のみ）
    month_complete = complete_df[pd.to_datetime(complete_df['販売日']).dt.to_period('M').astype(str) == month]
    drive_counts = {}
    for drive in drive_labels:
        count = int(month_complete[month_complete['駆動方式'] == drive]['販売数'].sum())
        drive_counts[drive] = count
    monthly_data.append({"month": month, "data": drive_counts})

months = df_monthly['販売月'].tolist()

# 6. 価格帯データ
price_labels = df_price['価格帯'].tolist()
price_counts = df_price['販売数'].tolist()

# 7. 市場インサイト
top_brand = brand_labels_20[0]
top_brand_sales = brand_sales_20[0]
second_brand = brand_labels_20[1]
second_brand_sales = brand_sales_20[1]
top_price_range = price_labels[price_counts.index(max(price_counts))]
top_price_sales = max(price_counts)
top_drive = drive_labels[drive_sales.index(max(drive_sales))]
top_drive_sales = max(drive_sales)

print("🔨 HTMLコンテンツを生成中...")

# HTML生成
html = f'''    <div id="overview" class="tab-content active">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="label">総販売数</div>
                <div class="value">{total_sales:,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="label">総売上</div>
                <div class="value">${total_revenue:,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">平均価格</div>
                <div class="value">${avg_price:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="icon">📈</div>
                <div class="label">中央値</div>
                <div class="value">${median_price:.2f}</div>
            </div>
        </div>

        <div class="insight-box">
            <h3>💡 市場インサイト</h3>
            <ul>
                <li>🔝 最大カテゴリ: {top_brand} ({top_brand_sales:,}件) と{second_brand} ({second_brand_sales:,}件) で市場の過半数を占める</li>
                <li>💎 高価格帯: 自動巻 (${complete_df[complete_df['駆動方式']=='自動巻']['価格'].median():.2f}) とOMEGA (${complete_df[complete_df['ブランド']=='OMEGA']['価格'].median():.2f}) が市場を牽引</li>
                <li>⚡ 回転率重視: クオーツ・ソーラーは低価格で回転が早い（エントリー層向け）</li>
                <li>🔩 パーツ市場: {len(df_csv[df_csv['商品状態']=='パーツ']):,}件の取引あり（完品に次ぐ規模）</li>
            </ul>
        </div>

        <h2 class="section-title">📊 カテゴリ別分析</h2>
        <div class="chart-grid">
            <div class="chart-container"><div id="movementBarChart"></div></div>
            <div class="chart-container"><div id="movementPieChart"></div></div>
        </div>


        <h2 class="section-title">📦 完品データ統計</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="label">完品販売数</div>
                <div class="value">{complete_sales:,}</div>
            </div>
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="label">完品総売上</div>
                <div class="value">${complete_revenue:,.0f}</div>
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

<h2 class="section-title">🏷️ ブランド別分析（Top20）</h2>
        <div class="chart-grid">
            <div class="chart-container"><div id="brandBarChart"></div></div>
            <div class="chart-container"><div id="brandPieChart"></div></div>
        </div>


        <h2 class="section-title">📅 月別販売数推移</h2>
        <div class="chart-container"><div id="monthlyTrendChart"></div></div>


        <h2 class="section-title">📅 月別販売数推移</h2>
        <div class="chart-container"><div id="monthlyTrendChart"></div></div>

        <h2 class="section-title">💰 価格帯分布（完品のみ）</h2>
        <div class="chart-container"><div id="priceDistChart"></div></div>
    </div>

    <script>
    // 駆動方式別棒グラフ
    function drawMovementBarChart() {{
        const data = [{{"y": {json.dumps(drive_labels)}, "x": {json.dumps(drive_sales)}, "type": "bar", "orientation": "h", "marker": {{"color": "#1976D2"}}}}];
        const layout = {{...plotlyLayout, title: '駆動方式別販売数', xaxis: {{title: '販売数'}}}};
        Plotly.newPlot('movementBarChart', data, layout, plotlyConfig);
    }}

    // 駆動方式別円グラフ
    function drawMovementPieChart() {{
        const data = [{{"labels": {json.dumps(drive_labels)}, "values": {json.dumps(drive_sales)}, "type": "pie", "hole": 0.4}}];
        const layout = {{...plotlyLayout, title: '駆動方式別シェア'}};
        Plotly.newPlot('movementPieChart', data, layout, plotlyConfig);
    }}

    // ブランド別棒グラフ
    function drawBrandBarChart() {{
        const data = [{{"y": {json.dumps(brand_labels_20)}, "x": {json.dumps(brand_sales_20)}, "type": "bar", "orientation": "h", "marker": {{"color": "#0D47A1"}}}}];
        const layout = {{...plotlyLayout, title: 'ブランド別販売数（Top20）', xaxis: {{title: '販売数'}}, height: 500}};
        Plotly.newPlot('brandBarChart', data, layout, plotlyConfig);
    }}

    // ブランド別円グラフ
    function drawBrandPieChart() {{
        const data = [{{"labels": {json.dumps(brand_labels_10)}, "values": {json.dumps(brand_sales_10)}, "type": "pie"}}];
        const layout = {{...plotlyLayout, title: 'ブランド別シェア（Top10）'}};
        Plotly.newPlot('brandPieChart', data, layout, plotlyConfig);
    }}

    // 月別販売数推移
    function drawMonthlyTrendChart() {{
        const months = {json.dumps(months)};
        const movementData = {{}};

        // 各駆動方式ごとのデータを準備
        {json.dumps(monthly_data)}.forEach(item => {{
            Object.keys(item.data).forEach(movement => {{
                if (!movementData[movement]) movementData[movement] = [];
            }});
        }});

        Object.keys(movementData).forEach(movement => {{
            {json.dumps(monthly_data)}.forEach(item => {{
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

    // 価格帯分布（50ドル刻み）
    function drawPriceDistChart() {{
        const data = [{{
            x: {json.dumps(price_labels)},
            y: {json.dumps(price_counts)},
            type: 'bar',
            marker: {{color: '#1976D2'}}
        }}];
        const layout = {{...plotlyLayout, title: '価格帯分布（完品のみ・50ドル刻み）', xaxis: {{title: '価格帯'}}, yaxis: {{title: '件数'}}}};
        Plotly.newPlot('priceDistChart', data, layout, plotlyConfig);
    }}

    // グラフ初期化
    document.addEventListener('DOMContentLoaded', function() {{
        drawMovementBarChart();
        drawMovementPieChart();
        drawBrandBarChart();
        drawBrandPieChart();
        drawMonthlyTrendChart();
        drawMonthlyTrendChart();
        drawPriceDistChart();
    }});
    </script>'''

# HTMLファイル読み込み
print("📄 HTMLファイルを読み込み中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 全体分析タブの開始位置を特定
overview_start = html_content.find('<div id="overview"')
if overview_start == -1:
    print("❌ エラー: 全体分析タブが見つかりません")
    exit(1)

print(f"✅ 全体分析タブの開始位置: {overview_start}")

# 全体分析タブの終了位置を特定（ネストカウント）
div_count = 1
search_pos = html_content.find('>', overview_start) + 1

while div_count > 0 and search_pos < len(html_content):
    next_open = html_content.find('<div', search_pos)
    next_close = html_content.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: 閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            overview_end = next_close + 6  # len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✅ 全体分析タブの終了位置: {overview_end}")

# 置換
old_size = len(html_content) / 1024
html_content = html_content[:overview_start] + html + html_content[overview_end:]
new_size = len(html_content) / 1024

print(f"\n📏 ファイルサイズ: {old_size:.1f}KB → {new_size:.1f}KB")

# 保存
print("💾 HTMLファイルを保存中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n✅ 全体分析タブの完全再構築が完了しました")
print(f"   7セクション:")
print(f"   1. 基本統計（4カード）")
print(f"   2. 市場インサイト（4項目）")
print(f"   3. カテゴリ別分析（駆動方式棒+円グラフ）")
print(f"   4. 完品データ統計（4カード）")
print(f"   5. ブランド別分析Top20（棒+円グラフ）")
print(f"   6. 月別販売数推移（折れ線グラフ）")
print(f"   7. 価格帯分布（棒グラフ）")
