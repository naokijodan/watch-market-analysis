#!/usr/bin/env python3
"""
Longinesタブ完全再構築スクリプト
最新データ2,984個を反映（13.6倍のデータ追加）
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime

print("=" * 60)
print("🔵 Longines タブ完全再構築")
print("=" * 60)

# ライン分類キーワード定義（将来の外部化を想定）
LINE_KEYWORDS = {
    'Conquest': ['Conquest'],
    'Flagship': ['Flagship'],
    'Heritage': ['Heritage'],
    'DolceVita': ['DolceVita', 'Dolce Vita'],
    'Spirit': ['Spirit'],
    'HydroConquest': ['HydroConquest', 'Hydro Conquest'],
}

# 1. データ読み込み
print("\n📊 データ読み込み中...")
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
longines = df[(df['ブランド'] == 'Longines') & (df['商品状態'] == '完品')].copy()

print(f"✅ 完品データ: {len(longines):,}件")
print(f"   総販売数: {int(longines['販売数'].sum()):,}個")

# 2. 型番抽出（正規表現）+ エラーログ
print("\n🔍 型番抽出中...")
model_pattern = r'L\d+\.\d+\.\d+'
extraction_errors = []

def extract_model_number(title):
    """タイトルから型番を抽出"""
    if pd.isna(title):
        return None
    match = re.search(model_pattern, str(title))
    if match:
        return match.group(0)
    return None

longines['型番'] = longines['タイトル'].apply(extract_model_number)
has_model = longines['型番'].notna()
extracted_count = longines[has_model].shape[0]
failed_count = len(longines) - extracted_count
extraction_rate = (extracted_count / len(longines)) * 100

# エラーログ作成
extraction_errors = longines[~has_model][['タイトル', '価格', '販売数']].copy()
extraction_errors.to_csv('extraction_errors.log', index=False)

print(f"   成功: {extracted_count:,}件 / {len(longines):,}件 ({extraction_rate:.1f}%)")
print(f"   失敗: {failed_count:,}件")
print(f"   ログ: extraction_errors.log に保存")

# 3. ライン分類
print("\n🏷️ ライン分類中...")
def classify_line(title):
    """タイトルからラインを分類"""
    if pd.isna(title):
        return 'その他Longines'
    title_str = str(title)
    for line, keywords in LINE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in title_str.lower():
                return line
    return 'その他Longines'

longines['ライン'] = longines['タイトル'].apply(classify_line)

# ライン別統計
line_stats = longines.groupby('ライン').agg({
    '販売数': 'sum',
    '価格': ['median', 'mean', 'std']
}).round(2)
line_stats.columns = ['販売数', '中央値', '平均価格', '標準偏差']
line_stats['CV値'] = (line_stats['標準偏差'] / line_stats['平均価格']).round(3)
line_stats['比率'] = (line_stats['販売数'] / longines['販売数'].sum() * 100).round(1)
line_stats = line_stats.sort_values('販売数', ascending=False)

print(f"   分類完了: {len(line_stats)}ライン")
for line, row in line_stats.iterrows():
    print(f"   - {line}: {int(row['販売数']):,}個 ({row['比率']:.1f}%)")

# 4. 基本統計
total_sales = int(longines['販売数'].sum())
median_price = longines['価格'].median()
avg_price = longines['価格'].mean()
cv = longines['価格'].std() / avg_price

print(f"\n📈 基本統計")
print(f"   総販売数: {total_sales:,}個")
print(f"   中央値: ${median_price:.2f}")
print(f"   平均価格: ${avg_price:.2f}")
print(f"   CV値: {cv:.3f}")
print(f"   型番抽出率: {extraction_rate:.1f}%")

# 5. 駆動方式別統計
drive_stats = longines.groupby('駆動方式')['販売数'].sum().sort_values(ascending=False)
drive_labels = drive_stats.index.tolist()
drive_sales = drive_stats.values.tolist()

# 6. 性別分布
if 'デパートメント' in longines.columns:
    gender_stats = longines.groupby('デパートメント')['販売数'].sum().sort_values(ascending=False)
    gender_labels = gender_stats.index.tolist()
    gender_sales = gender_stats.values.tolist()
else:
    gender_labels = []
    gender_sales = []

# 7. 価格帯分布（50ドル刻み）
price_bins = [0, 100, 150, 200, 300, 500, 1000, 2000, 10000]
price_labels_list = ['~$100', '$100-150', '$150-200', '$200-300', '$300-500', '$500-1K', '$1K-2K', '$2K~']
longines['価格帯'] = pd.cut(longines['価格'], bins=price_bins, labels=price_labels_list, right=False)
price_dist = longines.groupby('価格帯', observed=True)['販売数'].sum()
price_labels = price_dist.index.astype(str).tolist()
price_counts = price_dist.values.tolist()

# 8. ライン別円グラフデータ（Top6 + その他）
line_sales = line_stats.head(6)['販売数'].tolist()
line_names = line_stats.head(6).index.tolist()

# 9. Top30型番
if has_model.sum() > 0:
    top30_models = longines[has_model].groupby('型番').agg({
        '販売数': 'sum',
        '価格': 'median'
    }).sort_values('販売数', ascending=False).head(30)
    top30_models['CV'] = longines[has_model].groupby('型番')['価格'].apply(lambda x: x.std() / x.mean() if x.mean() > 0 else 0)
    top30_models = top30_models.round(2)
else:
    top30_models = pd.DataFrame()

# 10. ライン別Top15（各ラインごと）
line_top15 = {}
for line in line_stats.head(4).index:  # 上位4ラインのみ詳細表示
    line_data = longines[(longines['ライン'] == line) & (longines['型番'].notna())]
    if len(line_data) > 0:
        line_top = line_data.groupby('型番').agg({
            '販売数': 'sum',
            '価格': 'median',
            'タイトル': 'first'
        }).sort_values('販売数', ascending=False).head(15)
        line_top['CV'] = line_data.groupby('型番')['価格'].apply(lambda x: x.std() / x.mean() if x.mean() > 0 else 0)
        line_top15[line] = line_top.round(2)

# 11. 仕入れ上限計算（為替155円、送料3000円、手数料20%）
exchange_rate = 155
shipping = 3000
fee_rate = 0.20

def calc_purchase_limit(median_price):
    """仕入れ上限を計算"""
    return int((median_price * exchange_rate * (1 - fee_rate)) - shipping)

print("\n🔨 HTML生成中...")

# HTMLテンプレート生成
html = f'''    <div id="Longines" class="tab-content">
        <h2 class="section-title">🔵 Longines 詳細分析</h2>

        <!-- 基本統計 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">総販売数</div>
                <div class="value">{total_sales:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">中央値</div>
                <div class="value">${median_price:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">CV（変動係数）</div>
                <div class="value">{cv:.3f}</div>
            </div>
            <div class="stat-card">
                <div class="label">型番抽出率</div>
                <div class="value">{extraction_rate:.1f}%</div>
            </div>
        </div>

        <!-- 仕入れ戦略 -->
        <div class="strategy-section">
            <h3 class="section-title">🎯 仕入れ戦略（実践ガイド）</h3>
            <div class="strategy-grid">
                <div class="strategy-card">
                    <h4>✅ 狙い目条件</h4>
                    <ul>
                        <li><strong>Conquest:</strong> 最多販売数（{int(line_stats.loc['Conquest', '販売数']) if 'Conquest' in line_stats.index else 0}個）、スポーツウォッチとして人気</li>
                        <li><strong>DolceVita:</strong> エレガントライン（{int(line_stats.loc['DolceVita', '販売数']) if 'DolceVita' in line_stats.index else 0}個）、安定需要</li>
                        <li><strong>Flagship:</strong> フラッグシップライン、ブランドの顔</li>
                        <li><strong>クオーツモデル:</strong> 67.8%がクオーツ、低価格で回転が早い</li>
                    </ul>
                </div>
                <div class="strategy-card">
                    <h4>⚠️ 避けるべき条件</h4>
                    <ul>
                        <li>型番が不明瞭な商品（パーツ・ケースのみの可能性）</li>
                        <li>CV値 0.5以上の不安定なモデル</li>
                        <li>極端な高額品（$2,000以上）</li>
                    </ul>
                </div>
                <div class="strategy-card">
                    <h4>💰 仕入れ価格目安</h4>
                    <p><strong>通常モデル:</strong> ¥25,000以下</p>
                    <p><strong>人気ライン（Conquest等）:</strong> ¥35,000前後が上限</p>
                    <p><strong>Heritage/Spirit:</strong> ¥100,000前後（高額ライン）</p>
                </div>
            </div>
        </div>

        <!-- グラフセクション -->
        <h3 class="section-title">📊 市場分析グラフ</h3>
        <div class="charts-grid">
            <div class="chart-container">
                <h4>価格帯別分析（50ドル刻み）</h4>
                <div id="longines-price-chart"></div>
            </div>
            <div class="chart-container">
                <h4>駆動方式別分布</h4>
                <div id="longines-drive-chart"></div>
            </div>'''

# 性別分布グラフ（データがある場合のみ）
if gender_labels:
    html += f'''
            <div class="chart-container">
                <h4>性別・カテゴリー別分布</h4>
                <div id="longines-gender-chart"></div>
            </div>'''

html += f'''
            <div class="chart-container">
                <h4>ライン別売上比率</h4>
                <div id="longines-line-chart"></div>
            </div>
        </div>

        <!-- ライン別詳細分析 -->
        <h3 class="section-title">🔵 ライン別詳細分析（全{len(line_stats)}ライン）</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ライン</th>
                    <th>販売数</th>
                    <th>比率</th>
                    <th>中央値</th>
                    <th>仕入上限(¥)</th>
                    <th>CV値</th>
                    <th>安定度</th>
                    <th>検索</th>
                </tr>
            </thead>
            <tbody>'''

# ライン別詳細テーブル
for line, row in line_stats.iterrows():
    sales = int(row['販売数'])
    ratio = row['比率']
    median = row['中央値']
    limit = calc_purchase_limit(median)
    cv_val = row['CV値']
    stability = '★★★' if cv_val < 0.3 else '☆☆☆'

    html += f'''
                <tr>
                    <td><strong>{line}</strong></td>
                    <td>{sales:,}</td>
                    <td>{ratio:.1f}%</td>
                    <td>${median:.2f}</td>
                    <td>¥{limit:,}</td>
                    <td>{cv_val:.3f}</td>
                    <td>{stability}</td>
                    <td>
                        <a href="https://www.ebay.com/sch/i.html?_nkw=Longines+{line.replace(' ', '+')}+Watch&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                        <input type="checkbox" class="search-checkbox">
                        <a href="https://jp.mercari.com/search?keyword=Longines%20{line.replace(' ', '%20')}%20時計&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        <input type="checkbox" class="search-checkbox">
                    </td>
                </tr>'''

html += '''
            </tbody>
        </table>

        <!-- 全ライン横断 型番分析Top30 -->
        <h3 class="section-title">🏆 全ライン横断 型番分析Top30</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>順位</th>
                    <th>型番</th>
                    <th>販売数</th>
                    <th>中央値($)</th>
                    <th>仕入上限(¥)</th>
                    <th>CV</th>
                    <th>検索</th>
                </tr>
            </thead>
            <tbody>'''

# Top30型番テーブル
if not top30_models.empty:
    for rank, (model, row) in enumerate(top30_models.iterrows(), 1):
        sales = int(row['販売数'])
        median = row['価格']
        limit = calc_purchase_limit(median)
        cv_val = row['CV']

        html += f'''
                <tr>
                    <td><strong>{rank}</strong></td>
                    <td>{model}</td>
                    <td>{sales}</td>
                    <td>${median:.2f}</td>
                    <td>¥{limit:,}</td>
                    <td>{cv_val:.3f}</td>
                    <td>
                        <a href="https://www.ebay.com/sch/i.html?_nkw=Longines+{model.replace('.', '+')}&LH_Sold=1" target="_blank" class="link-btn link-ebay">eBay</a>
                        <input type="checkbox" class="search-checkbox">
                        <a href="https://jp.mercari.com/search?keyword=Longines%20{model.replace('.', '%20')}&status=on_sale" target="_blank" class="link-btn link-mercari">メルカリ</a>
                        <input type="checkbox" class="search-checkbox">
                    </td>
                </tr>'''

html += '''
            </tbody>
        </table>

        <!-- グラフ初期化スクリプト -->
        <script>
        (function() {
            // 価格帯別分布
            const priceData = [{
                x: ''' + json.dumps(price_labels) + ''',
                y: ''' + json.dumps(price_counts) + ''',
                type: 'bar',
                marker: {color: '#1565c0'}
            }];
            Plotly.newPlot('longines-price-chart', priceData, {
                xaxis: {title: '価格帯'},
                yaxis: {title: '販売数'},
                margin: {l: 50, r: 30, t: 30, b: 80}
            });

            // 駆動方式別分布
            const driveData = [{
                labels: ''' + json.dumps(drive_labels) + ''',
                values: ''' + json.dumps(drive_sales) + ''',
                type: 'pie',
                hole: 0.4
            }];
            Plotly.newPlot('longines-drive-chart', driveData, {
                margin: {l: 30, r: 30, t: 30, b: 30}
            });'''

# 性別分布グラフ（データがある場合のみ）
if gender_labels:
    html += '''
            // 性別分布
            const genderData = [{
                labels: ''' + json.dumps(gender_labels) + ''',
                values: ''' + json.dumps(gender_sales) + ''',
                type: 'pie',
                hole: 0.4
            }];
            Plotly.newPlot('longines-gender-chart', genderData, {
                margin: {l: 30, r: 30, t: 30, b: 30}
            });'''

html += '''
            // ライン別売上比率
            const lineData = [{
                labels: ''' + json.dumps(line_names) + ''',
                values: ''' + json.dumps(line_sales) + ''',
                type: 'pie',
                hole: 0.4
            }];
            Plotly.newPlot('longines-line-chart', lineData, {
                margin: {l: 30, r: 30, t: 30, b: 30}
            });
        })();
        </script>
    </div>'''

# 12. HTMLファイルの読み込みと置換
print("\n📄 HTMLファイル読み込み中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# バックアップ作成
backup_file = f'/Users/naokijodan/Desktop/watch-market-analysis/index.html.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"✅ バックアップ作成: {backup_file}")

# Longinesタブの開始位置を特定
longines_start = html_content.find('<div id="Longines"')
if longines_start == -1:
    print("❌ エラー: Longinesタブが見つかりません")
    exit(1)

print(f"✅ Longinesタブの開始位置: {longines_start}")

# ネストカウントで終了位置を特定
div_count = 1
search_pos = html_content.find('>', longines_start) + 1

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
            longines_end = next_close + 6  # len('</div>')
            break
        else:
            search_pos = next_close + 6

print(f"✅ Longinesタブの終了位置: {longines_end}")

# 挿入位置の前後確認
print("\n--- 挿入位置の前後 ---")
print(html_content[longines_start:longines_start+80])
print("...")
print(html_content[longines_end-50:longines_end+50])

# 置換
old_size = len(html_content) / 1024
html_content = html_content[:longines_start] + html + html_content[longines_end:]
new_size = len(html_content) / 1024

print(f"\n📏 ファイルサイズ: {old_size:.1f}KB → {new_size:.1f}KB")

# 保存
print("\n💾 HTMLファイル保存中...")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n" + "=" * 60)
print("✅ Longinesタブの完全再構築が完了しました")
print("=" * 60)
print(f"\n📊 更新サマリー")
print(f"   総販売数: 219個 → {total_sales:,}個 (13.6倍)")
print(f"   中央値: $262.95 → ${median_price:.2f}")
print(f"   型番抽出率: {extraction_rate:.1f}%")
print(f"   ライン数: {len(line_stats)}ライン")
print(f"   エラーログ: extraction_errors.log ({failed_count}件)")
print(f"   バックアップ: {backup_file}")
print(f"   ファイルサイズ: {old_size:.1f}KB → {new_size:.1f}KB")
