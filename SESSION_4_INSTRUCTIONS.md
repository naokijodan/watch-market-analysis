# セッション4: 最終検証とコミット

## あなたの役割
セッション2とセッション3の変更が正しく反映され、他のタブが破壊されていないことを確認し、Gitにコミットする。

## 重要な原則
- **検証が最優先**: 全てのタブが正しく表示されることを確認
- **問題があれば即座に停止**: 検証に失敗したらコミットしない
- **成果物**: 正しく更新されたindex.htmlと、適切なGitコミット

---

## タスク1: セッション2の変更確認

### 実行内容
市場インサイトが正しく更新されていることを確認する。

### 実行コマンド
```bash
grep -c "SEIKO (7,524件) とCASIO (6,300件)" /Users/naokijodan/Desktop/watch-market-analysis/index.html
```

### 期待される結果
```
1
```

結果が「1」であること。

### 検証に失敗した場合
```bash
cd /Users/naokijodan/Desktop/watch-market-analysis
git log --oneline -5  # 最近のコミットを確認
git revert <セッション2のコミットハッシュ> --no-edit
git push
```

セッション1に戻って再度確認。

---

## タスク2: セッション3の変更確認

### 実行内容
ブランド別グラフデータが正しく更新されていることを確認する。

### 実行コマンド
```bash
grep -c '"SEIKO", "CASIO", "Longines"' /Users/naokijodan/Desktop/watch-market-analysis/index.html
```

### 期待される結果
```
1
```

結果が「1」であること。

### 検証に失敗した場合
```bash
cd /Users/naokijodan/Desktop/watch-market-analysis
git log --oneline -5  # 最近のコミットを確認
git revert <セッション3のコミットハッシュ> --no-edit
git push
```

セッション1に戻って再度確認。

---

## タスク3: 重要タブの存在確認

### 実行内容
削除されてはいけないタブが全て存在することを確認する。

### 実行コマンド
```bash
cd /Users/naokijodan/Desktop/watch-market-analysis

# パーツタブの存在確認
grep -c 'id="parts"' index.html

# まとめ売りタブの存在確認
grep -c 'id="bundle"' index.html

# おすすめ出品順序タブの存在確認
grep -c 'id="recommend"' index.html

# 自動巻タブの存在確認
grep -c 'id="automatic"' index.html

# クオーツタブの存在確認
grep -c 'id="quartz"' index.html

# ソーラータブの存在確認
grep -c 'id="solar"' index.html

# 手巻きタブの存在確認
grep -c 'id="manual"' index.html

# スマートウォッチタブの存在確認
grep -c 'id="smartwatch"' index.html

# デジタルタブの存在確認
grep -c 'id="digital"' index.html
```

### 期待される結果
全てのコマンドが「1」を返すこと。

### 検証に失敗した場合
**即座に停止**し、以下を実行：
```bash
git log --oneline -5
# セッション2とセッション3のコミットを両方revert
git revert <セッション3のコミットハッシュ> --no-edit
git revert <セッション2のコミットハッシュ> --no-edit
git push
```

セッション1に戻って原因を調査。

---

## タスク4: ブラウザでの表示確認（推奨）

### 実行内容
ローカルサーバーを起動してブラウザで確認する。

### 実行コマンド
```bash
cd /Users/naokijodan/Desktop/watch-market-analysis

# Pythonサーバーを起動（バックグラウンド）
python3 -m http.server 8000 &

# サーバーのプロセスIDを記録
echo $! > .server_pid
```

