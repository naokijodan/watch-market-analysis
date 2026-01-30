#!/usr/bin/env python3
"""
全体分析タブのみを再構築
Excelファイルのデータを使用してHTMLを更新
"""

import pandas as pd
import json

# Excelファイルからデータ読み込み
print("📊 Excelファイルを読み込み中...")
df_basic = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='1_基本統計')
df_brands = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='2_ブランド別統計')
df_drive = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='3_駆動方式別統計')
df_price = pd.read_excel('/Users/naokijodan/Desktop/watch-market-analysis/分析シート.xlsx', sheet_name='8_価格帯分布')

# 基本統計の値を抽出
basic_stats = {}
for _, row in df_basic.iterrows():
    basic_stats[row['項目']] = row['値']

total_sales = int(basic_stats['総販売数'].replace(' 個', '').replace(',', ''))
avg_price = float(basic_stats['平均価格'].replace('$', ''))
median_price = float(basic_stats['中央値価格'].replace('$', ''))
total_listings = int(basic_stats['総出品数'].replace(' 件', '').replace(',', ''))

# CV値を計算（価格データから）
print("📈 統計値を計算中...")

# Top10ブランドデータ
top10_brands = df_brands.head(10)
brand_labels = top10_brands['ブランド'].tolist()
brand_sales = top10_brands['販売数'].tolist()

# 駆動方式データ
drive_labels = df_drive['駆動方式'].tolist()
drive_sales = df_drive['販売数'].tolist()

# 価格帯データ（Top10のみ）
top10_price = df_price.sort_values('販売数', ascending=False).head(10)
price_labels = top10_price['価格帯'].tolist()
price_sales = top10_price['販売数'].tolist()

# Top20ブランドテーブル
top20_brands = df_brands.head(20)

print("🔨 新しいHTMLコンテンツを生成中...")

# 新しい全体分析タブのHTML生成
new_overall_html = f'''<div id="overview" class="tab-content" style="display: block;">
        <h2 class="section-title">📊 全体分析</h2>

        <!-- 基本統計 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総出品数</div>
                <div class="value">{total_listings:,} 件</div>
            </div>
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{total_sales:,} 個</div>
            </div>
            <div class="stat-card">
                <div class="label">平均価格</div>
                <div class="value">${avg_price:,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値価格</div>
                <div class="value">${median_price:,.2f}</div>
            </div>
        </div>

        <!-- 市場インサイト -->
        <div class="insights-section">
            <h3 class="section-title">💡 市場インサイト</h3>
            <div class="insight-card">
                <strong>📈 人気ブランド:</strong> {brand_labels[0]}が{brand_sales[0]:,}個で最多販売
            </div>
            <div class="insight-card">
                <strong>💰 価格帯:</strong> ${price_labels[0]}が最多販売（{price_sales[0]:,}個）
            </div>
            <div class="insight-card">
                <strong>⚙️ 駆動方式:</strong> {drive_labels[0]}が{drive_sales[0]:,}個で最多
            </div>
        </div>

        <!-- グラフセクション -->
        <h3 class="section-title">📊 市場分析グラフ</h3>
        <div class="charts-grid">
            <div class="chart-container">
                <div id="overall-brand-chart"></div>
            </div>
            <div class="chart-container">
                <div id="overall-drive-chart"></div>
            </div>
            <div class="chart-container">
                <div id="overall-price-chart"></div>
            </div>
        </div>

        <!-- Top20ブランドテーブル -->
        <h3 class="section-title">🏆 Top20ブランド</h3>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>ブランド</th>
                        <th>出品数</th>
                        <th>販売数</th>
                        <th>平均価格</th>
                        <th>中央値</th>
                    </tr>
                </thead>
                <tbody>
'''

# Top20ブランドの行を追加
for idx, row in top20_brands.iterrows():
    rank = idx + 1
    new_overall_html += f'''                    <tr>
                        <td>{rank}</td>
                        <td><strong>{row['ブランド']}</strong></td>
                        <td>{int(row['出品数']):,}</td>
                        <td>{int(row['販売数']):,}</td>
                        <td>${row['平均価格']:.2f}</td>
                        <td>${row['中央値']:.2f}</td>
                    </tr>
'''

new_overall_html += '''                </tbody>
            </table>
        </div>

        <!-- グラフ初期化スクリプト -->
        <script>
        (function() {
            // ブランド別販売数グラフ
            const brandData = [{
                x: ''' + json.dumps(brand_labels) + ''',
                y: ''' + json.dumps(brand_sales) + ''',
                type: 'bar',
                marker: {color: '#1976d2'}
            }];
            Plotly.newPlot('overall-brand-chart', brandData, {
                title: 'Top10ブランド別販売数',
                xaxis: {title: 'ブランド'},
                yaxis: {title: '販売数'}
            });

            // 駆動方式別分布グラフ
            const driveData = [{
                labels: ''' + json.dumps(drive_labels) + ''',
                values: ''' + json.dumps(drive_sales) + ''',
                type: 'pie'
            }];
            Plotly.newPlot('overall-drive-chart', driveData, {
                title: '駆動方式別分布'
            });

            // 価格帯別分布グラフ
            const priceData = [{
                x: ''' + json.dumps(price_labels) + ''',
                y: ''' + json.dumps(price_sales) + ''',
                type: 'bar',
                marker: {color: '#4caf50'}
            }];
            Plotly.newPlot('overall-price-chart', priceData, {
                title: 'Top10価格帯別販売数',
                xaxis: {title: '価格帯'},
                yaxis: {title: '販売数'}
            });
        })();
        </script>
    </div>'''

# HTMLファイル読み込み
print("📄 HTMLファイルを読み込み中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 全体分析タブの開始位置を特定
overall_start = html.find('<div id="overview"')
if overall_start == -1:
    print("❌ エラー: 全体分析タブが見つかりません")
    exit(1)

print(f"✅ 全体分析タブの開始位置: {overall_start}")

# 全体分析タブの終了位置を特定（ネストカウント）
div_count = 1
search_pos = html.find('>', overall_start) + 1

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        print("❌ エラー: 閉じタグが見つかりません")
        exit(1)

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            overall_end = next_close + 6  # len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✅ 全体分析タブの終了位置: {overall_end}")

# 挿入位置の確認
print("\n--- 挿入位置の前後 ---")
print(html[overall_start:overall_start+100])
print("...")
print(html[overall_end-50:overall_end+50])

# 置換
old_size = len(html) / 1024
html = html[:overall_start] + new_overall_html + html[overall_end:]
new_size = len(html) / 1024

print(f"\n📏 ファイルサイズ: {old_size:.1f}KB → {new_size:.1f}KB")

# 保存
print("💾 HTMLファイルを保存中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ 全体分析タブの更新が完了しました")
print(f"   更新内容:")
print(f"   - 総出品数: {total_listings:,} 件")
print(f"   - 総販売数: {total_sales:,} 個")
print(f"   - 平均価格: ${avg_price:.2f}")
print(f"   - 中央値: ${median_price:.2f}")
print(f"   - Top10ブランドグラフ")
print(f"   - 駆動方式分布グラフ")
print(f"   - 価格帯分布グラフ")
print(f"   - Top20ブランドテーブル")
