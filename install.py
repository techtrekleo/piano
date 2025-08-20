#!/usr/bin/env python3
"""
音乐可视化器自动安装脚本
自动安装所需的依赖库
"""

import subprocess
import sys
import os

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误：需要Python 3.7或更高版本")
        print(f"当前版本：{sys.version}")
        return False
    print(f"✅ Python版本检查通过：{sys.version}")
    return True

def install_package(package):
    """安装单个包"""
    try:
        print(f"📦 正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败：{e}")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    if not os.path.exists("requirements.txt"):
        print("❌ 找不到requirements.txt文件")
        return False
    
    print("📋 开始安装依赖库...")
    
    # 先升级pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip升级成功")
    except:
        print("⚠️ pip升级失败，继续安装...")
    
    # 安装依赖
    success_count = 0
    total_count = 0
    
    with open("requirements.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                total_count += 1
                if install_package(line):
                    success_count += 1
    
    print(f"\n📊 安装结果：{success_count}/{total_count} 个包安装成功")
    
    if success_count == total_count:
        print("🎉 所有依赖安装完成！")
        return True
    else:
        print("⚠️ 部分依赖安装失败，请手动安装")
        return False

def test_imports():
    """测试关键库是否可以导入"""
    print("\n🧪 测试库导入...")
    
    test_libs = [
        ("librosa", "音频分析"),
        ("pygame", "音频播放"),
        ("matplotlib", "可视化"),
        ("numpy", "数值计算"),
        ("scipy", "科学计算")
    ]
    
    success_count = 0
    for lib, desc in test_libs:
        try:
            __import__(lib)
            print(f"✅ {lib} ({desc}) 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {lib} ({desc}) 导入失败：{e}")
    
    if success_count == len(test_libs):
        print("🎉 所有库导入测试通过！")
        return True
    else:
        print("⚠️ 部分库导入失败")
        return False

def main():
    """主函数"""
    print("🎵 音乐可视化器安装脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    print("\n🚀 开始安装...")
    
    # 安装依赖
    if install_requirements():
        # 测试导入
        if test_imports():
            print("\n🎊 安装完成！现在可以运行音乐可视化器了")
            print("\n使用方法：")
            print("python advanced_visualizer.py  # 运行高级版本")
            print("python music_visualizer.py      # 运行基础版本")
        else:
            print("\n⚠️ 安装完成但部分库无法导入，请检查安装")
    else:
        print("\n❌ 安装失败，请检查错误信息")

if __name__ == "__main__":
    main()
