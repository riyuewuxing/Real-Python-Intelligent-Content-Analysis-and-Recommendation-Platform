import pandas as pd
import streamlit as st
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# 设置页面配置
st.set_page_config(
    page_title="Real Python 博客内容主题分析",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载SpaCy模型和NLTK资源
@st.cache_resource
def load_nlp_resources():
    try:
        # 下载NLTK数据
        import nltk
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        # 加载SpaCy模型
        nlp = spacy.load("en_core_web_sm")
        stop_words = set(stopwords.words('english'))
        # 添加一些领域相关的停用词
        stop_words.update(['python', 'code', 'example', 'tutorial', 'learn', 'use', 'using', 'used', 'get', 'like', 'one', 'also', 'make', 'way', 'work', 'time', 'need', 'want', 'see', 'know', 'take', 'real', 'realpython'])
        lemmatizer = WordNetLemmatizer()
        return nlp, stop_words, lemmatizer
    except Exception as e:
        st.error(f"NLP资源加载失败: {e}")
        st.info("请确保已安装spacy和英文模型: python -m spacy download en_core_web_sm")
        st.stop()

# 加载数据
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('real_python_courses_analysis.csv')
        
        # 检查必要的列
        required_columns = ['Title', 'Content', 'Date']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV文件缺少必要的列: {required_columns}")
            st.stop()
        
        # 清理数据
        df = df.dropna(subset=['Content', 'Date'])
        df = df[df['Content'].str.len() > 100]  # 过滤太短的内容
        
        # 处理日期
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.to_period('M')
        except:
            st.warning("日期格式可能有问题，部分时间序列功能可能不可用")
            df['Year'] = 2024  # 默认年份
            df['Month'] = '2024-01'
        
        return df
    except FileNotFoundError:
        st.error("未找到 'real_python_courses_analysis.csv' 文件，请确保文件在当前目录下")
        st.stop()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        st.stop()

# 文本预处理
@st.cache_data
def preprocess_text(text, _nlp, _stop_words, _lemmatizer):
    """预处理文本内容"""
    # 转换为小写
    text = text.lower()
    
    # 移除HTML标签和特殊字符
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 使用SpaCy进行分词和词形还原
    doc = _nlp(text)
    tokens = []
    
    for token in doc:
        if (token.is_alpha and 
            not token.is_stop and 
            token.text not in _stop_words and 
            len(token.text) > 2 and
            len(token.text) < 20):  # 避免很长的词
            tokens.append(token.lemma_)
    
    return " ".join(tokens)

# 训练LDA模型
@st.cache_data
def train_lda_model(texts, n_topics=7, max_features=1000):
    """训练LDA主题模型"""
    # TF-IDF向量化
    vectorizer = TfidfVectorizer(
        max_df=0.95, 
        min_df=2, 
        max_features=max_features,
        stop_words='english'
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # 训练LDA模型
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method='online',
        random_state=42,
        max_iter=10,
        doc_topic_prior=0.1,
        topic_word_prior=0.01
    )
    
    lda_output = lda_model.fit_transform(tfidf_matrix)
    
    return lda_model, lda_output, vectorizer, tfidf_matrix, feature_names

# 获取主题关键词
def get_top_words(model, feature_names, n_top_words=10):
    """获取每个主题的关键词"""
    topic_words = {}
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_features_ind]
        topic_words[f"主题 {topic_idx + 1}"] = top_words
    return topic_words

