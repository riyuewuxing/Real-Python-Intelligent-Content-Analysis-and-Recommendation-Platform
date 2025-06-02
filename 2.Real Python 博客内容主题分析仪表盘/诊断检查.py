#!/usr/bin/env python3
"""
Real Python 博客内容主题分析仪表盘 - 诊断检查脚本
检查环境配置和依赖包是否正确安装
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(title):
    print("\n" + "="*50)
    print(f"🔍 {title}")
    print("="*50)

def check_python_version():
    print_header("Python 版本检查")
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("✅ Python 版本符合要求 (>= 3.8)")
        return True
    else:
        print("❌ Python 版本过低，需要 3.8 或更高版本")
        return False

def check_virtual_env():
    print_header("虚拟环境检查")
    
    # 检查虚拟环境文件夹
    venv_path = Path("venv_topic_analyzer")
    if venv_path.exists():
        print("✅ 找到虚拟环境文件夹")
        
        # 检查激活脚本
        activate_script = venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            print("✅ 虚拟环境激活脚本存在")
            return True
        else:
            print("❌ 虚拟环境激活脚本缺失")
            return False
    else:
        print("❌ 虚拟环境文件夹不存在")
        return False

def check_data_file():
    print_header("数据文件检查")
    
    data_file = Path("real_python_courses_analysis.csv")
    if data_file.exists():
        print("✅ 找到数据文件")
        
        # 检查文件大小
        size = data_file.stat().st_size
        print(f"📊 文件大小: {size:,} 字节")
        
        if size > 0:
            print("✅ 数据文件不为空")
            return True
        else:
            print("❌ 数据文件为空")
            return False
    else:
        print("❌ 数据文件不存在: real_python_courses_analysis.csv")
        return False

def check_dependencies():
    print_header("依赖包检查")
    
    required_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn'),
        ('nltk', 'nltk'),
        ('spacy', 'spacy'),
        ('plotly', 'plotly'),
        ('seaborn', 'seaborn'),
        ('matplotlib', 'matplotlib'),
        ('wordcloud', 'wordcloud')
    ]
    
    all_good = True
    
    for package_name, import_name in required_packages:
        try:
            exec(f"import {import_name}")
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name} - 未安装或导入失败: {e}")
            all_good = False
    
    return all_good

def check_spacy_model():
    print_header("SpaCy 英文模型检查")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ SpaCy 英文模型 (en_core_web_sm) 已安装")
        return True
    except OSError:
        print("❌ SpaCy 英文模型未安装")
        print("💡 请运行: python -m spacy download en_core_web_sm")
        return False

def check_nltk_data():
    print_header("NLTK 数据检查")
    
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        # 尝试加载停用词
        stop_words = stopwords.words('english')
        lemmatizer = WordNetLemmatizer()
        
        print("✅ NLTK 停用词和词形还原器可用")
        return True
    except Exception as e:
        print(f"❌ NLTK 数据缺失: {e}")
        print("💡 请运行应用时会自动下载，或手动运行:")
        print("   import nltk; nltk.download('stopwords'); nltk.download('wordnet')")
        return False

def run_quick_test():
    print_header("快速功能测试")
    
    try:
        # 测试主要导入
        import pandas as pd
        import streamlit as st
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import LatentDirichletAllocation
        
        # 测试简单功能
        sample_data = pd.DataFrame({'text': ['hello world', 'python programming']})
        vectorizer = TfidfVectorizer(max_features=10)
        matrix = vectorizer.fit_transform(sample_data['text'])
        
        print("✅ 核心功能测试通过")
        return True
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

def main():
    print("🎯 Real Python 博客内容主题分析仪表盘 - 环境诊断")
    print("🔍 正在检查系统环境和依赖配置...")
    
    checks = [
        ("Python 版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("数据文件", check_data_file),
        ("依赖包", check_dependencies),
        ("SpaCy 模型", check_spacy_model),
        ("NLTK 数据", check_nltk_data),
        ("功能测试", run_quick_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查时出错: {e}")
            results.append((name, False))
    
    # 总结报告
    print_header("检查结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:.<20} {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 所有检查通过！您可以正常运行应用。")
        print("💡 运行命令: streamlit run topic_dashboard_enhanced.py")
    else:
        print(f"\n⚠️  有 {total - passed} 项检查未通过，请根据上述提示进行修复。")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 