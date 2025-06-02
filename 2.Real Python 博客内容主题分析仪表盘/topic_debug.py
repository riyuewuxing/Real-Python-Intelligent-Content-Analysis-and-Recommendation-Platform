import pandas as pd
import sys
import os
sys.path.append(os.getcwd())

from topic_dashboard_enhanced import load_nlp_resources, load_data, enhanced_preprocess_text, train_optimized_lda_model, get_enhanced_topic_words

def debug_topic_naming():
    print("=== 开始调试主题命名逻辑 ===")
    
    # 加载资源
    nlp, stop_words, lemmatizer = load_nlp_resources()
    df = load_data()
    
    print(f"数据集大小: {len(df)} 条记录")
    
    # 预处理文本 (使用前50条数据进行快速测试)
    cleaned_texts = []
    for i, content in enumerate(df['Content'][:50]):
        if pd.notna(content):
            cleaned_text = enhanced_preprocess_text(content, nlp, stop_words, lemmatizer)
            cleaned_texts.append(cleaned_text)
            if i < 3:  # 显示前3个预处理结果
                print(f"\n原文 {i+1}: {content[:100]}...")
                print(f"预处理后: {cleaned_text[:100]}...")
        else:
            cleaned_texts.append("")
    
    df_sample = df.head(50).copy()
    df_sample['enhanced_cleaned_content'] = cleaned_texts
    df_processed = df_sample[df_sample['enhanced_cleaned_content'].str.len() > 20]
    
    print(f"\n有效文本数量: {len(df_processed)}")
    
    # 训练模型
    print("\n=== 训练LDA模型 ===")
    lda_model, lda_output, vectorizer, tfidf_matrix, feature_names = train_optimized_lda_model(
        df_processed['enhanced_cleaned_content'], n_topics=7, max_features=500
    )
    
    # 获取主题词汇
    top_topic_words, topic_names = get_enhanced_topic_words(lda_model, feature_names, 15)
    
    print('\n=== 生成的主题关键词 ===')
    for topic_key, words in top_topic_words.items():
        print(f'{topic_key}: {words[:10]}')
    
    print('\n=== 生成的主题名称 ===')
    for topic_key, name in topic_names.items():
        print(f'{topic_key}: {name}')
    
    # 分析主题命名逻辑
    print('\n=== 分析主题命名逻辑 ===')
    theme_keywords = {
        'basics': ['loop', 'variable', 'function', 'class', 'object', 'string', 'list', 'dict'],
        'data_science': ['data', 'dataframe', 'pandas', 'numpy', 'polars', 'analysis', 'csv'],
        'web': ['web', 'selenium', 'browser', 'html', 'http', 'request', 'api', 'url'],
        'database': ['database', 'sql', 'mysql', 'query', 'table', 'record'],
        'tools': ['tool', 'package', 'library', 'install', 'pip', 'environment', 'project'],
        'advanced': ['async', 'thread', 'performance', 'optimization', 'algorithm', 'pattern'],
        'testing': ['test', 'debug', 'error', 'exception', 'unittest', 'pytest']
    }
    
    for topic_idx, (topic_key, words) in enumerate(top_topic_words.items()):
        print(f"\n主题 {topic_idx + 1} 分析:")
        print(f"  关键词: {words[:5]}")
        top_words_str = ' '.join(words[:5])
        
        matched_themes = []
        for theme, keywords in theme_keywords.items():
            matches = [kw for kw in keywords if kw in top_words_str]
            if matches:
                matched_themes.append((theme, matches))
        
        print(f"  匹配的主题类别: {matched_themes}")
        
        if not matched_themes:
            print(f"  ❌ 没有匹配到任何预定义主题类别!")
        else:
            print(f"  ✅ 匹配成功")

if __name__ == "__main__":
    debug_topic_naming() 