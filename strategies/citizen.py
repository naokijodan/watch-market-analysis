#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CITIZEN戦略クラス
"""
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base import AbstractBrandStrategy

# CITIZENライン定義
CITIZEN_LINES = {
    # メインライン
    'Promaster': [
        'PROMASTER', 'PRO MASTER',
        'SKY', 'LAND', 'MARINE',
        'BN0', 'BJ7', 'BN2', 'BN4', 'JY8', 'CB5', 'AS7',
        'PMV', 'PMD', 'PMK',
    ],
    'Eco-Drive': [
        'ECO-DRIVE', 'ECO DRIVE',
        'ECODRIVE',
        'E870', 'E168', 'E111',
        'AT8', 'AT0', 'AW1', 'BM6', 'BM7', 'BM8',
    ],
    'Attesa': [
        'ATTESA',
        'AT8040', 'AT8185', 'AT8144',
        'CC', 'CB', 'AT',
    ],
    'Exceed': [
        'EXCEED',
        'AS7', 'ES9', 'ES8', 'EB',
        'EBG', 'EBD',
    ],
    'Campanola': [
        'CAMPANOLA',
        'CTR', 'AH7', 'AH4', 'BZ',
    ],
    'The CITIZEN': [
        'THE CITIZEN',
        'AQ4', 'AQ1', 'CTQ',
    ],
    # 特殊シリーズ
    'ANA-DIGI TEMP': [
        'ANA-DIGI TEMP', 'ANA DIGI TEMP',
        'ANADIGI TEMP', 'ANADIGITEMP',
        'JG2', 'JM0',
    ],
    'Tsuyosa': [
        'TSUYOSA',
        'NK0', 'NJ0', 'C7',
    ],
    'Nighthawk': [
        'NIGHTHAWK', 'NIGHT HAWK',
        'BJ7', 'CA4', 'CB5',
    ],
    'Chronomaster': [
        'CHRONOMASTER', 'CHRONO MASTER',
        'AQ4', 'AV0',
    ],
    'Satellite Wave': [
        'SATELLITE WAVE', 'SATELLITE-WAVE',
        'CC3', 'CC9', 'F100', 'F150', 'F900',
    ],
    # ヴィンテージ/その他
    'Seven Star': [
        'SEVEN STAR', 'SEVEN-STAR',
        'SEVENSTAR', '7-STAR',
    ],
    'Cosmotron': ['COSMOTRON'],
    'Leopard': ['LEOPARD'],
    'Homer Date': [
        'HOMER DATE', 'HOMERDATE',
        'HOMER',
    ],
    'OXY': [
        'OXY',
        '5508', '5509',
    ],
    'Crystron': ['CRYSTRON'],
    'FORMA': [
        'FORMA',
        'FRA', 'FRD',
    ],
    'xC': [
        'XC ', ' XC', 'X-C',
        'EC1', 'ES9',
    ],
    'wicca': [
        'WICCA',
        'KL0', 'KP2', 'KS1',
    ],
}

# キャラクター/コラボキーワード
CHARACTER_KEYWORDS = [
    'COLLABORATION', 'COLLAB',
    # 企業コラボ
    ' ANA ', 'ANA-', 'ANA ORIGINAL', 'ANA COCKPIT',
    'HONDA', 'TOYOTA', 'NISSAN', 'MAZDA',
    'BLUE ANGELS',
    # キャラクター
    'DISNEY', 'MICKEY', 'MINNIE',
    'HELLO KITTY', 'KITTY', 'SANRIO',
    'SNOOPY', 'PEANUTS', 'WOODSTOCK',
    # アニメ・ゲーム
    'FINAL FANTASY', 'FFXIV', 'FF14',
    'GUNDAM',
    'EVANGELION', ' EVA ',
    'ONE PIECE', 'NARUTO',
    ' 86 ', 'EIGHTY SIX', '86 COLLABORATION',
    # その他
    'MARVEL', 'STAR WARS',
    'LIMITED EDITION', 'SPECIAL EDITION', 'EXCLUSIVE',
]


class CITIZENStrategy(AbstractBrandStrategy):
    """CITIZEN戦略クラス"""

    def extract_model_number(self, title_upper):
        """型番抽出（CITIZEN用）"""
        # パターン1: アルファベット+数字+ハイフン+数字
        pattern1 = r'\b[A-Z]{2,3}\d{4}-\d{2}[A-Z]{0,2}\b'
        match1 = re.search(pattern1, title_upper)
        if match1:
            candidate = match1.group()
            if candidate not in ['CITIZEN']:
                return candidate

        # パターン2: 4桁-5桁（ヴィンテージ用）
        pattern2 = r'\b\d{4}-\d{5,6}\b'
        match2 = re.search(pattern2, title_upper)
        if match2:
            return match2.group()

        return "N/A"

    def classify_line(self, row):
        """ライン分類（CITIZEN用）"""
        title_upper = row['TITLE_UPPER']

        for line_name, keywords in CITIZEN_LINES.items():
            for kw in keywords:
                if kw in title_upper:
                    return line_name

        return 'その他CITIZEN'

    def is_character_collab(self, title_upper):
        """キャラクター/コラボ判定"""
        for kw in CHARACTER_KEYWORDS:
            if kw in title_upper:
                return True
        return False

    def generate_top30_html(self):
        """Top30テーブルHTML生成（検索リンク＋チェックボックス付き）"""
        from utils.common import format_price, generate_search_link_html

        top30 = self.stats['top30'].head(30)

        rows_html = []
        for idx, (model, row) in enumerate(top30.iterrows(), 1):
            sales = int(row['販売数'])
            median_price = row['価格']

            # 検索リンク＋チェックボックス
            search_links = generate_search_link_html(
                brand='CITIZEN',
                keyword=model,
                link_type='model',
                include_checkbox=True
            )

            row_html = f'''
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{model}</strong></td>
                        <td>{sales}</td>
                        <td>{format_price(median_price)}</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>'''
            rows_html.append(row_html)

        table_html = f'''
        <h3 class="section-title" style="color: #1565c0;">🏆 Top30人気モデル（中央値ベース）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>型番</th>
                        <th>販売数</th>
                        <th>中央値</th>
                        <th>仕入れ先検索</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        '''

        return table_html

    def generate_graphs_html(self):
        """グラフHTML生成（価格帯別、ライン別）"""
        import json
        from utils.common import aggregate_top_lines

        # 価格帯別データ
        price_ranges = self.stats['price_ranges']
        price_labels = price_ranges.index.tolist()
        price_values = price_ranges.values.tolist()

        # ライン別データ（Top7 + その他）
        line_stats = self.stats['line_stats']
        line_sales = line_stats['販売数'].sort_values(ascending=False)
        line_sales_aggregated = aggregate_top_lines(line_sales, top_n=7, others_label="その他")

        line_labels = line_sales_aggregated.index.tolist()
        line_values = line_sales_aggregated.values.tolist()

        graphs_html = f'''
        <h3 class="section-title" style="color: #1565c0;">📊 グラフ分析</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px;">

            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #1565c0; margin-bottom: 15px;">価格帯別販売分布</h4>
                <div id="citizen_price_chart" style="height: 350px;"></div>
            </div>

            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #1565c0; margin-bottom: 15px;">ライン別売上比率</h4>
                <div id="citizen_line_chart" style="height: 350px;"></div>
            </div>

        </div>

        <script>
        // 価格帯別棒グラフ
        Plotly.newPlot('citizen_price_chart', [{{
            x: {json.dumps(price_labels, ensure_ascii=False)},
            y: {json.dumps(price_values, ensure_ascii=False)},
            type: 'bar',
            marker: {{color: '#1565c0'}},
            text: {json.dumps(price_values, ensure_ascii=False)},
            textposition: 'outside',
            hovertemplate: '<b>%{{x}}</b><br>販売数: %{{y}}<extra></extra>'
        }}], {{
            margin: {{l: 50, r: 20, t: 20, b: 80}},
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            xaxis: {{title: '価格帯'}},
            yaxis: {{title: '販売数'}}
        }}, {{responsive: true}});

        // ライン別円グラフ
        Plotly.newPlot('citizen_line_chart', [{{
            labels: {json.dumps(line_labels, ensure_ascii=False)},
            values: {json.dumps(line_values, ensure_ascii=False)},
            type: 'pie',
            marker: {{
                colors: ['#1565c0', '#1976d2', '#1e88e5', '#2196f3', '#42a5f5', '#64b5f6', '#90caf9', '#bbdefb']
            }},
            textinfo: 'label+percent',
            textposition: 'outside',
            hovertemplate: '<b>%{{label}}</b><br>販売数: %{{value}}<br>比率: %{{percent}}<extra></extra>'
        }}], {{
            margin: {{l: 20, r: 20, t: 20, b: 20}},
            paper_bgcolor: 'white'
        }}, {{responsive: true}});
        </script>
        '''

        return graphs_html

    def generate_line_details_html(self):
        """ライン別詳細分析HTML（検索リンク＋チェックボックス付き）"""
        from utils.common import format_price, generate_search_link_html

        line_stats = self.stats['line_stats'].sort_values('販売数', ascending=False)

        rows_html = []
        for line_name, row in line_stats.iterrows():
            sales = int(row['販売数'])
            ratio = row['比率']
            median = row['中央値']
            cv = row['CV値']
            stability = row['安定度']

            # 検索リンク＋チェックボックス
            search_links = generate_search_link_html(
                brand='CITIZEN',
                keyword=line_name,
                link_type='line',
                include_checkbox=True
            )

            row_html = f'''
                    <tr>
                        <td><strong>{line_name}</strong></td>
                        <td>{sales}</td>
                        <td style="color: #1565c0;">{ratio * 100:.1f}%</td>
                        <td>{format_price(median)}</td>
                        <td>{cv:.3f}</td>
                        <td>{stability}</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>'''
            rows_html.append(row_html)

        html = f'''
        <h3 class="section-title" style="color: #1565c0;">🔵 ライン別詳細分析（全{len(line_stats)}ライン）</h3>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ライン</th>
                        <th>販売数</th>
                        <th style="color: #1565c0;">比率</th>
                        <th>中央値</th>
                        <th>CV値</th>
                        <th>安定度</th>
                        <th>仕入れ先検索</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        '''

        return html

    def generate_character_analysis_html(self):
        """キャラクター/コラボ分析HTML（検索リンク＋チェックボックス付き）"""
        from utils.common import generate_search_link_html

        # キャラクター/コラボ判定
        self.df['キャラクター/コラボ'] = self.df['TITLE_UPPER'].apply(self.is_character_collab)
        character_df = self.df[self.df['キャラクター/コラボ']].copy()

        if len(character_df) == 0:
            return "<p style='color: #999;'>キャラクター/コラボ商品はありません</p>"

        # キャラクター別集計
        character_counts = {}
        for title in character_df['TITLE_UPPER']:
            for kw in CHARACTER_KEYWORDS:
                if kw in title:
                    kw_clean = kw.strip()
                    character_counts[kw_clean] = character_counts.get(kw_clean, 0) + 1

        # 上位を抽出
        sorted_characters = sorted(character_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        total_char = len(character_df)
        median_price = character_df['価格'].median()
        ratio = total_char / len(self.df) * 100

        rows_html = []
        for char_name, count in sorted_characters:
            char_ratio = count / total_char * 100

            # 検索リンク＋チェックボックス
            search_links = generate_search_link_html(
                brand='CITIZEN',
                keyword=char_name,
                link_type='character',
                include_checkbox=True
            )

            row_html = f'''
                    <tr>
                        <td><strong>{char_name}</strong></td>
                        <td>{count}</td>
                        <td style="color: #1565c0;">{char_ratio:.1f}%</td>
                        <td>
                            {search_links}
                        </td>
                    </tr>'''
            rows_html.append(row_html)

        html = f'''
        <h3 class="section-title" style="color: #1565c0;">🤝 キャラクター/コラボ分析（複数視点）</h3>
        <p style="color: #666; margin-bottom: 15px;">同じ商品を別の角度から分析</p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 0.9em;">キャラクター商品数</div>
                <div style="color: #1565c0; font-size: 1.5em; font-weight: bold;">{total_char}個</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 0.9em;">中央値</div>
                <div style="font-size: 1.5em; font-weight: bold;">${int(median_price)}</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 0.9em;">全体比率</div>
                <div style="color: #1565c0; font-size: 1.5em; font-weight: bold;">{ratio:.1f}%</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>キャラクター</th>
                        <th>販売数</th>
                        <th>比率</th>
                        <th>仕入れ先検索</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        '''

        return html

    def generate_html(self):
        """HTML生成"""
        html = f'''<div id="CITIZEN" class="tab-content">
        <h2 style="color: #1565c0; margin-bottom: 20px;">CITIZEN 詳細分析</h2>

        {self.generate_base_stats_html()}

        {self.generate_top30_html()}

        {self.generate_graphs_html()}

        {self.generate_line_details_html()}

        {self.generate_character_analysis_html()}

        <p style="color: #666; margin: 20px 0;">
            ✅ CITIZEN完成：全セクション + 検索リンク＋チェックボックス
        </p>
    </div>'''

        return html


if __name__ == '__main__':
    print("✅ CITIZENストラテジー - Step 1: 型番抽出とライン分類")

    # テスト
    import pandas as pd

    # ダミーデータでテスト
    test_data = pd.DataFrame({
        'TITLE_UPPER': [
            'CITIZEN PROMASTER BN0151-09L ECO-DRIVE WATCH',
            'CITIZEN ATTESA AT8040-57E TITANIUM',
            'CITIZEN VINTAGE 1234-56789 AUTOMATIC'
        ],
        'タイトル': ['test1', 'test2', 'test3'],
        '価格': [200, 300, 150],
        '販売数': [5, 3, 2]
    })

    strategy = CITIZENStrategy(
        brand_name='CITIZEN',
        df_brand=test_data,
        brand_color='#1565c0',
        brand_color_light='#e3f2fd'
    )

    # 型番抽出テスト
    for title in test_data['TITLE_UPPER']:
        model = strategy.extract_model_number(title)
        print(f"  型番抽出: {title[:50]}... → {model}")

    # ライン分類テスト
    for idx, row in test_data.iterrows():
        line = strategy.classify_line(row)
        print(f"  ライン分類: {row['TITLE_UPPER'][:50]}... → {line}")

    print("\n✅ テスト完了")