### ブラウザでの確認手順
1. ブラウザで `http://localhost:8000/` を開く
2. 以下のタブをクリックして表示を確認：
   - ✅ **全体分析**
     - 市場インサイト: "SEIKO (7,524件) とCASIO (6,300件)" と表示されているか
     - ブランド別グラフ: SEIKOとCASIOが上位に表示されているか
   - ✅ 自動巻
   - ✅ クオーツ
   - ✅ ソーラー
   - ✅ 手巻き
   - ✅ スマートウォッチ
   - ✅ デジタル
   - ✅ **パーツ** ← 重要：このタブが存在し、データが表示されるか
   - ✅ **まとめ売り** ← 重要：このタブが存在し、データが表示されるか
   - ✅ **おすすめ出品順序** ← 重要：このタブが存在し、データが表示されるか
   - ✅ 各ブランドタブ（SEIKO, CASIO, Longines, OMEGA, GUCCI, CITIZEN, Tissot, Orient, ROLEX）

3. JavaScriptコンソールを開き、エラーがないことを確認（F12 → Console）

### サーバーの停止
```bash
# サーバーを停止
kill $(cat .server_pid)
rm .server_pid
```

### 検証基準
- 全タブが正しく表示される
- 全体分析タブのデータが最新（SEIKO 7,524件、CASIO 6,300件）
- グラフが正しく描画される
- JavaScriptエラーが出ていない

### 検証に失敗した場合
**即座に停止**し、タスク3の「検証に失敗した場合」の手順を実行。

---

## タスク5: GitHub Pagesでの最終確認（オプション）

### 実行内容
GitHub Pagesが正しく更新されていることを確認する。

### 実行手順
1. ブラウザで `https://naokijodan.github.io/watch-market-analysis/` を開く
2. 全体分析タブを確認：
   - 市場インサイト: "SEIKO (7,524件) とCASIO (6,300件)"
   - ブランド別グラフ: SEIKOとCASIOが上位
3. パーツ、まとめ売り、おすすめ出品順序タブが存在することを確認

### 注意事項
GitHub Pagesの反映には数分かかる場合があります。

---

## タスク6: Obsidianノート作成

### 実行内容
今回の更新内容を記録する。

### ファイル名
`/開発ログ/watch-market-analysis_全体分析タブ更新_2026-01-30.md`

### 内容
```markdown
# 全体分析タブ更新 - 2026-01-30

## ステータス
✅ 完了

## 問題
- 全体分析タブのデータが古い（CASIO 3,813件、SEIKO 3,278件）
- ブランド別グラフも古いデータのまま
- 実際は SEIKO 7,524件、CASIO 6,300件に更新が必要

## 修正内容

### セッション1: 設計とプロンプト生成
- index.html を読み取り、置換対象の古い文字列を特定
- SESSION_2_PROMPT.md を生成（市場インサイト更新用）
- SESSION_3_PROMPT.md を生成（ブランド別グラフ更新用）

### セッション2: 市場インサイトの更新
- 市場インサイトを1箇所だけ置換
- 置換前: "CASIO (3813件) とSEIKO (3278件) で市場の過半数を占める"
- 置換後: "SEIKO (7,524件) とCASIO (6,300件) で市場をリード"
- 検証: grep で他のタブが存在することを確認
- Git commit & push

### セッション3: ブランド別グラフデータの更新
- ブランド別グラフデータを1箇所だけ置換
- 新しいTop10: SEIKO, CASIO, Longines, (不明), OMEGA, GUCCI, CITIZEN, Tissot, Orient, ROLEX
- 検証: grep で他のタブが存在することを確認
- Git commit & push

### セッション4: 最終検証
- 全タブの存在確認（grep）
- ブラウザでの表示確認
- GitHub Pages での確認
- Obsidianノート作成

## アプローチ
**アンカーベースの外科的置換**
- 範囲指定は一切行わない
- 一意な文字列を完全に特定してから置換
- 各セッションで検証を実施
- 問題があれば即座に停止・revert

## 教訓
- 範囲指定（行番号、開始タグ〜終了タグ）は絶対に使わない
- 一意な文字列を grep -c で確認してから置換
- 1つずつ実行、1つずつ検証
- 各セッションでコミットすることで、問題があれば部分的にrevert可能

## 参考
- SESSION_1_INSTRUCTIONS.md
- SESSION_2_PROMPT.md（セッション1が生成）
- SESSION_3_PROMPT.md（セッション1が生成）
- SESSION_4_INSTRUCTIONS.md
- OVERVIEW_UPDATE_PLAN.md（失敗した計画書）

## 検証結果
- ✅ 市場インサイト: SEIKO (7,524件) とCASIO (6,300件)
- ✅ ブランド別グラフ: 最新Top10に更新
- ✅ パーツタブ: 存在
- ✅ まとめ売りタブ: 存在
- ✅ おすすめ出品順序タブ: 存在
- ✅ 自動巻タブ: 存在
- ✅ JavaScriptエラー: なし
- ✅ GitHub Pages: 正しく表示
```

