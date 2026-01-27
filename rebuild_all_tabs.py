#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKO・CASIO・CITIZENタブを同時に再構築するスクリプト
タブ間の相互干渉を防ぎ、安全に全タブを更新
"""

import subprocess
import sys

print("🔄 全タブ同時再構築開始...")
print("=" * 60)
print()

# 1. SEIKOタブを再構築
print("📊 1/3: SEIKOタブ再構築中...")
print("-" * 60)
result_seiko = subprocess.run([sys.executable, 'rebuild_seiko_v3_complete.py'],
                              capture_output=True, text=True)
print(result_seiko.stdout)
if result_seiko.returncode != 0:
    print("❌ SEIKOタブ再構築エラー:")
    print(result_seiko.stderr)
    sys.exit(1)

print()

# 2. CASIOタブを再構築
print("🔴 2/3: CASIOタブ再構築中...")
print("-" * 60)
result_casio = subprocess.run([sys.executable, 'rebuild_casio_v3_complete.py'],
                              capture_output=True, text=True)
print(result_casio.stdout)
if result_casio.returncode != 0:
    print("❌ CASIOタブ再構築エラー:")
    print(result_casio.stderr)
    sys.exit(1)

print()

# 3. CITIZENタブを再構築
print("🔵 3/3: CITIZENタブ再構築中...")
print("-" * 60)
result_citizen = subprocess.run([sys.executable, 'rebuild_citizen_v3_complete.py'],
                                capture_output=True, text=True)
print(result_citizen.stdout)
if result_citizen.returncode != 0:
    print("❌ CITIZENタブ再構築エラー:")
    print(result_citizen.stderr)
    sys.exit(1)

print()
print("=" * 60)
print("✅ 全タブ（SEIKO・CASIO・CITIZEN）の同時再構築完了！")
print()
print("📝 確認事項:")
print("  ✓ SEIKOタブ: 24ライン、Top15モデル")
print("  ✓ CASIOタブ: 11ライン、Top15モデル")
print("  ✓ CITIZENタブ: ライン別分析、Top15モデル")
