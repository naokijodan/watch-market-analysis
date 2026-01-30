# セッション1: 設計とプロンプト生成

## あなたの役割
現状を分析し、セッション2とセッション3が実行できる**具体的なプロンプト（指示書）**を作成する。

## 重要な原則
- **READ ONLY**: このセッションではファイルを一切変更しない
- **成果物**: セッション2とセッション3用の実行可能なプロンプトを作成

---

## タスク1: 現状確認

### 実行内容
`index.html` の全体分析タブ（id="overview"）を読み、以下を特定する：

1. **市場インサイトの古い文言**
2. **ブランド別グラフの古いJavaScriptコード**

### 実行コマンド
```python
Read(file_path="/Users/naokijodan/Desktop/watch-market-analysis/index.html", offset=300, limit=100)
```

範囲を調整して、以下を見つける：
- `<h3>💡 市場インサイト</h3>` の直後のリスト
- ブランド別グラフのPlotlyスクリプト（`brandPieChart` または `brandBarChart`）

---

## タスク2: 置換対象の特定と記録

### 市場インサイト
**探す文字列**:
```html
<li>🔝 最大カテゴリ: CASIO (3813件) とSEIKO (3278件) で市場の過半数を占める</li>
```

この文字列が**一意である**ことを確認：
```bash
grep -c "CASIO (3813件) とSEIKO (3278件)" index.html
```
結果が「1」であることを確認。

**前後のコンテキスト**も記録（5行前後）:
```python
Read(file_path="index.html", offset=<該当行の5行前>, limit=15)
```

### ブランド別グラフ
**探すコードブロック**:
グラフデータを含むスクリプトブロック全体。例：
```javascript
const data = [{"labels": ["CASIO", "SEIKO", ...], "values": [3813, 3278, ...], "type": "pie"}];
```

このコードブロックが**一意である**ことを確認：
- 配列の値 `[3813, 3278, 419, 361, ...]` で検索
- 1箇所だけヒットすることを確認

**前後のコンテキスト**も記録。

---

## タスク3: セッション2用プロンプトの生成

以下の形式でファイルを作成：

**ファイル名**: `SESSION_2_PROMPT.md`

**内容**:
```markdown
# セッション2: 市場インサイトの更新

## 実行内容
`index.html` の市場インサイトを1箇所だけ置換する。

## 置換対象

### ファイルパス
/Users/naokijodan/Desktop/watch-market-analysis/index.html

### 置換前の文字列（完全一致）
[ここに実際に見つけた文字列を貼り付け]

例：
```html
                <li>🔝 最大カテゴリ: CASIO (3813件) とSEIKO (3278件) で市場の過半数を占める</li>
```
（インデントも含めて完全に一致する文字列）

### 置換後の文字列
```html
                <li>🔝 最大カテゴリ: SEIKO (7,524件) とCASIO (6,300件) で市場をリード</li>
```

### コンテキスト（確認用）
この文字列の前後5行：
```html
[前後のコンテキストをここに貼り付け]
```

## 実行コマンド
```python
Edit(
    file_path="/Users/naokijodan/Desktop/watch-market-analysis/index.html",
    old_string="[上記の置換前の文字列]",
    new_string="[上記の置換後の文字列]"
)
```

## 検証手順

### 1. 置換が成功したことを確認
```bash
grep -c "SEIKO (7,524件) とCASIO (6,300件)" index.html
```
結果が「1」であること。

### 2. 他のタブが存在することを確認
```bash
grep -c 'id="parts"' index.html     # 1
grep -c 'id="bundle"' index.html    # 1
grep -c 'id="recommend"' index.html # 1
```
全て「1」であること。

### 3. Git commit
```bash
git add index.html
git commit -m "fix: 市場インサイトを最新データに更新 (SEIKO 7,524件, CASIO 6,300件)"
```

## 検証に失敗した場合
```bash
git reset --hard HEAD
```
セッション1に戻って確認。
```

---

## タスク4: セッション3用プロンプトの生成

同様に `SESSION_3_PROMPT.md` を作成：

**内容**:
```markdown
# セッション3: ブランド別グラフデータの更新

## 実行内容
`index.html` のブランド別グラフデータを1箇所だけ置換する。

## 置換対象

### ファイルパス
/Users/naokijodan/Desktop/watch-market-analysis/index.html

### 置換前のコードブロック（完全一致）
[ここに実際に見つけたコードブロックを貼り付け]

例：
```javascript
    const data = [{"labels": ["CASIO", "SEIKO", "OMEGA", "CITIZEN", "Orient", "TAG HEUER", "GUCCI", "ROLEX", "Hamilton", "Longines"], "values": [3813, 3278, 419, 361, 300, 230, 138, 106, 98, 90], "type": "pie"}];
```

### 置換後のコードブロック
```javascript
    const data = [{"labels": ["SEIKO", "CASIO", "Longines", "(不明)", "OMEGA", "GUCCI", "CITIZEN", "Tissot", "Orient", "ROLEX"], "values": [7524, 6300, 2984, 1425, 1375, 982, 897, 684, 556, 471], "type": "pie"}];
```

### コンテキスト（確認用）
この文字列の前後5行：
```javascript
[前後のコンテキストをここに貼り付け]
```

## 実行コマンド
```python
Edit(
    file_path="/Users/naokijodan/Desktop/watch-market-analysis/index.html",
    old_string="[上記の置換前のコードブロック]",
    new_string="[上記の置換後のコードブロック]"
)
```

## 検証手順

### 1. 置換が成功したことを確認
```bash
grep -c '"SEIKO", "CASIO", "Longines"' index.html
```
結果が「1」であること。

### 2. 他のタブが存在することを確認
```bash
grep -c 'id="parts"' index.html     # 1
grep -c 'id="bundle"' index.html    # 1
grep -c 'id="recommend"' index.html # 1
```
全て「1」であること。

### 3. Git commit
```bash
git add index.html
git commit -m "fix: ブランド別グラフを最新データに更新 (SEIKO 7,524件, CASIO 6,300件)"
```

## 検証に失敗した場合
```bash
git reset --hard HEAD
```
セッション1に戻って確認。
```

---

## 成果物

このセッションの完了時に以下のファイルが作成されていること：

1. `SESSION_2_PROMPT.md` - セッション2用の実行可能な指示書
2. `SESSION_3_PROMPT.md` - セッション3用の実行可能な指示書

これらのファイルには：
- **実際のコード（置換前）** が正確に記載されている
- **前後のコンテキスト** が含まれている
- **検証手順** が明確に記載されている

---

## 注意事項

- このセッションではファイルを変更しない
- 置換対象の文字列は**完全に一致**するものを記録
- インデント、スペース、改行も含めて正確にコピー
- 一意性を必ず確認（grep -c で「1」であること）
