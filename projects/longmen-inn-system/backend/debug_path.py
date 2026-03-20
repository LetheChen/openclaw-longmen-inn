from pathlib import Path

current = Path(__file__).resolve()
print(f"当前文件: {current}")
print(f"上一级: {current.parent}")
print(f"上两级: {current.parent.parent}")
print(f"上三级: {current.parent.parent.parent}")
print(f"上四级: {current.parent.parent.parent.parent}")
print(f"上五级: {current.parent.parent.parent.parent.parent}")

root = current.parent.parent.parent.parent.parent
print(f"\nROOT路径: {root}")
print(f"LEDGER.md存在: {(root / 'LEDGER.md').exists()}")
print(f"ROSTER.md存在: {(root / 'ROSTER.md').exists()}")
