#!/usr/bin/env python3
"""依次运行 assets/ 下全部 build-*.py，重建书中 SVG 插图；任何脚本的断言失败都会使退出码非零。"""
import pathlib
import subprocess
import sys

here = pathlib.Path(__file__).resolve().parent
scripts = sorted(p for p in here.glob("build-*.py") if p.name != "build-all.py")
failed = []
for script in scripts:
    print(f"== {script.name}", flush=True)
    if subprocess.run([sys.executable, "-B", str(script)], cwd=here).returncode != 0:
        failed.append(script.name)
svgs = sorted(p.name for p in here.glob("*.svg"))
print(f"完成：{len(scripts)} 个构建脚本，{len(svgs)} 张 SVG；失败：{failed or '无'}")
sys.exit(1 if failed else 0)
