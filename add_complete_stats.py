#!/usr/bin/env python3
"""
全体分析タブに完品データの統計を追加
1. 完品データの統計カードを追加
2. 価格帯分布のタイトルに「完品のみ」を明記
"""

import pandas as pd

# CSVデータ読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_complete = df[df['商品状態'] == '完品'].copy()

# 完品データの統計
complete_count = len(df_complete)
complete_total = df_complete['価格'].sum()
complete_avg = df_complete['価格'].mean()
complete_median = df_complete['価格'].median()

print("=== 完品データ統計 ===")
print(f"総販売数: {complete_count:,}件")
print(f"総売上: ${complete_total:,.2f}")
print(f"平均価格: ${complete_avg:.2f}")
print(f"中央値: ${complete_median:.2f}")

# HTMLファイル読み込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"\n=== HTMLファイル読み込み ===")
print(f"ファイルサイズ: {len(html)}文字")

# 1. 価格帯分布のタイトルに「完品のみ」を追加
print("\n=== 価格帯分布のタイトルを修正 ===")
old_title = '<h2 class="section-title">💰 価格帯分布</h2>'
new_title = '<h2 class="section-title">💰 価格帯分布（完品のみ）</h2>'

if old_title in html:
    html = html.replace(old_title, new_title)
    print("✅ 価格帯分布のタイトルに「完品のみ」を追加しました")
else:
    print("❌ 価格帯分布のタイトルが見つかりません")

# グラフのタイトルも修正
old_graph_title = "title: '価格帯分布（50ドル刻み）'"
new_graph_title = "title: '価格帯分布（完品のみ・50ドル刻み）'"

if old_graph_title in html:
    html = html.replace(old_graph_title, new_graph_title)
    print("✅ グラフタイトルに「完品のみ」を追加しました")
else:
    print("⚠️ グラフタイトルが見つかりませんでした")

# 2. 完品データの統計カードセクションを追加
print("\n=== 完品データの統計カードセクションを追加 ===")

# 挿入位置: ブランド別分析の直前
insert_marker = '<h2 class="section-title">🏷️ ブランド別分析（Top20）</h2>'
insert_pos = html.find(insert_marker)

if insert_pos == -1:
    print("❌ 挿入位置が見つかりません")
else:
    # 完品データの統計カードセクション
    complete_stats_section = f'''
        <h2 class="section-title">📦 完品データ統計</h2>
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

    # セクションを挿入
    html = html[:insert_pos] + complete_stats_section + html[insert_pos:]
    print(f"✅ 完品データの統計カードセクションを追加しました（{insert_pos}文字目）")

# HTMLファイルを保存
print("\n=== HTMLファイルを保存 ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTMLファイルを保存しました（{len(html)}文字）")

print("\n=== 完了 ===")
print("✅ 完品データの統計カードセクションを追加")
print("✅ 価格帯分布のタイトルに「完品のみ」を追加")
