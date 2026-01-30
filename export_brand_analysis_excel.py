#!/usr/bin/env python3
"""
ブランド別詳細分析をExcelに出力
主要12ブランドについて、個別のシートを作成
"""

import pandas as pd
import re
from collections import Counter

# CSVファイル読み込み
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')

# 主要12ブランド
target_brands = ['SEIKO', 'CASIO', 'OMEGA', 'CITIZEN', 'Orient', 'TAG HEUER',
                 'GUCCI', 'ROLEX', 'Hamilton', 'Longines', 'Cartier', 'RADO']

def extract_model_number_generic(title, brand):
    """ブランドごとの型番抽出"""
    title_upper = str(title).upper()

    if brand == 'SEIKO':
        patterns = [
            r'\b([567][A-Z]{3}[0-9]{3,4}[A-Z]?)\b',
            r'\b(SBD[CX]\d{3})\b',
            r'\b(SRP[A-Z]?\d{3})\b',
            r'\b(SKX\d{3})\b',
            r'\b(SNZG\d{2})\b'
        ]
    elif brand == 'CASIO':
        patterns = [
            r'\b([A-Z]{2,3}-[A-Z0-9]{3,5}(?:-\d+)?[A-Z]?)\b',
            r'\b(G-[A-Z0-9]{4,6})\b',
            r'\b(DW-[A-Z0-9]{4,6})\b',
            r'\b(GA-[A-Z0-9]{4,6})\b'
        ]
    elif brand == 'OMEGA':
        patterns = [
            r'\b(\d{3}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{3})\b',
            r'\b(\d{4}\.\d{2}\.\d{2})\b'
        ]
    elif brand == 'ROLEX':
        patterns = [
            r'\b(\d{5,6})\b'
        ]
    elif brand == 'TAG HEUER':
        patterns = [
            r'\b([A-Z]{2,3}\d{4})\b',
            r'\b([A-Z]{3}\.\d{3}\.[A-Z]\d{1,2})\b'
        ]
    else:
        return None

    for p in patterns:
        match = re.search(p, title_upper)
        if match:
            return match.group(1)
    return None

def classify_line_generic(title, brand):
    """ブランドごとのライン分類"""
    title_upper = str(title).upper()

    if brand == 'SEIKO':
        if any(k in title_upper for k in ['PRESAGE', 'プレザージュ']):
            return 'Presage'
        elif any(k in title_upper for k in ['PROSPEX', 'プロスペックス']):
            return 'Prospex'
        elif any(k in title_upper for k in ['5 SPORTS', 'SEIKO 5', 'SEIKO5']):
            return 'SEIKO 5'
        elif any(k in title_upper for k in ['GRAND SEIKO', 'グランドセイコー']):
            return 'Grand Seiko'
        elif any(k in title_upper for k in ['ASTRON', 'アストロン']):
            return 'Astron'
        elif any(k in title_upper for k in ['BRIGHTZ', 'ブライツ']):
            return 'Brightz'
        elif any(k in title_upper for k in ['LUKIA', 'ルキア']):
            return 'Lukia'
        else:
            return '不明'

    elif brand == 'CASIO':
        if any(k in title_upper for k in ['G-SHOCK', 'GSHOCK']):
            return 'G-SHOCK'
        elif any(k in title_upper for k in ['BABY-G', 'BABYG']):
            return 'BABY-G'
        elif any(k in title_upper for k in ['OCEANUS', 'オシアナス']):
            return 'OCEANUS'
        elif any(k in title_upper for k in ['PRO TREK', 'PROTREK']):
            return 'PRO TREK'
        elif any(k in title_upper for k in ['EDIFICE', 'エディフィス']):
            return 'EDIFICE'
        elif any(k in title_upper for k in ['SHEEN', 'シーン']):
            return 'SHEEN'
        elif any(k in title_upper for k in ['LINEAGE', 'リニエージ']):
            return 'LINEAGE'
        else:
            return '不明'

    elif brand == 'OMEGA':
        if any(k in title_upper for k in ['SEAMASTER']):
            return 'Seamaster'
        elif any(k in title_upper for k in ['SPEEDMASTER']):
            return 'Speedmaster'
        elif any(k in title_upper for k in ['CONSTELLATION']):
            return 'Constellation'
        elif any(k in title_upper for k in ['DE VILLE']):
            return 'De Ville'
        else:
            return '不明'

    elif brand == 'ROLEX':
        if any(k in title_upper for k in ['SUBMARINER']):
            return 'Submariner'
        elif any(k in title_upper for k in ['DATEJUST']):
            return 'Datejust'
        elif any(k in title_upper for k in ['DAYTONA']):
            return 'Daytona'
        elif any(k in title_upper for k in ['GMT-MASTER', 'GMT MASTER']):
            return 'GMT-Master'
        elif any(k in title_upper for k in ['OYSTER']):
            return 'Oyster Perpetual'
        else:
            return '不明'

    else:
        return '不明'

