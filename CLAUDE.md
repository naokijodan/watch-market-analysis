# watch-market-analysis プロジェクトルール

## 🎯 プロジェクト概要
eBay時計販売データの分析システム
- SEIKO、CASIO、CITIZEN、Orientなどのブランド別詳細分析
- HTMLタブ形式で複数ブランドの統計・人気モデル・仕入れ戦略を提供

## 🚫 行動規範（過去の失敗から学んだ絶対ルール）

### 1. ファイルは末尾まで読む
- 部分読み（最初の200行だけ等）で仕様を推測してはならない
- 雛形・テンプレートは必ず全行読み込んでから作業する
- 「だいたい理解した」は理解していない

### 2. 質問に先に答える
- ユーザーが「なぜ？」と聞いたら、まず答える
- 作業を強行して質問を無視してはならない
- 質問への回答 → 合意 → 作業、の順序を守る

### 3. 設計を提示し、承認を得てから実装する
- コードを書く前に設計書（変更内容・影響範囲）を提示
- ユーザーの承認なしに実装を進めない
- 3者協議を指示された場合は必ず実行する

### 4. 完了を自己判断しない
- 作業後は必ず `git diff` で差分を確認する
- HTMLの出力をブラウザで検証する
- 「完了」はユーザーが判断する。自分で宣言しない

### 5. 模倣が基本、改善は許可制
- 既存の構造・順序を勝手に「改善」しない
- 雛形がある場合は完全に模倣する
- 改善したい場合はユーザーに提案して承認を得る

---

## 🚨 重要：HTMLタブ置換時の再発防止策

### 過去の失敗事例（必読）

#### 1. SEIKOタブ消失（2026-01-27）
- **原因**: 正規表現 `</div>\s*(?=<div id="|</div>\s*<script>)` が曖昧
- **結果**: CASIOスクリプト実行時にSEIKOタブを上書き

#### 2. CASIOタブ消失（2026-01-27）
- **原因**: 正規表現がネストされた`</div>`の最初のものにマッチ
- **結果**: SEIKOスクリプト実行時にCASIOタブまで置換

#### 3. CITIZENタブのデータ欠損（2026-01-27）
- **原因**: JSONファイルの`model_stats`が空配列だった
- **結果**: Top30セクションが空（0行）

#### 4. Orientタブが空（2026-01-27）
- **原因**: タブボタンは存在するが、コンテンツdivが未実装
- **結果**: タブをクリックしても何も表示されない

#### 5. 検索列追加スクリプトが3分以上実行（2026-01-28）
- **原因**: `(?:.*?<td[^>]*>[^<]*</td>)+?` のネスト量指定子が728KBのHTMLに対してcatastrophic backtracking
- **結果**: 0/8キャラクターに検索列追加失敗、リンクとチェックボックス消失
- **見落とし**: 実行ログの「0/8個」を確認せず報告、HTML出力を検証せず
- **修正**: `.*?` で行末まで単純マッチに変更、Orient構造対応
- **長期対策**: Python標準 `html.parser` への移行を検討（3者協議で合意）

---

## ✅ HTMLタブ置換の正しい方法

### 【必須】正規表現を使わない

```python
# ❌ 絶対に使ってはいけない方法
pattern = r'</div>(?=\s*<script>)'
html = re.sub(pattern, replacement, html)

# ✅ 正しい方法：文字列位置ベースの分割・結合
insert_pos = 441058  # 正確な位置を特定
html = html[:insert_pos] + new_content + html[insert_pos:]
```

### 【必須】ネストカウントで終了位置を特定

```python
# タブの終了</div>を探す（ネストを考慮）
div_count = 1
search_pos = tab_start + len('<div id="TABNAME" class="tab-content">')

while div_count > 0 and search_pos < body_pos:
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
            tab_end = next_close + 6  # 6 = len('</div>')
            break
        else:
            search_pos = next_close + 6

# ここでtab_endが正確な終了位置
```

### 【必須】実装前の確認

1. **挿入位置の目視確認**
```python
# 挿入位置の前後50文字を表示
print(html[insert_pos-50:insert_pos+50])
```

2. **既存タブの位置確認**
```python
# 既存タブの終了位置を確認
citizen_end = ... # ネストカウントで特定
print(f"CITIZENタブ終了: {citizen_end}")
print(f"</body>位置: {body_pos}")
print(f"挿入位置: {citizen_end + 6}")
```

