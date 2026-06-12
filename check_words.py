"""
你画我猜词库维护工具
====================
检查 CSV 词库中的常见问题：
  - 重复词条
  - 序号不连续
  - 空词条行

用法：
  python check_words.py                    # 检查默认 CSV 文件
  python check_words.py 你画我猜词库.csv    # 指定文件
"""

import csv
import sys
from collections import Counter
from pathlib import Path

# 修复 Windows 下 GBK 终端输出 emoji 报错的问题
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def check_csv(filepath: str) -> int:
    """检查 CSV 词库，返回发现的问题数。"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ 文件不存在: {filepath}")
        return 1

    print(f"📋 检查文件: {path.name}\n{'=' * 50}")

    issues = 0

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers_raw = next(reader, None)
        if headers_raw is None:
            print("❌ CSV 文件为空")
            return 1
        headers = [h.strip() for h in headers_raw]

        rows = []
        for raw_row in reader:
            row = [v.strip() for v in raw_row]
            while len(row) < len(headers):
                row.append("")
            rows.append(dict(zip(headers, row)))

    # ---- 1. 空词条 ----
    empty_indices = []
    for r in rows:
        idx = r.get("序号", "")
        word = r.get("词", "")
        if not word:
            empty_indices.append(idx)
    if empty_indices:
        print(f"⚠️  发现 {len(empty_indices)} 个空词条行（序号: {', '.join(empty_indices)}）")
        issues += 1
    else:
        print("✅ 无空词条行")

    # ---- 2. 序号连续性 ----
    indices = []
    for r in rows:
        try:
            indices.append(int(r.get("序号", "0")))
        except ValueError:
            pass
    if indices:
        expected = list(range(1, len(indices) + 1))
        if indices != expected:
            gaps = [i for i, (a, b) in enumerate(zip(indices, expected), 1) if a != b]
            print(f"⚠️  序号不连续！问题位置约在第 {gaps[:5]}... 行附近（共 {len(gaps)} 处）")
            issues += 1
        else:
            print(f"✅ 序号连续 (1 ~ {len(indices)})")

    # ---- 3. 重复词条 ----
    words = [r.get("词", "") for r in rows if r.get("词", "")]
    counter = Counter(words)
    duplicates = {w: c for w, c in counter.items() if c > 1}
    if duplicates:
        print(f"❌ 发现 {len(duplicates)} 个重复词条:")
        for w, c in sorted(duplicates.items(), key=lambda x: -x[1]):
            dup_rows = [r.get("序号", "?") for r in rows if r.get("词") == w]
            print(f"   · 「{w}」出现 {c} 次（序号: {', '.join(dup_rows)}）")
        issues += len(duplicates)
    else:
        print("✅ 无重复词条")

    # ---- 汇总 ----
    print(f"{'=' * 50}")
    print(f"📊 词库总数: {len(words)} 条")
    if issues == 0:
        print("🎉 词库检查全部通过！")
    else:
        print(f"⚠️  共发现 {issues} 个问题，请修复后重新检查")
    return issues


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "你画我猜词库.csv"
    sys.exit(check_csv(csv_path))
