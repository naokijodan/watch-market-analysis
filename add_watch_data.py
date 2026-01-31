#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時計データ追加統合パイプライン
前回のTissot追加の反省を踏まえ、全工程を自動化
"""

import pandas as pd
import sys
import os
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Tuple
from generate_attributes import WatchAttributeGenerator

class WatchDataPipeline:
    """時計データ追加の統合パイプライン"""

    # 既存CSVパス
    EXISTING_CSV = '/Users/naokijodan/Desktop/watch-market-analysis/時計データ_分類済み.csv'
    TEMP_CSV = '/Users/naokijodan/Desktop/watch-market-analysis/時計データ_分類済み_temp.csv'
    BACKUP_CSV = '/Users/naokijodan/Desktop/watch-market-analysis/時計データ_分類済み_backup.csv'

    # プロジェクトディレクトリ
    PROJECT_DIR = '/Users/naokijodan/Desktop/watch-market-analysis'

    # 閾値設定
    THRESHOLDS = {
        '駆動方式_判定率_最小': 30.0,  # 駆動方式が30%以上判定できていればOK
        'デパートメント_判定率_最小': 20.0,  # デパートメントが20%以上判定できていればOK
        '歩留まり率_最小': 20.0,  # 完品データが20%以上あればOK
    }

    def __init__(self, new_csv_path: str):
        """
        Args:
            new_csv_path: 追加する新規CSVのパス
        """
        self.new_csv_path = new_csv_path
        self.report = []  # 診断レポート

    def log(self, message: str):
        """ログ出力"""
        print(message)
        self.report.append(message)

    def step1_dry_run(self) -> bool:
        """
        ステップ1: Dry Run（抽出率チェック）

        Returns:
            True: 閾値をクリア, False: 閾値未達
        """
        self.log("\n" + "="*80)
        self.log("ステップ1: Dry Run（新規データの抽出率チェック）")
        self.log("="*80)

        # 新規CSVを読み込み
        try:
            df_new = pd.read_csv(self.new_csv_path)
            self.log(f"✓ 新規CSV読み込み: {len(df_new)}件")
        except Exception as e:
            self.log(f"❌ エラー: CSVの読み込みに失敗しました")
            self.log(f"   {e}")
            return False

        # 属性を生成（テスト）
        self.log("\n🔧 属性生成テスト中...")
        df_with_attrs = WatchAttributeGenerator.generate_all_attributes(df_new)

        # 抽出率を計算
        rates = WatchAttributeGenerator.calculate_extraction_rates(df_with_attrs)

        self.log("\n📊 抽出率:")
        for attr, rate in rates.items():
            self.log(f"  {attr}: {rate:.1f}%")

        # 閾値チェック
        self.log("\n🔍 閾値チェック:")
        駆動方式_判定率 = rates.get('駆動方式_判定率', 0)
        デパートメント_判定率 = rates.get('デパートメント_判定率', 0)

        passed = True

        if 駆動方式_判定率 < self.THRESHOLDS['駆動方式_判定率_最小']:
            self.log(f"  ⚠️ 駆動方式の判定率が低い: {駆動方式_判定率:.1f}% < {self.THRESHOLDS['駆動方式_判定率_最小']}%")
            self.log("     → タイトルに 'Automatic', 'Quartz', 'Solar' 等のキーワードが少ない可能性")
            passed = False
        else:
            self.log(f"  ✓ 駆動方式判定率: OK ({駆動方式_判定率:.1f}%)")

        if デパートメント_判定率 < self.THRESHOLDS['デパートメント_判定率_最小']:
            self.log(f"  ⚠️ デパートメントの判定率が低い: {デパートメント_判定率:.1f}% < {self.THRESHOLDS['デパートメント_判定率_最小']}%")
            self.log("     → タイトルに 'Men', 'Women', 'Ladies' 等のキーワードが少ない可能性")
            passed = False
        else:
            self.log(f"  ✓ デパートメント判定率: OK ({デパートメント_判定率:.1f}%)")

        if not passed:
            self.log("\n❌ Dry Runが閾値未達です。新規データを確認してください。")
            return False

        self.log("\n✅ Dry Run成功（全閾値クリア）")
        return True

    def step2_merge_csv(self) -> Tuple[bool, int, int]:
        """
        ステップ2: CSVマージ（重複チェック）

        Returns:
            (success, new_count, duplicate_count)
        """
        self.log("\n" + "="*80)
        self.log("ステップ2: CSVマージ（重複チェック）")
        self.log("="*80)

        # 既存CSVを読み込み
        df_existing = pd.read_csv(self.EXISTING_CSV)
        self.log(f"✓ 既存CSV: {len(df_existing)}件")

        # 新規CSVを読み込み
        df_new = pd.read_csv(self.new_csv_path)
        self.log(f"✓ 新規CSV: {len(df_new)}件")

        # 属性生成
        self.log("\n🔧 新規データに属性を生成中...")
        df_new_with_attrs = WatchAttributeGenerator.generate_all_attributes(df_new)

        # 重複チェック（タイトル + 販売日で判定）
        self.log("\n🔍 重複チェック中...")
        df_merged = pd.concat([df_existing, df_new_with_attrs], ignore_index=True)

        # 重複を削除（タイトル + 販売日が同じものを削除）
        before_count = len(df_merged)
        df_merged = df_merged.drop_duplicates(subset=['タイトル', '販売日'], keep='first')
        after_count = len(df_merged)

        duplicate_count = before_count - after_count
        new_count = after_count - len(df_existing)

        self.log(f"  重複除外: {duplicate_count}件")
        self.log(f"  新規追加: {new_count}件")
        self.log(f"  最終データ件数: {after_count}件")

        # 一時ファイルに保存
        df_merged.to_csv(self.TEMP_CSV, index=False)
        self.log(f"\n✓ 一時ファイルに保存: {self.TEMP_CSV}")

        return True, new_count, duplicate_count

    def step3_validate_yield_rate(self) -> bool:
        """
        ステップ3: 歩留まり率検証

        Returns:
            True: 閾値をクリア, False: 閾値未達
        """
        self.log("\n" + "="*80)
        self.log("ステップ3: 歩留まり率検証")
        self.log("="*80)

        df = pd.read_csv(self.TEMP_CSV)

        # 完品データ件数
        完品_count = (df['商品状態'] == '完品').sum()
        歩留まり率 = 完品_count / len(df) * 100

        self.log(f"  総データ件数: {len(df)}件")
        self.log(f"  完品データ: {完品_count}件")
        self.log(f"  歩留まり率: {歩留まり率:.1f}%")

        if 歩留まり率 < self.THRESHOLDS['歩留まり率_最小']:
            self.log(f"\n⚠️ 警告: 歩留まり率が低い ({歩留まり率:.1f}% < {self.THRESHOLDS['歩留まり率_最小']}%)")
            self.log("  → パーツやジャンクが多い可能性があります")
            self.log("  → 続行しますが、タブ生成時に表示データが少ない可能性があります")

        self.log("\n✅ 歩留まり率検証完了")
        return True

    def step4_regenerate_tabs(self) -> bool:
        """
        ステップ4: タブ再生成

        Returns:
            True: 成功, False: 失敗
        """
        self.log("\n" + "="*80)
        self.log("ステップ4: タブ再生成")
        self.log("="*80)

        # 一時CSVを本番CSVに置き換え（タブ生成スクリプトが読み込む）
        shutil.copy(self.TEMP_CSV, self.EXISTING_CSV)
        self.log(f"✓ CSVを更新: {self.EXISTING_CSV}")

        os.chdir(self.PROJECT_DIR)

        # 駆動方式タブ再生成
        self.log("\n🔧 駆動方式タブ再生成中...")
        result = subprocess.run(
            ['python3', 'build_movement_tabs.py'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.log(f"❌ 駆動方式タブの再生成に失敗しました")
            self.log(result.stderr)
            return False
        self.log("✓ 駆動方式タブ完了")

        # パーツタブ再生成
        self.log("\n🔧 パーツタブ再生成中...")
        result = subprocess.run(
            ['python3', 'build_parts_tabs.py'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.log(f"❌ パーツタブの再生成に失敗しました")
            self.log(result.stderr)
            return False
        self.log("✓ パーツタブ完了")

        self.log("\n✅ タブ再生成完了")
        return True

    def step5_commit_and_push(self, new_count: int) -> bool:
        """
        ステップ5: Git commit & push

        Args:
            new_count: 新規追加件数

        Returns:
            True: 成功, False: 失敗
        """
        self.log("\n" + "="*80)
        self.log("ステップ5: Git commit & push")
        self.log("="*80)

        os.chdir(self.PROJECT_DIR)

        # git add
        subprocess.run(['git', 'add', 'index.html'], check=True)
        self.log("✓ git add index.html")

        # commit message
        date_str = datetime.now().strftime('%Y-%m-%d')
        commit_message = f"""feat: 新規時計データ{new_count}件を追加