### 【必須】実装後の検証

```python
# 1. タブコンテンツdivの存在確認
assert '<div id="Orient" class="tab-content">' in html

# 2. Top30セクションのデータ行数確認
top30_section = ...
rows = tbody.count('<tr>')
assert rows == 30, f"Top30が{rows}行しかありません"

# 3. ファイルサイズの増加確認
old_size = 448.9  # KB
new_size = len(html) / 1024
assert new_size > old_size, "ファイルサイズが増加していません（空の可能性）"

print(f"✅ 検証完了: {old_size}KB → {new_size:.1f}KB")
```

---

## 📋 HTMLタブ追加・修正チェックリスト

### 実装前
- [ ] 挿入位置を**文字列位置**で特定（正規表現を使わない）
- [ ] ネストされた`<div>`の終了位置を**カウント**で特定
- [ ] 挿入位置の前後50文字を表示して目視確認
- [ ] 既存タブへの影響範囲を確認

### 実装中
- [ ] 正規表現を使わない（`re.sub`, `re.findall`の使用禁止）
- [ ] CSVから直接データ生成（JSONに依存しない）
- [ ] 文字列の分割・結合のみ使用

### 実装後
- [ ] タブコンテンツdivの存在確認
- [ ] Top30セクションのデータ行数確認（30行）
- [ ] ライン別セクションの存在確認
- [ ] ファイルサイズの増加確認
- [ ] タブの順序確認（SEIKO→CASIO→CITIZEN→Orient）
- [ ] スクリプト単体でテスト実行
- [ ] `rebuild_all_tabs.py`に追加（該当する場合）

---

## 🔄 タブ再構築スクリプトの実行順序

```bash
# 個別実行
python3 rebuild_seiko_v3_complete.py
python3 rebuild_casio_v3_complete.py
python3 rebuild_citizen_v3_complete.py
python3 rebuild_orient_v3_complete.py

# 一括実行（推奨）
python3 rebuild_all_tabs.py
```

**実行順序**: SEIKO → CASIO → CITIZEN → Orient

**重要**: この順序を変更しないこと。後のタブが前のタブに依存している。

---

## 📦 ファイル構成

```
watch-market-analysis/
├── index.html                          # メインHTML
├── CLAUDE.md                           # このファイル
│
│  【データ追加パイプライン】
├── add_watch_data.py                   # CSVマージ + 属性生成 + 駆動方式/パーツタブ再生成
├── generate_attributes.py              # 属性生成（add_watch_data.pyから呼ばれる）
│
│  【分析シート生成】
├── export_analysis_excel.py            # → 分析シート.xlsx
├── export_brand_analysis_excel.py      # → ブランド別詳細分析.xlsx
├── 分析シート.xlsx                      # 全体統計（12シート）
├── ブランド別詳細分析.xlsx              # ブランド別詳細（12ブランド）
│
│  【HTMLタブ再生成（現在使用するスクリプト）】
├── rebuild_overall_complete.py         # 全体分析タブ
├── rebuild_brand_list_tab.py           # ブランド一覧タブ
├── rebuild_seiko_v3_complete.py        # SEIKOタブ
├── rebuild_casio_v3_complete.py        # CASIOタブ
├── rebuild_citizen_v3_complete.py      # CITIZENタブ
├── rebuild_orient_v3_complete.py       # Orientタブ
├── rebuild_omega_v3_complete.py        # OMEGAタブ
├── rebuild_rolex_v3_complete.py        # ROLEXタブ
├── rebuild_tagheuer_v3_complete.py     # TAG HEUERタブ
├── rebuild_gucci_v3_complete.py        # GUCCIタブ
├── rebuild_hamilton_v3_complete.py     # Hamiltonタブ
├── rebuild_longines_complete_fixed.py  # Longinesタブ（7セクション完全版）
├── rebuild_cartier_v3_complete.py      # Cartierタブ
├── rebuild_rado_v3_complete.py         # RADOタブ
├── build_movement_tabs.py              # 駆動方式タブ（6種）
├── build_parts_tabs.py                 # パーツタブ（4種）
│
│  【データソース（プロジェクト外）】
│  ~/Desktop/時計データ_分類済み.csv    # メインCSV
│
│  【その他】
├── rebuild_all_tabs.py                 # 旧・全タブ一括再構築（非推奨）
└── schema.py                           # データスキーマ定義
```

