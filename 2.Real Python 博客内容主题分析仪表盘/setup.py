#!/usr/bin/env python3
"""
Real Python 博客内容主题分析仪表盘 - 自动化设置脚本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行系统命令并处理错误"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - 完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败!")
        print(f"错误信息: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安装Python包依赖"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ 未找到 {requirements_file} 文件")
        return False
    
    command = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
    return run_command(command, "安装Python包依赖")

def download_nltk_data():
    """下载NLTK数据包"""
    nltk_downloads = [
        "stopwords",
        "wordnet", 
        "averaged_perceptron_tagger",
        "punkt"
    ]
    
    for package in nltk_downloads:
        command = [
            sys.executable, "-c", 
            f"import nltk; nltk.download('{package}', quiet=True); print('下载 {package} 完成')"
        ]
        
        success = run_command(command, f"下载NLTK数据包: {package}")
        if not success:
            print(f"⚠️  警告: {package} 下载失败，可能需要手动安装")

def download_spacy_model():
    """下载SpaCy英文模型"""
    command = [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
    return run_command(command, "下载SpaCy英文模型")

def verify_installation():
    """验证安装是否成功"""
    print(f"\n{'='*50}")
    print("🔍 验证安装...")
    print(f"{'='*50}")
    
    # 测试导入主要包
    packages_to_test = [
        ("pandas", "数据处理"),
        ("streamlit", "Web框架"),
        ("sklearn", "机器学习"),
        ("nltk", "自然语言处理"),
        ("spacy", "SpaCy NLP"),
        ("plotly", "数据可视化"),
        ("wordcloud", "词云生成")
    ]
    
    failed_imports = []
    
    for package, description in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {description} ({package})")
        except ImportError:
            print(f"❌ {description} ({package}) - 导入失败")
            failed_imports.append(package)
    
    # 测试SpaCy模型
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ SpaCy英文模型")
    except OSError:
        print("❌ SpaCy英文模型 - 未找到")
        failed_imports.append("en_core_web_sm")
    
    # 测试NLTK数据
    try:
        import nltk
        from nltk.corpus import stopwords
        stopwords.words('english')
        print("✅ NLTK停用词数据")
    except:
        print("❌ NLTK停用词数据")
        failed_imports.append("nltk_data")
    
    return len(failed_imports) == 0, failed_imports

def create_run_script():
    """创建运行脚本"""
    script_content = '''@echo off
echo 启动 Real Python 博客内容主题分析仪表盘...
echo.
echo 请确保已运行 setup.py 完成初始化设置
echo.
streamlit run topic_dashboard.py
pause
'''
    
    try:
        with open("run_dashboard.bat", "w", encoding="utf-8") as f:
            f.write(script_content)
        print("✅ 创建Windows运行脚本: run_dashboard.bat")
    except Exception as e:
        print(f"⚠️  创建运行脚本失败: {e}")

def main():
    """主函数"""
    print("🚀 Real Python 博客内容主题分析仪表盘 - 自动化设置")
    print("=" * 60)
    
    # 1. 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 2. 安装Python包
    if not install_requirements():
        print("❌ Python包安装失败，请检查网络连接或手动安装")
        sys.exit(1)
    
    # 3. 下载NLTK数据
    download_nltk_data()
    
    # 4. 下载SpaCy模型
    if not download_spacy_model():
        print("⚠️  SpaCy模型下载失败，请手动运行:")
        print("   python -m spacy download en_core_web_sm")
    
    # 5. 验证安装
    success, failed = verify_installation()
    
    if success:
        print(f"\n{'='*50}")
        print("🎉 安装完成！所有组件都已正确安装")
        print(f"{'='*50}")
        print("\n📋 下一步操作:")
        print("1. 确保 real_python_courses_analysis.csv 文件在当前目录")
        print("2. 运行以下命令启动应用:")
        print("   streamlit run topic_dashboard.py")
        print("\n或者运行创建的批处理文件:")
        print("   run_dashboard.bat (Windows)")
        
        # 创建运行脚本
        create_run_script()
        
    else:
        print(f"\n{'='*50}")
        print("⚠️  安装过程中出现问题")
        print(f"{'='*50}")
        print("未成功安装的组件:")
        for item in failed:
            print(f"  ❌ {item}")
        print("\n请查看上面的错误信息并手动解决问题")
        
    print(f"\n{'='*50}")
    print("📚 如需帮助，请查看 README.md 文件")
    print(f"{'='*50}")

if __name__ == "__main__":
    main() 