#!/usr/bin/env python3
"""
Real Python 博客内容主题分析仪表盘 - 演示脚本
本脚本展示主要功能并进行基本的数据分析演示
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_and_analyze_data():
    """加载数据并进行基本分析"""
    print("📊 Real Python 博客内容主题分析 - 数据概览")
    print("=" * 60)
    
    try:
        # 加载数据
        df = pd.read_csv('real_python_courses_analysis.csv')
        print(f"✅ 成功加载数据文件")
        print(f"📄 总文章数: {len(df)}")
        
        # 检查数据结构
        print(f"\n📋 数据列信息:")
        for col in df.columns:
            non_null_count = df[col].count()
            print(f"  • {col}: {non_null_count} 条有效记录")
        
        # 内容长度分析
        if 'Content' in df.columns:
            df['content_length'] = df['Content'].str.len()
            print(f"\n📝 文章内容统计:")
            print(f"  • 平均长度: {df['content_length'].mean():.0f} 字符")
            print(f"  • 最短文章: {df['content_length'].min()} 字符")
            print(f"  • 最长文章: {df['content_length'].max()} 字符")
            
            # 过滤有效文章
            valid_articles = df[df['content_length'] > 100]
            print(f"  • 有效文章数 (>100字符): {len(valid_articles)}")
        
        # 日期分析
        if 'Date' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Date'])
                df['Year'] = df['Date'].dt.year
                print(f"\n📅 时间分布:")
                year_counts = df['Year'].value_counts().sort_index()
                for year, count in year_counts.items():
                    print(f"  • {year}: {count} 篇文章")
            except:
                print(f"⚠️  日期格式解析失败")
        
        # 关键词分析
        if 'Keywords' in df.columns:
            keywords_data = df['Keywords'].dropna()
            if len(keywords_data) > 0:
                print(f"\n🏷️  关键词信息:")
                print(f"  • 有关键词的文章: {len(keywords_data)} 篇")
                
                # 提取所有关键词
                all_keywords = []
                for keywords in keywords_data:
                    if isinstance(keywords, str):
                        all_keywords.extend([k.strip() for k in keywords.split(',')])
                
                from collections import Counter
                keyword_freq = Counter(all_keywords)
                top_keywords = keyword_freq.most_common(10)
                
                print(f"  • 热门关键词 (Top 10):")
                for keyword, count in top_keywords:
                    print(f"    - {keyword}: {count} 次")
        
        return df
        
    except FileNotFoundError:
        print("❌ 未找到 'real_python_courses_analysis.csv' 文件")
        print("请确保文件在当前目录下")
        return None
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return None

def demonstrate_text_processing():
    """演示文本预处理过程"""
    print(f"\n{'='*60}")
    print("🔧 文本预处理演示")
    print("=" * 60)
    
    # 示例文本
    sample_text = """
    <h1>Python Lists: A Complete Guide</h1>
    <p>Python lists are one of the most versatile data structures in Python. 
    In this tutorial, you'll learn how to create, modify, and use Python lists effectively.</p>
    <code>my_list = [1, 2, 3, 'python', 'tutorial']</code>
    <p>Lists in Python are mutable, which means you can change their content after creation.</p>
    """
    
    print("📝 原始文本示例:")
    print(f"'{sample_text[:100]}...'")
    
    # 模拟预处理步骤
    import re
    
    # 1. 移除HTML标签
    cleaned = re.sub(r'<.*?>', '', sample_text)
    print(f"\n🧹 移除HTML标签后:")
    print(f"'{cleaned[:100]}...'")
    
    # 2. 转换为小写并移除特殊字符
    cleaned = cleaned.lower()
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)
    print(f"\n🔤 标准化后:")
    print(f"'{cleaned[:100]}...'")
    
    # 3. 分词
    words = cleaned.split()
    print(f"\n✂️  分词结果 (前10个):")
    print(f"{words[:10]}")
    
    # 4. 移除停用词 (简化版)
    stop_words = {'the', 'in', 'and', 'or', 'you', 'to', 'of', 'a', 'are', 'is', 'this', 'that', 'will'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    print(f"\n🚫 移除停用词后:")
    print(f"{filtered_words}")

def demonstrate_topic_modeling_concept():
    """演示主题建模概念"""
    print(f"\n{'='*60}")
    print("🎯 主题建模概念演示")
    print("=" * 60)
    
    # 模拟主题示例
    topics = {
        "主题 1 - 数据结构": ["list", "dict", "set", "tuple", "array", "dataframe", "structure", "collection"],
        "主题 2 - Web开发": ["django", "flask", "web", "http", "api", "request", "response", "server"],
        "主题 3 - 数据科学": ["pandas", "numpy", "matplotlib", "analysis", "data", "visualization", "plot", "chart"],
        "主题 4 - 机器学习": ["model", "algorithm", "training", "prediction", "sklearn", "feature", "classification", "regression"],
        "主题 5 - 基础语法": ["function", "class", "variable", "loop", "condition", "syntax", "basic", "fundamental"]
    }
    
    print("🎲 模拟发现的主题:")
    for topic_name, keywords in topics.items():
        print(f"\n📌 {topic_name}:")
        print(f"   关键词: {', '.join(keywords[:5])}...")
    
    print(f"\n💡 LDA主题模型的工作原理:")
    print("   1. 将文档表示为主题的混合")
    print("   2. 将主题表示为词汇的分布")
    print("   3. 通过迭代优化找到最佳主题分配")
    print("   4. 每篇文章被分配到最可能的主题")

def show_visualization_examples():
    """展示可视化示例概念"""
    print(f"\n{'='*60}")
    print("📊 数据可视化功能预览")
    print("=" * 60)
    
    # 模拟数据
    topic_distribution = {
        "主题 1": 25,
        "主题 2": 18,
        "主题 3": 22,
        "主题 4": 15,
        "主题 5": 12,
        "主题 6": 8
    }
    
    print("🥧 主题分布图 (模拟数据):")
    total = sum(topic_distribution.values())
    for topic, count in topic_distribution.items():
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"   {topic:8} |{bar:20}| {count:2d} 篇 ({percentage:.1f}%)")
    
    print(f"\n📈 时间趋势分析:")
    print("   • 分析各主题随时间的流行度变化")
    print("   • 识别热门话题的生命周期")
    print("   • 预测未来内容方向")
    
    print(f"\n☁️  词云功能:")
    print("   • 为每个主题生成关键词词云")
    print("   • 直观展示重要词汇")
    print("   • 支持自定义样式和颜色")

def show_next_steps():
    """显示下一步操作指南"""
    print(f"\n{'='*60}")
    print("🚀 如何启动完整的分析系统")
    print("=" * 60)
    
    print("📋 操作步骤:")
    print("   1. 运行设置脚本安装依赖:")
    print("      python setup.py")
    print("")
    print("   2. 启动Web仪表盘:")
    print("      streamlit run topic_dashboard.py")
    print("")
    print("   3. 在浏览器中打开:")
    print("      http://localhost:8501")
    print("")
    print("⚙️  可配置参数:")
    print("   • 主题数量: 3-15个主题")
    print("   • 特征词数量: 500-2000个词汇")
    print("   • 过滤条件: 文章长度、日期范围等")
    print("")
    print("📊 核心功能:")
    print("   • 智能主题发现与分析")
    print("   • 交互式数据可视化")
    print("   • 时间趋势分析")
    print("   • 详细主题报告")
    print("   • 结果导出功能")

def main():
    """主演示函数"""
    print("🎭 Real Python 博客内容主题分析仪表盘 - 功能演示")
    print("=" * 80)
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 数据加载和分析
    df = load_and_analyze_data()
    
    # 2. 文本预处理演示
    demonstrate_text_processing()
    
    # 3. 主题建模概念
    demonstrate_topic_modeling_concept()
    
    # 4. 可视化示例
    show_visualization_examples()
    
    # 5. 下一步指南
    show_next_steps()
    
    print(f"\n{'='*80}")
    print("✨ 演示完成！查看 README.md 了解更多详细信息")
    print("=" * 80)

if __name__ == "__main__":
    main() 