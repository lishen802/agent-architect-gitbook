#!/usr/bin/env python3
"""依次运行 assets/ 下全部 build-*.py，重建书中 SVG 插图。"""
import pathlib
import subprocess
import sys

here = pathlib.Path(__file__).resolve().parent
scripts = sorted(p for p in here.glob("build-*.py") if p.name != "build-all.py")
for script in scripts:
    print(f"== {script.name}")
    subprocess.run([sys.executable, "-B", str(script)], cwd=here, check=True)
print(f"完成：{len(scripts)} 个构建脚本")