---

## 🎨 ブランドカラー定義

- **SEIKO**: ブルー系 (`#1976d2`, `#e3f2fd`)
- **CASIO**: レッド系 (`#e63946`, `#ffe5e5`)
- **CITIZEN**: シアン系 (`#1565c0`, `#e3f2fd`)
- **Orient**: オレンジ系 (`#FF6B35`, `#FFE5D9`)

新しいブランドを追加する場合は、既存のカラーと被らないように選択すること。

---

## 📝 開発ログ

重要な変更・修正を行った場合は、Obsidianの`/開発ログ/`にノートを作成すること。

### 命名規則
```
watch-market-analysis_{変更内容}_{日付}.md
```

### 必須項目
- 問題・原因・修正内容
- 失敗事例（該当する場合）
- 再発防止策
- Git履歴
- ステータス

---

## 🚀 新しいブランドタブを追加する場合

### 手順

1. **データ確認**
```python
import pandas as pd
df = pd.read_csv('/Users/naokijodan/Desktop/時計データ_分類済み.csv')
df_brand = df[df['ブランド'] == 'BRANDNAME'].copy()
print(f"商品数: {len(df_brand)}")
```

2. **スクリプト作成**
- `rebuild_{brandname}_v3_complete.py` を作成
- SEIKO/CASIO/CITIZEN/Orientのいずれかをテンプレートとして使用
- ライン分類ロジックをブランドに合わせて調整

3. **HTML挿入位置の特定**
- 最後のブランドタブの終了位置を**ネストカウント**で特定
- 文字列位置ベースで挿入

4. **実行と検証**
```bash
python3 rebuild_{brandname}_v3_complete.py
# 検証スクリプトで確認
```

5. **rebuild_all_tabs.py に追加**
```python
# N. BRANDNAMEタブを再構築
print(f"🟢 {N}/{TOTAL}: BRANDNAMEタブ再構築中...")
result_brand = subprocess.run([sys.executable, 'rebuild_{brandname}_v3_complete.py'], ...)
```

6. **Git commit & Obsidianノート作成**

---

## 💡 トラブルシューティング

### Q: タブをクリックしても何も表示されない
A: タブコンテンツdivが存在しない可能性があります。
```bash
grep '<div id="TABNAME" class="tab-content">' index.html
```
存在しない場合は、該当するスクリプトを実行してください。

### Q: Top30セクションが空（0行）
A: JSONではなくCSVから直接生成するようにスクリプトを修正してください。

### Q: タブが相互に上書きされる
A: 正規表現を使っている可能性があります。文字列位置ベースの置換に変更してください。

### Q: ファイルサイズが増加しない
A: コンテンツが実際に挿入されていない可能性があります。挿入位置を確認してください。

---

## 🏗️ 【2026-01-27】完全再構築計画

### 背景と目的

**問題**:
- Regex置換の失敗（ネストした`<div>`にマッチしない）
- 実行順序依存による相互上書き
- Orient のみ異なる構造（🎁限定モデル分析 vs 🎭キャラクター/コラボ分析）
- SEIKO/CASIOでライン別円グラフが追加されない
- ライン別詳細分析・キャラクター/コラボ分析セクションに検索リンクがない

**3者協議の結論**:
- ✅ ゼロベース再構築（既存コードのパッチングではない）
- ✅ Strategy Patternアーキテクチャ
- ✅ Schema-First開発
- ✅ Golden Masterテスト
- ✅ 単一スクリプトで全ブランド生成（実行順序依存を排除）

---

### Phase 1: 準備（Golden Master作成）

**目的**: 現在の出力をベースラインとして保存し、回帰テストに使用

**作業**:
1. 既存の4スクリプトを実行してHTMLを生成
2. 各ブランドタブのHTMLセクションを抽出
3. `golden_master/` ディレクトリに保存
4. 検証スクリプト作成（構造比較、グラフ数確認）

**成果物**:
- `golden_master/seiko_tab.html`
- `golden_master/casio_tab.html`
- `golden_master/citizen_tab.html`
- `golden_master/orient_tab.html`
- `golden_master/verify.py`

---

### Phase 2: データスキーマ定義