### 実行コマンド
```bash
# Obsidianノートを作成
# （mcp__obsidian__write_note ツールを使用）
```

---

## タスク7: 作業完了報告

### 実行内容
ユーザーに以下を報告する：

1. ✅ セッション2の変更確認完了
2. ✅ セッション3の変更確認完了
3. ✅ 全タブの存在確認完了
4. ✅ ブラウザでの表示確認完了（該当する場合）
5. ✅ GitHub Pages での確認完了（該当する場合）
6. ✅ Obsidianノート作成完了

### 報告内容
```
全体分析タブの更新が完了しました。

【更新内容】
- 市場インサイト: SEIKO (7,524件) とCASIO (6,300件) に更新
- ブランド別グラフ: 最新Top10に更新

【検証結果】
- ✅ 市場インサイトが正しく更新されている
- ✅ ブランド別グラフが正しく更新されている
- ✅ パーツタブが存在する
- ✅ まとめ売りタブが存在する
- ✅ おすすめ出品順序タブが存在する
- ✅ 自動巻タブが存在する
- ✅ 他の全タブが正常に表示される
- ✅ JavaScriptエラーなし

【GitHub Pages】
https://naokijodan.github.io/watch-market-analysis/

【Obsidianノート】
/開発ログ/watch-market-analysis_全体分析タブ更新_2026-01-30.md
```

---

## 🚨 緊急時の対応

### 問題が発生した場合
```bash
cd /Users/naokijodan/Desktop/watch-market-analysis

# 最近のコミットを確認
git log --oneline -5

# セッション3のコミットをrevert
git revert <セッション3のコミットハッシュ> --no-edit

# セッション2のコミットをrevert
git revert <セッション2のコミットハッシュ> --no-edit

# プッシュ
git push
```

### ロールバック後の確認
```bash
# 重要タブの存在確認
grep -c 'id="parts"' index.html       # 1
grep -c 'id="bundle"' index.html      # 1
grep -c 'id="recommend"' index.html   # 1
grep -c 'id="automatic"' index.html   # 1
```

全て「1」が返ることを確認。

---

## 成功基準

このセッションが成功するためには：

1. ✅ セッション2の変更が正しく反映されている
2. ✅ セッション3の変更が正しく反映されている
3. ✅ パーツタブが存在する
4. ✅ まとめ売りタブが存在する
5. ✅ おすすめ出品順序タブが存在する
6. ✅ 自動巻タブが存在する
7. ✅ 他の全タブが存在する
8. ✅ JavaScriptエラーが出ていない
9. ✅ GitHub Pagesで正しく表示される
10. ✅ Obsidianノートが作成されている

---

## 注意事項

- **検証なしで報告しない**: 全ての検証を実施してから報告する
- **問題があれば即座に停止**: 検証に失敗したらコミットせず、revertする
- **セッション2と3の両方を検証**: 片方だけでなく、両方が正しく反映されていることを確認
- **重要タブの存在確認は必須**: パーツ、まとめ売り、おすすめ出品順序タブが削除されていないことを確認

**このセッションは最終検証です。慎重に実行してください。**
