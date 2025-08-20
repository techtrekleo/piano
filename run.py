#!/usr/bin/env python3
"""
音乐可视化器启动脚本
让用户选择运行基础版本还是高级版本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    required_libs = ['librosa', 'pygame', 'matplotlib', 'numpy', 'scipy']
    missing_libs = []
    
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)
    
    if missing_libs:
        print("❌ 缺少以下依赖库：")
        for lib in missing_libs:
            print(f"   - {lib}")
        print("\n请先运行安装脚本：")
        print("python install.py")
        return False
    
    return True

def show_menu():
    """显示菜单"""
    print("🎵 音乐可视化器 - See Music")
    print("=" * 40)
    print("请选择要运行的版本：")
    print("1. 高级版本 (推荐) - 更多功能和更好的效果")
    print("2. 基础版本 - 简单但稳定的版本")
    print("3. 安装依赖库")
    print("4. 退出")
    print("=" * 40)

def run_version(version):
    """运行指定版本"""
    if version == "advanced":
        if os.path.exists("advanced_visualizer.py"):
            print("🚀 启动高级版本...")
            subprocess.run([sys.executable, "advanced_visualizer.py"])
        else:
            print("❌ 找不到高级版本文件")
    elif version == "basic":
        if os.path.exists("music_visualizer.py"):
            print("🚀 启动基础版本...")
            subprocess.run([sys.executable, "music_visualizer.py"])
        else:
            print("❌ 找不到基础版本文件")
    elif version == "install":
        if os.path.exists("install.py"):
            print("🔧 启动安装脚本...")
            subprocess.run([sys.executable, "install.py"])
        else:
            print("❌ 找不到安装脚本")

def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == "1":
                run_version("advanced")
                break
            elif choice == "2":
                run_version("basic")
                break
            elif choice == "3":
                run_version("install")
                input("\n按回车键继续...")
            elif choice == "4":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入1-4")
                input("按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except EOFError:
            print("\n\n👋 再见！")
            break

if __name__ == "__main__":
    main()
