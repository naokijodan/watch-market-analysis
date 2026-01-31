# watch-market-analysis プロジェクトルール

## プロジェクト概要
eBay時計販売データの分析システム
- SEIKO、CASIO、CITIZEN、Orient、OMEGA、ROLEX等のブランド別詳細分析
- HTMLタブ形式で複数ブランドの統計・人気モデル・仕入れ戦略を提供
- データソース: `~/Desktop/時計データ_分類済み.csv`
- 公開URL: https://naokijodan.github.io/watch-market-analysis/

---

## 行動規範（過去の失敗から学んだ絶対ルール）

### 1. ファイルは末尾まで読む
- 部分読みで仕様を推測しない。雛形は全行読んでから作業する

### 2. 質問に先に答える
- ユーザーが「なぜ？」と聞いたら、まず答える。作業を強行しない

### 3. 設計を提示し、承認を得てから実装する
- コードを書く前に設計書（変更内容・影響範囲）を提示
- 3者協議を指示された場合は必ず実行する

### 4. 完了を自己判断しない
- 作業後は `git diff` で差分確認、HTMLはブラウザで検証
- 「完了」はユーザーが判断する

### 5. 模倣が基本、改善は許可制
- 既存の構造・順序を勝手に「改善」しない
- 雛形がある場合は完全に模倣する

---

## ファイル構成

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
│
│  【HTMLタブ再生成スクリプト】
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
├── rebuild_longines_complete_fixed.py  # Longinesタブ
├── rebuild_cartier_v3_complete.py      # Cartierタブ
├── rebuild_rado_v3_complete.py         # RADOタブ
├── build_movement_tabs.py              # 駆動方式タブ（6種）
├── build_parts_tabs.py                 # パーツタブ（4種）
│
│  【検索リンク追加スクリプト】
├── add_casio_search_links.py           # CASIOライン別・コラボに検索リンク追加
│
│  【その他】
├── rebuild_all_tabs.py                 # 全タブ一括再構築
└── schema.py                           # データスキーマ定義
```

---

## HTMLタブ操作の鉄則

### 過去の失敗事例（教訓）

| 事例 | 原因 | 結果 |
|------|------|------|
| SEIKOタブ消失 | 正規表現 `</div>\s*(?=<div id=")` が曖昧 | CASIOスクリプト実行時にSEIKOを上書き |
| CASIOタブ消失 | 正規表現がネスト`</div>`の最初にマッチ | SEIKOスクリプト実行時にCASIOまで置換 |
| CITIZENデータ欠損 | JSONの`model_stats`が空配列 | Top30が0行 |
| 検索列追加が無限実行 | ネスト量指定子が728KBのHTMLでbacktracking | 0/8成功、リンク消失 |

### 鉄則1: 正規表現を使わない

```python
# ❌ 禁止
html = re.sub(pattern, replacement, html)

# ✅ 正しい方法：文字列位置ベースの分割・結合
insert_pos = html.find('<div id="TARGET"')
html = html[:insert_pos] + new_content + html[insert_pos:]
```

### 鉄則2: ネストカウントで終了位置を特定

```python
div_count = 1
search_pos = tab_start + len('<div id="TABNAME" class="tab-content">')
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
            tab_end = next_close + 6
            break
        else:
            search_pos = next_close + 6
```

### 鉄則3: CSVから直接生成（JSONに依存しない）

### 鉄則4: 実装前後の検証を必ず行う

**実装前**:
- 挿入位置の前後50文字を表示して目視確認
- 既存タブへの影響範囲を確認

**実装後**:
- タブコンテンツdivの存在確認
- Top30のデータ行数確認（30行）
- ファイルサイズの増加確認
- ブラウザで各セクションを目視確認
- 実行ログで「N/N個」が全て一致しているか確認

### チェックリスト

```
□ 挿入位置を文字列位置で特定（正規表現禁止）
□ ネストされた<div>の終了位置をカウントで特定
□ 挿入位置の前後50文字を目視確認
□ CSVから直接データ生成
□ タブコンテンツdivの存在確認
□ Top30セクションのデータ行数確認
□ ファイルサイズの増加確認
□ ブラウザで出力確認してから報告
```

---

## データ追加手順

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
  □ build_movement_tabs.py / build_parts_tabs.py（必要に応じて）
□ Phase 4: 完了処理
  □ ブラウザで各タブ確認
  □ git diff で差分確認
  □ git commit & push
  □ Obsidianノート作成
```

### Phase 2 補足

`add_watch_data.py` の処理内容:
- Dry Run（属性生成テスト・抽出率チェック）
- 重複チェック（タイトル + 販売日で判定）
- 歩留まり率検証
- CSV保存 → 駆動方式タブ・パーツタブ再生成
- **注意: このスクリプトは駆動方式+パーツタブしか再生成しない。Phase 3が必須**

### Phase 3: HTMLタブ再生成の実行順序

| 順序 | スクリプト | 対象 |
|------|-----------|------|
| 1 | `rebuild_overall_complete.py` | 全体分析タブ |
| 2 | `rebuild_brand_list_tab.py` | ブランド一覧タブ |
| 3 | `rebuild_xxx_v3_complete.py` | 該当ブランドタブ |
| 4 | `build_movement_tabs.py` | 駆動方式タブ（Phase 2で実行済みならスキップ可） |
| 5 | `build_parts_tabs.py` | パーツタブ（Phase 2で実行済みならスキップ可） |

### 新しい会話でもOK

新しい会話を始めても、以下から文脈を復元できる：
- プロジェクトルール: `CLAUDE.md`（このファイル）
- データソース: `~/Desktop/時計データ_分類済み.csv`
- 過去の変更履歴: Gitコミット履歴
- 開発ログ: Obsidian `/開発ログ/watch-market-analysis_*.md`

---

## 新しいブランドタブを追加する場合

1. **データ確認**: CSVで該当ブランドの商品数を確認
2. **スクリプト作成**: `rebuild_{brandname}_v3_complete.py` を作成（既存ブランドをテンプレートとして模倣）
3. **HTML挿入位置**: 最後のブランドタブの終了位置をネストカウントで特定
4. **実行と検証**: ブラウザで確認
5. **Git commit & Obsidianノート作成**

---

## ブランドカラー定義

| ブランド | カラー | コード |
|---------|--------|--------|
| SEIKO | ブルー系 | `#1976d2`, `#e3f2fd` |
| CASIO | レッド系 | `#e63946`, `#ffe5e5` |
| CITIZEN | シアン系 | `#1565c0`, `#e3f2fd` |
| Orient | オレンジ系 | `#FF6B35`, `#FFE5D9` |

新ブランド追加時は既存カラーと被らないように選択すること。

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| タブクリックで何も表示されない | コンテンツdivが未実装 | 該当スクリプトを実行 |
| Top30が空（0行） | JSONから生成している | CSVから直接生成するよう修正 |
| タブが相互に上書き | 正規表現を使っている | 文字列位置ベースに変更 |
| ファイルサイズが増加しない | コンテンツ未挿入 | 挿入位置を確認 |

---

## 開発ログルール

- 重要な変更・修正を行った場合は Obsidian `/開発ログ/` にノートを作成
- **命名規則**: `watch-market-analysis_{変更内容}_{日付}.md`
- **必須項目**: 問題・原因・修正内容・失敗事例（該当時）・再発防止策・ステータス
- CLAUDE.md には教訓・ルールのみ記載。作業記録はObsidianとGit履歴に委ねる

---

**このファイルは、プロジェクトの重要なルールと再発防止策を記録しています。**
**タブの追加・修正を行う際は、必ずこのファイルを参照してください。**
