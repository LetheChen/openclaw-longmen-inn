"""
允许 python -m app.cli 调用
"""
from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