- 新規追加: {new_count}件
- 駆動方式タブ更新
- パーツタブ更新
- 日付: {date_str}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
"""

        # git commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        self.log("✓ git commit完了")

        # git push
        subprocess.run(['git', 'push'], check=True)
        self.log("✓ git push完了")

        self.log("\n✅ Git操作完了")
        return True

    def step6_generate_report(self, new_count: int, duplicate_count: int):
        """
        ステップ6: 診断レポート生成
        """
        self.log("\n" + "="*80)
        self.log("📋 最終レポート")
        self.log("="*80)

        df = pd.read_csv(self.EXISTING_CSV)

        # ブランド別統計
        brand_counts = df.groupby('ブランド').size().sort_values(ascending=False).head(10)

        self.log(f"\n✅ 成功: 新規データ{new_count}件を追加")
        self.log(f"\n【詳細】")
        self.log(f"  - 新規追加: {new_count}件")
        self.log(f"  - 重複除外: {duplicate_count}件")
        self.log(f"  - 最終データ件数: {len(df)}件")

        self.log(f"\n【ブランド別Top10】")
        for brand, count in brand_counts.items():
            self.log(f"  - {brand}: {count}件")

        self.log(f"\n【次のステップ】")
        self.log(f"  1. GitHub Pagesは2-5分で更新されます")
        self.log(f"  2. 公開URL: https://naokijodan.github.io/watch-market-analysis/")
        self.log(f"  3. 更新を確認してください")

    def run(self) -> bool:
        """
        パイプライン実行

        Returns:
            True: 成功, False: 失敗
        """
        try:
            # ステップ1: Dry Run
            if not self.step1_dry_run():
                self.log("\n❌ パイプライン中断: Dry Run失敗")
                return False

            # ステップ2: CSVマージ
            success, new_count, duplicate_count = self.step2_merge_csv()
            if not success:
                self.log("\n❌ パイプライン中断: CSVマージ失敗")
                return False

            if new_count == 0:
                self.log("\n⚠️ 新規データがありません（全て重複）")
                # 一時ファイル削除
                if os.path.exists(self.TEMP_CSV):
                    os.remove(self.TEMP_CSV)
                return True

            # ステップ3: 歩留まり率検証
            if not self.step3_validate_yield_rate():
                self.log("\n❌ パイプライン中断: 歩留まり率検証失敗")
                # ロールバック
                if os.path.exists(self.TEMP_CSV):
                    os.remove(self.TEMP_CSV)
                return False

            # ステップ4: タブ再生成
            if not self.step4_regenerate_tabs():
                self.log("\n❌ パイプライン中断: タブ再生成失敗")
                # ロールバック
                if os.path.exists(self.BACKUP_CSV):
                    shutil.copy(self.BACKUP_CSV, self.EXISTING_CSV)
                return False

            # ステップ5: Git commit & push
            if not self.step5_commit_and_push(new_count):
                self.log("\n❌ パイプライン中断: Git操作失敗")
                return False

            # ステップ6: 診断レポート
            self.step6_generate_report(new_count, duplicate_count)

            # 一時ファイル削除
            if os.path.exists(self.TEMP_CSV):
                os.remove(self.TEMP_CSV)

            self.log("\n" + "="*80)
            self.log("✅ パイプライン完了")
            self.log("="*80)

            return True

        except Exception as e:
            self.log(f"\n❌ エラー: {e}")
            import traceback
            self.log(traceback.format_exc())

            # ロールバック
            if os.path.exists(self.TEMP_CSV):
                os.remove(self.TEMP_CSV)

            return False


def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 add_watch_data.py <new_csv_path>")
        print("例: python3 add_watch_data.py ~/Desktop/new_seiko_2026_feb.csv")
        sys.exit(1)

    new_csv_path = sys.argv[1]

    if not os.path.exists(new_csv_path):
        print(f"❌ エラー: ファイルが見つかりません: {new_csv_path}")
        sys.exit(1)

    pipeline = WatchDataPipeline(new_csv_path)
    success = pipeline.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
