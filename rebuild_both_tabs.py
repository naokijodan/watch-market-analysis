#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIKOタブとCASIOタブを同時に再構築するスクリプト
"""

import subprocess
import sys

print("🔄 SEIKOタブとCASIOタブを同時再構築開始...")
print()

# 1. SEIKOタブを再構築
print("📊 1/2: SEIKOタブ再構築中...")
result_seiko = subprocess.run([sys.executable, 'rebuild_seiko_v3_complete.py'],
                              capture_output=True, text=True)
print(result_seiko.stdout)
if result_seiko.returncode != 0:
    print("❌ SEIKOタブ再構築エラー:")
    print(result_seiko.stderr)
    sys.exit(1)

print()

# 2. CASIOタブを再構築
print("🔴 2/2: CASIOタブ再構築中...")
result_casio = subprocess.run([sys.executable, 'rebuild_casio_v3_complete.py'],
                              capture_output=True, text=True)
print(result_casio.stdout)
if result_casio.returncode != 0:
    print("❌ CASIOタブ再構築エラー:")
    print(result_casio.stderr)
    sys.exit(1)

print()
print("✅ SEIKOタブとCASIOタブの同時再構築完了！")