# 创建饼图
def create_pie_chart(data, title):
    """使用Matplotlib创建饼图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("husl", len(data))
    
    wedges, texts, autotexts = ax.pie(
        data.values, 
        labels=data.index, 
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 美化文本
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    return fig

# 创建柱状图
def create_bar_chart(data, title, xlabel, ylabel):
    """使用Seaborn创建柱状图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sns.barplot(data=data.reset_index(), x=data.index, y=data.values, ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # 旋转x轴标签
    plt.xticks(rotation=45, ha='right')
    
    # 添加数值标签
    for i, v in enumerate(data.values):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

# 创建时间趋势图
def create_trend_chart(data, title):
    """创建时间趋势图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 为每个主题创建不同的线条
    topics = data['主题名称'].unique()
    colors = sns.color_palette("husl", len(topics))
    
    for i, topic in enumerate(topics):
        topic_data = data[data['主题名称'] == topic]
        ax.plot(topic_data['Year'], topic_data['文章数量'], 
               marker='o', label=topic, color=colors[i], linewidth=2, markersize=6)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('文章数量', fontsize=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# 创建热力图
def create_heatmap(data, title):
    """创建相关性热力图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(data, annot=True, cmap='viridis', center=0, 
                square=True, linewidths=0.5, ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

# 主函数
def main():
    st.title("📚 Real Python 博客内容主题分析仪表盘")
    st.markdown("**使用 Seaborn + Matplotlib 可视化方案**")
    st.markdown("---")
    
    # 加载资源
    with st.spinner("正在加载NLP资源..."):
        nlp, stop_words, lemmatizer = load_nlp_resources()
    
    # 加载数据
    with st.spinner("正在加载数据..."):
        df = load_data()
    
    st.success(f"✅ 成功加载 {len(df)} 篇文章")
    
    # 侧边栏配置
    st.sidebar.header("📊 分析设置")
    
    # 主题数量选择
    n_topics = st.sidebar.slider(
        "选择主题数量 (LDA)", 
        min_value=3, 
        max_value=15, 
        value=7,
        help="选择要发现的主题数量"
    )
    
    # 最大特征词数量
    max_features = st.sidebar.slider(
        "最大特征词数量", 
        min_value=500, 
        max_value=2000, 
        value=1000,
        help="用于主题建模的最大词汇数量"
    )
    
    # 预处理文本
    if 'cleaned_content' not in df.columns:
        with st.spinner("正在预处理文本..."):
            progress_bar = st.progress(0)
            cleaned_texts = []
            
            for i, content in enumerate(df['Content']):
                cleaned_text = preprocess_text(content, nlp, stop_words, lemmatizer)
                cleaned_texts.append(cleaned_text)
                progress_bar.progress((i + 1) / len(df))
            
            df['cleaned_content'] = cleaned_texts
            progress_bar.empty()
    
    # 过滤掉清理后内容太短的文章
    df = df[df['cleaned_content'].str.len() > 20]
    
    if len(df) == 0:
        st.error("预处理后没有有效的文本内容")
        st.stop()
    
    # 训练LDA模型
    with st.spinner("正在训练主题模型..."):
        lda_model, lda_output, vectorizer, tfidf_matrix, feature_names = train_lda_model(
            df['cleaned_content'], n_topics, max_features
        )
    
    # 为每篇文章分配主导主题
    df['dominant_topic'] = lda_output.argmax(axis=1)
    df['topic_probability'] = lda_output.max(axis=1)
    
    # 获取主题关键词
    top_topic_words = get_top_words(lda_model, feature_names, 10)
    
    st.success("✅ 主题模型训练完成！")
    
    # === 主题概览 ===
    st.header("🎯 主题概览")
    
    # 显示主题关键词
    cols = st.columns(3)
    topics_list = list(top_topic_words.keys())
    
    for i in range(min(3, len(topics_list))):
        with cols[i]:
            topic_name = topics_list[i]
            words = top_topic_words[topic_name]
            st.subheader(f"**{topic_name}**")
            st.write("**关键词:**")
            for j, word in enumerate(words[:5]):
                st.write(f"{j+1}. {word}")
    
    # 侧边栏显示所有主题
    st.sidebar.subheader("🔍 所有主题关键词")
    selected_topic_display = st.sidebar.selectbox(
        "选择查看具体主题",
        options=list(top_topic_words.keys())
    )
    
    with st.sidebar.expander(f"📝 {selected_topic_display} 详细信息"):
        words = top_topic_words[selected_topic_display]
        for i, word in enumerate(words):
            st.write(f"{i+1}. **{word}**")
    
    st.markdown("---")
    
    # === 主题分布分析 ===
    st.header("📊 主题分布分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 主题分布饼图
        topic_counts = df['dominant_topic'].value_counts()
        topic_counts.index = [f"主题 {i + 1}" for i in topic_counts.index]
        
        st.subheader("各主题文章数量分布")
        fig_pie = create_pie_chart(topic_counts, "各主题文章数量分布")
        st.pyplot(fig_pie)
    
    with col2:
        # 主题分布柱状图
        st.subheader("各主题文章数量统计")
        fig_bar = create_bar_chart(topic_counts, "各主题文章数量统计", "主题", "文章数量")
        st.pyplot(fig_bar)
    
    # 主题置信度分析
    st.subheader("🎯 主题置信度分析")
    
    # 计算平均置信度
    avg_confidence = df.groupby('dominant_topic')['topic_probability'].mean()
    avg_confidence.index = [f"主题 {i + 1}" for i in avg_confidence.index]
    
    fig_conf = create_bar_chart(avg_confidence, "各主题的平均置信度", "主题", "平均置信度")
    st.pyplot(fig_conf)
    
    st.markdown("---")
    
    # === 时间趋势分析 ===
    if 'Year' in df.columns and df['Year'].nunique() > 1:
        st.header("📈 主题时间趋势分析")
        
        # 按年份和主题分组
        yearly_trends = df.groupby(['Year', 'dominant_topic']).size().reset_index(name='文章数量')
        yearly_trends['主题名称'] = yearly_trends['dominant_topic'].apply(lambda x: f"主题 {x + 1}")
        
        fig_trend = create_trend_chart(yearly_trends, "各主题文章发布趋势（按年）")
        st.pyplot(fig_trend)
        
        st.markdown("---")
    
    # === 主题详细分析 ===
    st.header("🔍 主题详细分析")
    
    # 选择主题进行详细查看
    selected_topic_id = st.selectbox(
        "选择主题进行详细分析",
        options=sorted(df['dominant_topic'].unique()),
        format_func=lambda x: f"主题 {x + 1}: {', '.join(top_topic_words[f'主题 {x + 1}'][:3])}"
    )
    
    # 过滤该主题的文章
    topic_articles = df[df['dominant_topic'] == selected_topic_id].sort_values(
        by='topic_probability', ascending=False
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🎯 主题 {selected_topic_id + 1} 的文章列表 ({len(topic_articles)} 篇)")
        
        # 显示文章列表
        for idx, row in topic_articles.head(10).iterrows():
            with st.expander(f"📄 {row['Title']} (置信度: {row['topic_probability']:.2f})"):
                st.write(f"**发布日期:** {row['Date']}")
                if 'URL' in row:
                    st.write(f"**链接:** {row['URL']}")
                
                # 显示文章摘要（前200个字符）
                content_preview = row['Content'][:200] + "..." if len(row['Content']) > 200 else row['Content']
                st.write(f"**内容预览:** {content_preview}")
    
    with col2:
        # 该主题的词云
        st.subheader(f"☁️ 主题 {selected_topic_id + 1} 词云")
        
        # 获取该主题的关键词和权重
        topic_words = top_topic_words[f"主题 {selected_topic_id + 1}"]
        word_freq = {word: len(topic_words) - i for i, word in enumerate(topic_words)}
        
        try:
            wordcloud = WordCloud(
                width=400, 
                height=300, 
                background_color='white',
                colormap='viridis',
                max_words=50
            ).generate_from_frequencies(word_freq)
            
            fig_wc, ax_wc = plt.subplots(figsize=(8, 6))
            ax_wc.imshow(wordcloud, interpolation='bilinear')
            ax_wc.axis("off")
            ax_wc.set_title(f"主题 {selected_topic_id + 1} 词云", fontsize=14, fontweight='bold')
            st.pyplot(fig_wc)
        except Exception as e:
            st.error(f"词云生成失败: {e}")
    
    st.markdown("---")
    
    # === 统计信息 ===
    st.header("📋 数据统计信息")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总文章数", len(df))
    
    with col2:
        st.metric("主题数量", n_topics)
    
    with col3:
        st.metric("词汇表大小", len(feature_names))
    
    with col4:
        avg_confidence = df['topic_probability'].mean()
        st.metric("平均主题置信度", f"{avg_confidence:.3f}")
    
    # 关键词统计
    st.subheader("📝 高频关键词统计")
    
    # 获取所有清理后的文本
    all_words = []
    for text in df['cleaned_content']:
        all_words.extend(text.split())
    
    # 统计词频
    word_freq = Counter(all_words)
    top_words = word_freq.most_common(20)
    
    word_df = pd.DataFrame(top_words, columns=['词汇', '频次'])
    
    fig_words = create_bar_chart(word_df.set_index('词汇')['频次'], 
                                "高频词汇排行榜 (Top 20)", "词汇", "频次")
    st.pyplot(fig_words)
    
    st.markdown("---")
    
    # === 下载结果 ===
    st.header("💾 下载分析结果")
    
    # 准备下载数据
    download_df = df[['Title', 'Date', 'dominant_topic', 'topic_probability']].copy()
    download_df['主题名称'] = download_df['dominant_topic'].apply(lambda x: f"主题 {x + 1}")
    download_df['主题关键词'] = download_df['dominant_topic'].apply(
        lambda x: ', '.join(top_topic_words[f"主题 {x + 1}"][:5])
    )
    
    csv = download_df.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 下载主题分析结果 (CSV)",
        data=csv,
        file_name="real_python_topic_analysis_results.csv",
        mime="text/csv"
    )
    
    # 显示结果预览
    with st.expander("📊 查看分析结果预览"):
        st.dataframe(download_df, use_container_width=True)

if __name__ == "__main__":
    main() 