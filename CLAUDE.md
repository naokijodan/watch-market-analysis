# watch-market-analysis プロジェクトルール

## 🎯 プロジェクト概要
eBay時計販売データの分析システム
- SEIKO、CASIO、CITIZEN、Orientなどのブランド別詳細分析
- HTMLタブ形式で複数ブランドの統計・人気モデル・仕入れ戦略を提供

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
├── index.html                        # メインHTML（547.5 KB）
├── 時計データ_分類済み.csv          # データソース（~/Desktop/）
├── rebuild_seiko_v3_complete.py     # SEIKOタブ再構築
├── rebuild_casio_v3_complete.py     # CASIOタブ再構築
├── rebuild_citizen_v3_complete.py   # CITIZENタブ再構築
├── rebuild_orient_v3_complete.py    # Orientタブ再構築
├── rebuild_all_tabs.py              # 全タブ一括再構築
└── CLAUDE.md                         # このファイル
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

**このファイルは、プロジェクトの重要なルールと再発防止策を記録しています。**
**タブの追加・修正を行う際は、必ずこのファイルを参照してください。**