**必須フィールド（全ブランド共通）**:
```python
{
    "model_number": str,      # 型番
    "title": str,             # タイトル
    "price": float,           # 価格
    "sales": int,             # 販売数
    "line": str,              # ライン
    "condition": str,         # 商品状態
    "category": str           # カテゴリ
}
```

**ブランド固有フィールド**:
```python
{
    "drive_type": str,         # 駆動方式（SEIKO, CITIZEN）
    "character_collab": bool,  # キャラクター/コラボ
    "limited_edition": bool,   # 限定モデル（Orient）
    "anniversary_model": bool  # 記念モデル（Orient）
}
```

**バリデーションルール**:
- 価格: 0以上の数値
- 販売数: 0以上の整数
- ライン: 空文字は"不明"に正規化
- 型番: 抽出失敗時は"N/A"

**成果物**: `schema.py`

---

### Phase 3: 共通パイプライン設計

**アーキテクチャ**: Strategy Pattern

```
BrandAnalyzer (Context)
    ├── AbstractBrandStrategy (抽象基底クラス)
    │   ├── extract_model_number()
    │   ├── classify_line()
    │   ├── generate_sections()
    │   └── calculate_cv()
    │
    ├── SEIKOStrategy
    ├── CASIOStrategy
    ├── CITIZENStrategy
    └── OrientStrategy
```

**共通処理フロー**:
1. CSV読み込み
2. 完品データフィルタ
3. ブランド別データ抽出
4. 型番抽出（ブランド別）
5. ライン分類（ブランド別）
6. 統計計算（共通）
7. HTML生成（共通テンプレート + ブランド固有）

**成果物**:
- `brand_analyzer.py`
- `strategies/base.py`
- `utils/common.py`

---

### Phase 4: 統一HTMLテンプレート

**6セクション構成（全ブランド統一）**:
1. 📊 基本統計（販売数、平均価格、CV値）
2. 🏆 Top30人気モデル（テーブル + eBay/メルカリ検索リンク）
3. 📈 価格帯別販売分布（棒グラフ）
4. 📊 ライン別売上比率（円グラフ）← **全ブランドで統一**
5. 🔵 ライン別詳細分析（テーブル + **検索リンク追加**）
6. 🎭 キャラクター/コラボ分析（テーブル + **検索リンク追加**）

**重要な追加機能**:
- ✅ **ライン別詳細分析に検索リンク**: ライン名（例: "SEIKO 5"）でeBay/メルカリ検索
- ✅ **キャラクター/コラボ分析に検索リンク**: キャラクター名（例: "ジブリ"）でeBay/メルカリ検索
- ✅ Orientに🎭キャラクター/コラボ分析を追加（既存の🎁は7番目に残す）
- ✅ グラフレイアウトはCSS Gridで2x3配置

**検索リンク仕様**:
```python
# ライン別詳細分析の例
line_name = "SEIKO 5"
ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=SEIKO+SEIKO+5+Watch&LH_Sold=1"
mercari_url = f"https://jp.mercari.com/search?keyword=SEIKO%20SEIKO%205%20時計&status=on_sale"

# キャラクター/コラボ分析の例
character = "ジブリ"
ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=SEIKO+ジブリ+Watch&LH_Sold=1"
mercari_url = f"https://jp.mercari.com/search?keyword=SEIKO%20ジブリ%20時計&status=on_sale"
```

**チェックボックス機能**:
各検索リンクの横にチェックボックスを配置し、ユーザーが検索済みを判断できるようにする。

```html
<a href="..." target="_blank" class="link-btn link-ebay">eBay</a>
<input type="checkbox" class="search-checkbox">
<a href="..." target="_blank" class="link-btn link-mercari">メルカリ</a>
<input type="checkbox" class="search-checkbox">
```

**適用箇所**:
- Top30テーブル（各モデル）
- ライン別詳細分析（各ライン）
- キャラクター/コラボ分析（各キャラクター）

**成果物**: `templates/brand_tab.html`

---

### Phase 5: 実装順序

1. **共通ユーティリティ** (`utils/common.py`)
   - `calculate_cv(values)`
   - `format_price(price)`
   - `aggregate_top_lines(df, top_n=7)`
   - `generate_search_links(brand, keyword, type='model')`

2. **基底クラス** (`strategies/base.py`)

3. **CITIZENストラテジー** (`strategies/citizen.py`)
   - 既存ロジック移植 + 検索リンク追加