def calculate_cv(values):
    """変動係数を計算"""
    if len(values) == 0:
        return 0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5
    return std_dev / mean

def extract_character_collab(title):
    """キャラクター/コラボを抽出"""
    title_upper = str(title).upper()

    # キャラクター/コラボキーワード
    keywords = {
        'ジブリ': ['GHIBLI', 'ジブリ', 'トトロ', 'TOTORO'],
        'ディズニー': ['DISNEY', 'ディズニー', 'MICKEY', 'ミッキー'],
        'マリオ': ['MARIO', 'マリオ', 'LUIGI', 'ルイージ'],
        'ポケモン': ['POKEMON', 'ポケモン', 'PIKACHU', 'ピカチュウ'],
        'ドラゴンボール': ['DRAGON BALL', 'ドラゴンボール', 'GOKU', '悟空'],
        'ワンピース': ['ONE PIECE', 'ワンピース', 'LUFFY', 'ルフィ'],
        'ガンダム': ['GUNDAM', 'ガンダム', 'ZAKU', 'ザク'],
        '記念モデル': ['ANNIVERSARY', 'アニバーサリー', '記念', 'MEMORIAL'],
        '限定モデル': ['LIMITED', 'リミテッド', '限定', 'SPECIAL EDITION'],
        'コラボ': ['COLLABORATION', 'コラボ', 'COLLAB', 'X ']
    }

    for collab_name, patterns in keywords.items():
        if any(k in title_upper for k in patterns):
            return collab_name

    return None

