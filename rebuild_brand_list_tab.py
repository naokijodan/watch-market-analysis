#!/usr/bin/env python3
"""
ブランド一覧タブの修正スクリプト
1. 販売数を正しく集計（データ数 → 総販売数）
2. リンク表示を改善
"""
import pandas as pd
import json
from datetime import datetime
from urllib.parse import quote

print("=" * 80)
print("ブランド一覧タブの修正")
print("=" * 80)

# 1. CSVから正しい集計
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# ブランド別の総販売数を集計
brand_sales = df.groupby('ブランド')['販売数'].sum().sort_values(ascending=False)
total_sales = brand_sales.sum()
total_brands = len(brand_sales)
avg_sales = brand_sales.mean()

print(f"\n総ブランド数: {total_brands}個")
print(f"総販売数: {total_sales:,}個")
print(f"平均販売数/ブランド: {avg_sales:.1f}個")

# 2. ブランドデータ準備
brands_data = []
for rank, (brand, sales) in enumerate(brand_sales.items(), 1):
    ratio = (sales / total_sales) * 100

    # 検索リンク生成
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(brand)}+Watch&LH_Sold=1&LH_Complete=1"
    mercari_url = f"https://jp.mercari.com/search?keyword={quote(brand)}%20時計&status=on_sale"

    brands_data.append({
        'rank': rank,
        'brand': brand,
        'sales': sales,
        'ratio': ratio,
        'ebay_url': ebay_url,
        'mercari_url': mercari_url
    })

# 3. HTMLテンプレート生成

# 3.1 基本統計カード（修正）
stats_html = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <div class="icon">🏷️</div>
            <div class="value">{total_brands}</div>
            <div class="label">総ブランド数</div>
        </div>
        <div class="stat-card">
            <div class="icon">📊</div>
            <div class="value">{total_sales:,}</div>
            <div class="label">総販売数</div>
        </div>
        <div class="stat-card">
            <div class="icon">📈</div>
            <div class="value">{avg_sales:.1f}</div>
            <div class="label">平均販売数/ブランド</div>
        </div>
    </div>
'''

# 3.2 検索ボックス
search_box_html = '''
    <div style="margin-bottom: 20px;">
        <input type="text" id="brandSearch" placeholder="🔍 ブランド名で検索..."
               onkeyup="filterBrands()"
               style="width: 100%; max-width: 400px; padding: 10px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-card); color: var(--text-primary);">
    </div>
'''

# 3.3 テーブル生成（リンク表示を改善）
table_rows = []
for brand in brands_data:
    row = f'''        <tr>
            <td>{brand['rank']}</td>
            <td><strong>{brand['brand']}</strong></td>
            <td>{brand['sales']:,}</td>
            <td>{brand['ratio']:.2f}%</td>
            <td style="white-space: nowrap;">
                <a href="{brand['ebay_url']}" target="_blank" class="link-btn link-ebay" style="font-size: 0.75em; padding: 4px 8px;">eBay</a>
                <input type="checkbox" class="search-checkbox" style="margin: 0 4px;">
                <a href="{brand['mercari_url']}" target="_blank" class="link-btn link-mercari" style="font-size: 0.75em; padding: 4px 8px;">メルカリ</a>
                <input type="checkbox" class="search-checkbox" style="margin: 0 4px;">
            </td>
        </tr>'''
    table_rows.append(row)

table_html = f'''
    <div class="table-container">
        <table id="brandsTable">
            <thead>
                <tr>
                    <th onclick="sortBrandsTable('rank')" style="cursor: pointer;">ランク ▼</th>
                    <th onclick="sortBrandsTable('brand')" style="cursor: pointer;">ブランド名</th>
                    <th onclick="sortBrandsTable('sales')" style="cursor: pointer;">販売数</th>
                    <th>比率</th>
                    <th>検索</th>
                </tr>
            </thead>
            <tbody id="brandsTableBody">
{''.join(table_rows)}
            </tbody>
        </table>
    </div>