4. **他ブランドストラテジー**
   - `strategies/seiko.py` + 検索リンク
   - `strategies/casio.py` + 検索リンク
   - `strategies/orient.py` + 🎭セクション追加 + 検索リンク

5. **統合スクリプト** (`rebuild_all_brands_unified.py`)
   - 全ブランドを1回の実行で生成
   - 文字列位置ベースで置換
   - 1回のファイル書き込みで完了

---

### Phase 6: テスト & 検証

**テスト項目**:
1. Golden Master回帰テスト
2. 検索リンクの動作確認（全セクション）
3. グラフ数の一致確認（各ブランド6個）
4. Top30行数の確認（各30行）
5. 冪等性テスト（2回実行して同じ結果）
6. 視覚検証（ブラウザで全タブ確認）

**成果物**:
- `tests/test_golden_master.py`
- `tests/test_search_links.py`
- `tests/test_idempotency.py`

---

### 実装優先度

**優先度1（必須）**:
- Phase 1, 2, 3, 5の実装
- 全ブランドでライン別円グラフ追加
- ライン別詳細分析・キャラクター/コラボ分析に検索リンク追加
- Orientに🎭キャラクター/コラボ分析を追加

**優先度2（推奨）**:
- Phase 4のテンプレート化
- Phase 6のテスト自動化

---

### 実装開始の前提条件

1. ✅ この計画書の承認
2. ✅ `rebuild_all_brands_unified.py` の既存コードを削除
3. ✅ 既存の4スクリプトはGolden Master作成まで保持

---

## 🔍 HTML操作時の必須チェックリスト（2026-01-28追加）

### テーブル構造変更時の注意点

**問題**: テーブルに列を追加すると、既存の正規表現パターンが壊れる

**チェックリスト**:
- [ ] テーブル構造変更（列追加/削除）を行う場合、依存スクリプトを確認
- [ ] `add_all_checkboxes_dynamic.py` がテーブル構造に依存していないか確認
- [ ] 実行後、必ずログで「N/N個」が全て一致しているか確認
- [ ] **差分確認**: `git diff` で変更内容を確認し、抜けがないかチェック
- [ ] HTML出力をブラウザで目視確認してから報告

### 正規表現パターンの原則

**禁止パターン**:
```python
# ❌ ネスト量指定子 → catastrophic backtracking
r'(?:.*?<td[^>]*>[^<]*</td>)+?'

# ❌ 最後の列に依存 → 列追加で壊れる
r'<td class="seiko-accent">[^<]*</td>\s*</tr>'
```

**推奨パターン**:
```python
# ✅ 行末まで単純マッチ
r'<td><strong>NAME</strong></td>.*?\s*</tr>'

# ✅ ブランド分岐を減らす（統一パターン）
# 各ブランドで同じパターンを使う
```

### 長期的な改善策（3者協議で合意）

**現状**: 正規表現でHTMLを操作（脆弱、保守性低）

**推奨**: Python標準 `html.parser` へ移行
- 依存関係ゼロ（外部ライブラリ不要）
- 線形時間パフォーマンス（728KB → 数秒）
- 保守性・可読性が向上
- 再発リスクを根本解決

**実装優先度**: 次回のメンテナンスタイミングで最優先

### 実行後の検証手順（必須）

1. **ログ確認**:
   - 「N/N個」の数値が一致しているか
   - 「0/N個」があれば即座に調査

2. **差分確認**:
   ```bash
   git diff HEAD~1 HEAD -- [変更ファイル]
   ```
   - 変更箇所が意図通りか確認
   - 予期しない変更がないか確認

3. **HTML出力確認**:
   - ブラウザで各セクションを開く
   - 検索リンクとチェックボックスが表示されているか
   - 各ブランドで動作確認

4. **報告前の最終確認**:
   - [ ] ログで全ブランド成功を確認
   - [ ] 差分で変更内容を確認
   - [ ] HTMLで実際の出力を確認
   - 上記3点が完了してから報告する

---

## 📊 データ追加方法（2026-02-01更新）

### クイックチェックリスト

