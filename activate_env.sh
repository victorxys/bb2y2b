#!/bin/bash
# 激活虚拟环境的便捷脚本
echo "正在激活虚拟环境..."
source myenv/bin/activate
echo "虚拟环境已激活！"
echo "Python版本: $(python --version)"
echo "当前工作目录: $(pwd)"
echo ""
echo "使用 'deactivate' 命令退出虚拟环境"
echo "使用 'python your_script.py' 运行Python脚本"