# Excelファイル作成
with pd.ExcelWriter('/Users/naokijodan/Desktop/watch-market-analysis/ブランド別詳細分析.xlsx', engine='openpyxl') as writer:

    for brand in target_brands:
        print(f"📊 {brand} の分析中...")

        # ブランドでフィルタ（完品のみ）
        brand_df = df[(df['ブランド'] == brand) & (df['商品状態'] == '完品')].copy()

        if len(brand_df) == 0:
            print(f"  ⚠️ {brand} のデータなし")
            continue

        # 型番抽出
        brand_df['型番'] = brand_df['タイトル'].apply(lambda x: extract_model_number_generic(x, brand))

        # ライン分類
        brand_df['ライン'] = brand_df['タイトル'].apply(lambda x: classify_line_generic(x, brand))

        # シート名（Excelシート名は31文字まで）
        sheet_name = brand[:31]

        # 1. 基本統計
        basic_stats = pd.DataFrame({
            '項目': [
                '出品数',
                '販売数',
                '平均価格',
                '中央値',
                '最低価格',
                '最高価格',
                'CV値',
                '型番抽出率'
            ],
            '値': [
                f"{len(brand_df)} 件",
                f"{brand_df['販売数'].sum()} 個",
                f"${brand_df['価格'].mean():.2f}",
                f"${brand_df['価格'].median():.2f}",
                f"${brand_df['価格'].min():.2f}",
                f"${brand_df['価格'].max():.2f}",
                f"{calculate_cv(brand_df['価格'].tolist()):.3f}",
                f"{(brand_df['型番'].notna().sum() / len(brand_df) * 100):.1f}%"
            ]
        })

        # Excelに書き込み（行1から）
        start_row = 0
        basic_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
        start_row += len(basic_stats) + 2

        # 2. Top30人気モデル（型番別）- HTMLページの順序に合わせる
        model_df = brand_df[brand_df['型番'].notna()].copy()
        if len(model_df) > 0:
            model_stats = model_df.groupby('型番').agg({
                '販売数': 'sum',
                '価格': ['median', 'count']
            }).reset_index()
            model_stats.columns = ['型番', '販売数', '中央値', '出品数']

            # CV値を追加
            cv_values = []
            for model in model_stats['型番']:
                model_prices = model_df[model_df['型番'] == model]['価格'].tolist()
                cv_values.append(calculate_cv(model_prices))
            model_stats['CV値'] = cv_values

            # 仕入上限（中央値の70%）
            model_stats['仕入上限(¥)'] = (model_stats['中央値'] * 150 * 0.7).round(0).astype(int)

            # 検索キーワードを追加
            model_stats['eBay検索'] = model_stats['型番'].apply(lambda x: f"{brand} {x} Watch")
            model_stats['メルカリ検索'] = model_stats['型番'].apply(lambda x: f"{brand} {x} 時計")

            model_stats = model_stats.sort_values('販売数', ascending=False).head(30).reset_index(drop=True)

            pd.DataFrame([['Top30人気モデル（型番別）', '', '', '', '', '', '', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                                                        startrow=start_row, index=False, header=False)
            start_row += 1
            model_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
            start_row += len(model_stats) + 2

        # 3. ライン別統計
        line_stats = brand_df.groupby('ライン').agg({
            'ブランド': 'count',
            '販売数': 'sum',
            '価格': ['mean', 'median']
        }).reset_index()
        line_stats.columns = ['ライン', '出品数', '販売数', '平均価格', '中央値']

        # CV値を追加
        cv_values = []
        for line in line_stats['ライン']:
            line_prices = brand_df[brand_df['ライン'] == line]['価格'].tolist()
            cv_values.append(calculate_cv(line_prices))
        line_stats['CV値'] = cv_values

        # 検索キーワードを追加
        line_stats['eBay検索'] = line_stats['ライン'].apply(lambda x: f"{brand} {x} Watch")
        line_stats['メルカリ検索'] = line_stats['ライン'].apply(lambda x: f"{brand} {x} 時計")

        line_stats = line_stats.sort_values('販売数', ascending=False).reset_index(drop=True)

        pd.DataFrame([['ライン別統計', '', '', '', '', '', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                                      startrow=start_row, index=False, header=False)
        start_row += 1
        line_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
        start_row += len(line_stats) + 2

        # 4. 各ライン内の人気型番Top10
        top_lines = line_stats.head(7)['ライン'].tolist()  # Top7ライン

        for line_name in top_lines:
            line_models = brand_df[(brand_df['ライン'] == line_name) & (brand_df['型番'].notna())].copy()

            if len(line_models) > 0:
                line_model_stats = line_models.groupby('型番').agg({
                    '販売数': 'sum',
                    '価格': ['median', 'count']
                }).reset_index()
                line_model_stats.columns = ['型番', '販売数', '中央値', '出品数']

                # CV値
                cv_values = []
                for model in line_model_stats['型番']:
                    model_prices = line_models[line_models['型番'] == model]['価格'].tolist()
                    cv_values.append(calculate_cv(model_prices))
                line_model_stats['CV値'] = cv_values

                # 仕入上限
                line_model_stats['仕入上限(¥)'] = (line_model_stats['中央値'] * 150 * 0.7).round(0).astype(int)

                # 検索キーワード
                line_model_stats['eBay検索'] = line_model_stats['型番'].apply(lambda x: f"{brand} {x} Watch")
                line_model_stats['メルカリ検索'] = line_model_stats['型番'].apply(lambda x: f"{brand} {x} 時計")

                line_model_stats = line_model_stats.sort_values('販売数', ascending=False).head(10).reset_index(drop=True)

                pd.DataFrame([[f'{line_name} - Top10型番', '', '', '', '', '', '', '', '']]).to_excel(
                    writer, sheet_name=sheet_name, startrow=start_row, index=False, header=False)
                start_row += 1
                line_model_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                start_row += len(line_model_stats) + 2

        # 5. キャラクター/コラボ分析
        brand_df['キャラクター/コラボ'] = brand_df['タイトル'].apply(extract_character_collab)
        collab_df = brand_df[brand_df['キャラクター/コラボ'].notna()].copy()

        if len(collab_df) > 0:
            collab_stats = collab_df.groupby('キャラクター/コラボ').agg({
                'ブランド': 'count',
                '販売数': 'sum',
                '価格': ['mean', 'median']
            }).reset_index()
            collab_stats.columns = ['キャラクター/コラボ', '出品数', '販売数', '平均価格', '中央値']

            # CV値を追加
            cv_values = []
            for collab in collab_stats['キャラクター/コラボ']:
                collab_prices = collab_df[collab_df['キャラクター/コラボ'] == collab]['価格'].tolist()
                cv_values.append(calculate_cv(collab_prices))
            collab_stats['CV値'] = cv_values

            # 検索キーワードを追加
            collab_stats['eBay検索'] = collab_stats['キャラクター/コラボ'].apply(lambda x: f"{brand} {x} Watch")
            collab_stats['メルカリ検索'] = collab_stats['キャラクター/コラボ'].apply(lambda x: f"{brand} {x} 時計")

            collab_stats = collab_stats.sort_values('販売数', ascending=False).reset_index(drop=True)

            pd.DataFrame([['キャラクター/コラボ分析', '', '', '', '', '', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                                                          startrow=start_row, index=False, header=False)
            start_row += 1
            collab_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
            start_row += len(collab_stats) + 2

        # 6. 駆動方式別統計
        drive_stats = brand_df.groupby('駆動方式').agg({
            'ブランド': 'count',
            '販売数': 'sum',
            '価格': ['mean', 'median']
        }).reset_index()
        drive_stats.columns = ['駆動方式', '出品数', '販売数', '平均価格', '中央値']
        drive_stats = drive_stats.sort_values('販売数', ascending=False).reset_index(drop=True)

        pd.DataFrame([['駆動方式別統計', '', '', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                                    startrow=start_row, index=False, header=False)
        start_row += 1
        drive_stats.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
        start_row += len(drive_stats) + 2

        # 7. 価格帯分布（50ドル刻み）
        bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, float('inf')]
        labels = ['$0-50', '$50-100', '$100-150', '$150-200', '$200-250', '$250-300', '$300-350', '$350-400',
                  '$400-450', '$450-500', '$500-550', '$550-600', '$600-650', '$650-700', '$700-750', '$750-800',
                  '$800-850', '$850-900', '$900-950', '$950-1000', '$1000+']
        brand_df['価格帯'] = pd.cut(brand_df['価格'], bins=bins, labels=labels)
        price_dist = brand_df.groupby('価格帯', observed=False).agg({
            'ブランド': 'count',
            '販売数': 'sum'
        }).reset_index()
        price_dist.columns = ['価格帯', '出品数', '販売数']

        pd.DataFrame([['価格帯分布（50ドル刻み）', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                                     startrow=start_row, index=False, header=False)
        start_row += 1
        price_dist.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
        start_row += len(price_dist) + 2

        # 8. 月別推移
        brand_df['販売月'] = pd.to_datetime(brand_df['販売日']).dt.to_period('M')
        monthly = brand_df.groupby('販売月').agg({
            'ブランド': 'count',
            '販売数': 'sum'
        }).reset_index()
        monthly.columns = ['販売月', '出品数', '販売数']
        monthly['販売月'] = monthly['販売月'].astype(str)

        pd.DataFrame([['月別推移', '', '']]).to_excel(writer, sheet_name=sheet_name,
                                                     startrow=start_row, index=False, header=False)
        start_row += 1
        monthly.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
        start_row += len(monthly) + 2

        print(f"  ✅ {brand} 完了 ({len(brand_df)}件)")

print("\n✅ ブランド別詳細分析を出力しました:")
print("   /Users/naokijodan/Desktop/watch-market-analysis/ブランド別詳細分析.xlsx")
print(f"\n対象ブランド: {', '.join(target_brands)}")