'''

# 3.4 上位30ブランドのPlotlyグラフデータ
top30 = brands_data[:30]
graph_data = {
    'brands': [b['brand'] for b in top30],
    'sales': [b['sales'] for b in top30]
}

graph_html = f'''
    <div class="chart-container">
        <h3>📊 上位30ブランド販売数</h3>
        <div id="brandsChart"></div>
    </div>

    <script>
    var brandsChartData = {{
        x: {json.dumps(graph_data['brands'])},
        y: {json.dumps(graph_data['sales'])},
        type: 'bar',
        marker: {{color: '#1976D2'}}
    }};

    var brandsChartLayout = {{
        height: 500,
        margin: {{l: 100, r: 50, t: 30, b: 120}},
        xaxis: {{tickangle: -45, automargin: true}},
        yaxis: {{title: '販売数'}},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    }};

    Plotly.newPlot('brandsChart', [brandsChartData], brandsChartLayout, {{responsive: true}});
    </script>
'''

# 3.5 ソート・検索機能のJavaScript（修正: count → sales）
js_functions = '''
<script>
// ブランドテーブルのソート機能
var brandsSortOrder = {rank: 'asc', brand: 'asc', sales: 'desc'};
var currentBrandsSortColumn = 'rank';

function sortBrandsTable(column) {
    var table = document.getElementById('brandsTable');
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));

    // ソート方向を切り替え
    if (currentBrandsSortColumn === column) {
        brandsSortOrder[column] = brandsSortOrder[column] === 'asc' ? 'desc' : 'asc';
    }
    currentBrandsSortColumn = column;

    rows.sort(function(a, b) {
        var aVal, bVal;

        if (column === 'rank' || column === 'sales') {
            var colIndex = column === 'rank' ? 0 : 2;
            aVal = parseInt(a.cells[colIndex].textContent.replace(/,/g, ''));
            bVal = parseInt(b.cells[colIndex].textContent.replace(/,/g, ''));
        } else {
            aVal = a.cells[1].textContent.trim();
            bVal = b.cells[1].textContent.trim();
        }

        if (brandsSortOrder[column] === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    // テーブルを再構築
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

// ブランド検索フィルター
function filterBrands() {
    var input = document.getElementById('brandSearch').value.toLowerCase();
    var tbody = document.getElementById('brandsTableBody');
    var rows = tbody.getElementsByTagName('tr');

    for (var i = 0; i < rows.length; i++) {
        var brandName = rows[i].cells[1].textContent.toLowerCase();
        if (brandName.includes(input)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}
</script>
'''

# 3.6 タブコンテンツ全体
new_tab_content = f'''
    <div id="brands" class="tab-content">
        <h2 class="section-title">🏷️ ブランド一覧（全{total_brands}ブランド）</h2>
{stats_html}
{search_box_html}
        <h3>🏆 全ブランドリスト</h3>
{table_html}
{graph_html}
    </div>
{js_functions}
'''

# 4. 既存HTMLから古いbrandsタブを削除して新しいものに置換
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 古いbrandsタブの開始位置を特定
old_brands_start = html.find('<div id="brands" class="tab-content">')
if old_brands_start == -1:
    print("\n❌ エラー: brandsタブが見つかりません")
    exit(1)

# ネストカウントで終了位置を特定
div_count = 1
search_pos = old_brands_start + len('<div id="brands" class="tab-content">')

while div_count > 0 and search_pos < len(html):
    next_open = html.find('<div', search_pos)
    next_close = html.find('</div>', search_pos)

    if next_close == -1:
        break

    if next_open != -1 and next_open < next_close:
        div_count += 1
        search_pos = next_open + 4
    else:
        div_count -= 1
        if div_count == 0:
            old_brands_end = next_close + 6
            break
        else:
            search_pos = next_close + 6

# JavaScript関数部分も含める必要がある
# </div>の後の<script>...</script>も削除対象
js_start = html.find('<script>', old_brands_end)
if js_start != -1 and js_start < old_brands_end + 100:
    # <script>から次の</script>までを探す
    js_end = html.find('</script>', js_start) + len('</script>')
    old_brands_end = js_end

print(f"\n古いbrandsタブの範囲: {old_brands_start} → {old_brands_end}")

# 5. バックアップ作成
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"/Users/naokijodan/Desktop/watch-market-analysis/index.html.backup_{timestamp}"
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ バックアップ作成: {backup_file}")

# 6. 置換実行
html = html[:old_brands_start] + new_tab_content + html[old_brands_end:]

# 7. ファイルに書き込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ brandsタブを修正しました")
print(f"✅ 総販売数: {total_sales:,}個")
print(f"✅ リンク表示: 「eBay」「メルカリ」ボタンに変更")

print("\n" + "=" * 80)
print("ブラウザで確認してください: http://localhost:8000")
print("=" * 80)