```
□ Phase 1: 事前準備
  □ CLAUDE.md読む（行動規範確認）
  □ Obsidian開発ログ確認
  □ git status / git log 確認
□ Phase 2: データマージ + 分析シート更新
  □ python3 add_watch_data.py <新規CSVパス>
  □ python3 export_analysis_excel.py
  □ python3 export_brand_analysis_excel.py
□ Phase 3: HTMLタブ再生成（この順序で実行）
  □ python3 rebuild_overall_complete.py
  □ python3 rebuild_brand_list_tab.py
  □ python3 rebuild_xxx_v3_complete.py（該当ブランド）
  □ python3 build_movement_tabs.py
  □ python3 build_parts_tabs.py
□ Phase 4: 完了処理
  □ ブラウザで各タブ確認
  □ git diff で差分確認
  □ git commit & push
  □ Obsidianノート作成
```

### Phase 1: 事前準備

1. **CLAUDE.md を読む** - 行動規範を確認（焦って作業しない）
2. **Obsidian の開発ログを確認** - 過去の失敗・注意点を把握
3. **Git の状態を確認** - 未コミットの変更がないか `git status` / `git log` で確認

### Phase 2: データマージ + 分析シート更新

4. **新データのCSVパスを受け取る**
5. **CSVマージ**
   ```bash
   cd ~/Desktop/watch-market-analysis
   python3 add_watch_data.py <新規CSVパス>
   ```
   - Dry Run（属性生成テスト・抽出率チェック）
   - 重複チェック（タイトル + 販売日で判定）
   - 歩留まり率検証
   - CSV保存 → 駆動方式タブ・パーツタブ再生成
   - **注意: このスクリプトは駆動方式+パーツタブしか再生成しない。Phase 3が必須**

6. **分析シート再生成**
   ```bash
   python3 export_analysis_excel.py       # → 分析シート.xlsx
   python3 export_brand_analysis_excel.py  # → ブランド別詳細分析.xlsx
   ```
   - 新ブランドを追加する場合は `export_brand_analysis_excel.py` の `target_brands` リストに追加が必要

### Phase 3: HTMLタブ再生成

**実行順序と依存関係**:

| 順序 | スクリプト | 対象 | 依存関係 |
|------|-----------|------|---------|
| 1 | `rebuild_overall_complete.py` | 全体分析タブ | CSVから全体統計を再計算 |
| 2 | `rebuild_brand_list_tab.py` | ブランド一覧タブ | CSVからブランド別販売数を再集計 |
| 3 | `rebuild_xxx_v3_complete.py` | 該当ブランドタブ | CSVからブランド別詳細を再生成 |
| 4 | `build_movement_tabs.py` | 駆動方式タブ | add_watch_data.pyで実行済みだが確認用 |
| 5 | `build_parts_tabs.py` | パーツタブ | add_watch_data.pyで実行済みだが確認用 |

**順序4,5はadd_watch_data.pyで実行済みのため、問題なければスキップ可**

### Phase 4: 完了処理

7. **検証**: ブラウザで各タブの表示を確認
8. **差分確認**: `git diff` で変更内容を確認
9. **Git commit & push**
10. **Obsidianノート作成**
    - ファイル名: `watch-market-analysis_データ追加_{日付}.md`
    - 内容: 追加件数、ブランド別統計、変更履歴

### 関連スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| `add_watch_data.py` | CSVマージ + 属性生成 + 駆動方式/パーツタブ再生成 |
| `generate_attributes.py` | 属性生成（add_watch_data.pyから呼ばれる） |
| `export_analysis_excel.py` | 分析シート.xlsx 生成 |
| `export_brand_analysis_excel.py` | ブランド別詳細分析.xlsx 生成 |
| `rebuild_overall_complete.py` | 全体分析タブ再生成 |
| `rebuild_brand_list_tab.py` | ブランド一覧タブ再生成 |
| `rebuild_xxx_v3_complete.py` | 各ブランドタブ再生成（xxxはブランド名） |
| `build_movement_tabs.py` | 駆動方式タブ再生成 |
| `build_parts_tabs.py` | パーツタブ再生成 |

### 新しい会話でもOK

新しい会話を始めても、以下から文脈を復元できる：
- プロジェクトルール: `CLAUDE.md`（このファイル）
- データソース: `~/Desktop/時計データ_分類済み.csv`
- 過去の変更履歴: Gitコミット履歴
- 開発ログ: Obsidian `/開発ログ/watch-market-analysis_*.md`

---

**このファイルは、プロジェクトの重要なルールと再発防止策を記録しています。**
**タブの追加・修正を行う際は、必ずこのファイルを参照してください。**
