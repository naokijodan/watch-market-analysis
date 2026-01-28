#!/usr/bin/env python3
"""
月別販売数推移セクションを復元
"""

# HTMLファイル読み込み
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("=== HTMLファイル読み込み ===")
print(f"ファイルサイズ: {len(html)}文字")

# 1. 価格帯分布セクションの前に月別販売数推移セクションを追加
print("\n=== 月別販売数推移セクションを追加 ===")

insert_marker = '<h2 class="section-title">💰 価格帯分布（完品のみ）</h2>'
insert_pos = html.find(insert_marker)

if insert_pos == -1:
    print("❌ 挿入位置が見つかりません")
    exit(1)

# 月別販売数推移セクション
monthly_section = '''
        <h2 class="section-title">📅 月別販売数推移</h2>
        <div class="chart-container"><div id="monthlyTrendChart"></div></div>

        '''

html = html[:insert_pos] + monthly_section + html[insert_pos:]
print(f"✅ 月別販売数推移セクションを追加しました（{insert_pos}文字目）")

# 2. drawMonthlyTrendChart関数を追加
print("\n=== drawMonthlyTrendChart関数を追加 ===")

# 価格帯分布関数の直前に挿入
function_marker = '// 価格帯分布（50ドル刻み）'
function_pos = html.find(function_marker)

if function_pos == -1:
    print("❌ 関数挿入位置が見つかりません")
    exit(1)

# 月別販売数推移関数
monthly_function = '''
    // 月別販売数推移
    function drawMonthlyTrendChart() {
        const months = ["2025-12", "2026-01"];
        const movementData = {};

        // 各駆動方式ごとのデータを準備
        [{"month": "2025-12", "data": {"クオーツ": 159, "スマートウォッチ": 2, "ソーラー": 45, "デジタル": 26, "不明": 146, "手巻き": 17, "自動巻": 63}}, {"month": "2026-01", "data": {"クオーツ": 2841, "スマートウォッチ": 29, "ソーラー": 878, "デジタル": 278, "不明": 2984, "手巻き": 254, "自動巻": 1553}}].forEach(item => {
            Object.keys(item.data).forEach(movement => {
                if (!movementData[movement]) movementData[movement] = [];
            });
        });

        Object.keys(movementData).forEach(movement => {
            [{"month": "2025-12", "data": {"クオーツ": 159, "スマートウォッチ": 2, "ソーラー": 45, "デジタル": 26, "不明": 146, "手巻き": 17, "自動巻": 63}}, {"month": "2026-01", "data": {"クオーツ": 2841, "スマートウォッチ": 29, "ソーラー": 878, "デジタル": 278, "不明": 2984, "手巻き": 254, "自動巻": 1553}}].forEach(item => {
                movementData[movement].push(item.data[movement] || 0);
            });
        });

        const traces = Object.keys(movementData).map(movement => ({
            x: months,
            y: movementData[movement],
            name: movement,
            type: 'scatter',
            mode: 'lines+markers',
            stackgroup: 'one'
        }));

        const layout = {...plotlyLayout, title: '月別販売数推移（完品のみ）', xaxis: {title: '年月'}, yaxis: {title: '販売数'}};
        Plotly.newPlot('monthlyTrendChart', traces, layout, plotlyConfig);
    }

    '''

html = html[:function_pos] + monthly_function + html[function_pos:]
print(f"✅ drawMonthlyTrendChart関数を追加しました（{function_pos}文字目）")

# 3. initCharts関数にdrawMonthlyTrendChart()呼び出しを追加
print("\n=== initCharts関数にdrawMonthlyTrendChart()呼び出しを追加 ===")

# drawPriceDistChart()の直前に追加
call_marker = '        drawPriceDistChart();'
call_pos = html.find(call_marker)

if call_pos == -1:
    print("❌ 関数呼び出し挿入位置が見つかりません")
    exit(1)

monthly_call = '        drawMonthlyTrendChart();\n'
html = html[:call_pos] + monthly_call + html[call_pos:]
print(f"✅ drawMonthlyTrendChart()呼び出しを追加しました（{call_pos}文字目）")

# HTMLファイルを保存
print("\n=== HTMLファイルを保存 ===")
with open('/Users/naokijodan/Desktop/watch-market-analysis/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTMLファイルを保存しました（{len(html)}文字）")

print("\n=== 完了 ===")
print("✅ 月別販売数推移セクションを復元")
print("✅ drawMonthlyTrendChart関数を追加")
print("✅ 関数呼び出しを追加")
