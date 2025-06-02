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
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')

# ===============================
# 页面配置与样式设置
# ===============================

st.set_page_config(
    page_title="Real Python 博客内容主题分析仪表盘",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 尝试设置支持中文的字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except Exception as e:
    st.warning(f"设置中文字体失败: {e}。图表中的中文可能无法正确显示。请确保系统安装了中文字体如SimHei或Microsoft YaHei。")

# 设置Seaborn样式
sns.set_palette("husl")

# 自定义CSS样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .topic-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #1f77b4;
        transition: all 0.3s ease;
    }
    
    .topic-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .section-header {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    
    .confidence-bar {
        background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        height: 20px;
        border-radius: 10px;
        margin: 0.2rem 0;
    }
    
    .stSelectbox > label {
        font-weight: 600;
        color: #2c3e50;
    }
    
    .topic-keywords {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# 核心功能函数
# ===============================

@st.cache_resource
def load_nlp_resources():
    """加载NLP资源并优化停用词"""
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        nlp = spacy.load("en_core_web_sm")
        stop_words = set(stopwords.words('english'))
        
        # 增强的领域特定停用词
        domain_stopwords = {
            'python', 'code', 'example', 'tutorial', 'learn', 'use', 'using', 
            'used', 'get', 'like', 'one', 'also', 'make', 'way', 'work', 
            'time', 'need', 'want', 'see', 'know', 'take', 'real', 
            'realpython', 'article', 'post', 'blog', 'course', 'lesson',
            'chapter', 'section', 'page', 'website', 'link', 'click',
            'read', 'write', 'show', 'display', 'create', 'build'
        }
        stop_words.update(domain_stopwords)
        
        lemmatizer = WordNetLemmatizer()
        return nlp, stop_words, lemmatizer
    except Exception as e:
        st.error(f"NLP资源加载失败: {e}")
        st.info("请确保已安装spacy和英文模型: python -m spacy download en_core_web_sm")
        st.stop()

@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        df = pd.read_csv('../shared_data/real_python_courses_analysis.csv')
        
        required_columns = ['Title', 'Content', 'Date']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV文件缺少必要的列: {required_columns}")
            st.stop()
        
        # 数据清理和增强
        df = df.dropna(subset=['Content', 'Date'])
        df = df[df['Content'].str.len() > 100]
        
        # 更稳健的日期处理
        parsed_dates = pd.to_datetime(df['Date'], errors='coerce')
        successful_parses = parsed_dates.notna()
        num_failed = len(df) - successful_parses.sum()

        if num_failed > 0:
            st.warning(f"⚠️ 日期格式处理：{num_failed}条记录的日期无法被自动解析，这些记录将使用估算日期或可能在时间趋势分析中被忽略。")
        
        df['Date'] = parsed_dates
        # 对于无法解析的日期，填充一个固定日期，或标记它们以便后续处理
        # 这里我们选择不直接填充，让后续的dt访问器自然处理NaT
        
        # 只有在Date列成功转换为datetime后才尝试访问dt属性
        if pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.to_period('M')
            df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
        else:
            # 如果转换失败，创建包含NaT/NaN的列以避免后续错误
            st.error("日期列未能成功转换为datetime格式，时间相关分析可能不准确。")
            df['Year'] = np.nan
            df['Month'] = pd.NaT
            df['YearMonth'] = pd.NaT 
        
        # 添加内容长度和词数统计
        df['content_length'] = df['Content'].str.len()
        df['word_count'] = df['Content'].str.split().str.len()
        
        return df
    except FileNotFoundError:
        st.error("未找到 '../shared_data/real_python_courses_analysis.csv' 文件")
        st.stop()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        st.stop()

@st.cache_data
def enhanced_preprocess_text(text, _nlp, _stop_words, _lemmatizer):
    """增强的文本预处理"""
    # 基础清理
    text = text.lower()
    
    # 移除HTML标签、代码块和特殊字符
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'```[\s\S]*?```', ' CODE_BLOCK ', text)
    text = re.sub(r'`[^`]+`', ' CODE_INLINE ', text)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 使用SpaCy进行高级处理
    doc = _nlp(text)
    tokens = []
    
    for token in doc:
        if (token.is_alpha and 
            not token.is_stop and 
            token.text not in _stop_words and 
            len(token.text) > 2 and
            len(token.text) < 20 and
            token.pos_ in ['NOUN', 'ADJ', 'VERB']):  # 只保留关键词性
            tokens.append(token.lemma_)
    
    return " ".join(tokens)

@st.cache_data
def train_optimized_lda_model(texts, n_topics=7, max_features=1000, min_df=2, max_df=0.95):
    """训练优化的LDA模型"""
    # 使用TF-IDF向量化，包含2-gram
    vectorizer = TfidfVectorizer(
        max_df=max_df, 
        min_df=min_df, 
        max_features=max_features,
        stop_words='english',
        ngram_range=(1, 2)  # 包含1-gram和2-gram
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # 训练LDA模型
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method='online',
        random_state=42,
        max_iter=20,
        doc_topic_prior=0.1,
        topic_word_prior=0.01,
        learning_decay=0.7
    )
    
    lda_output = lda_model.fit_transform(tfidf_matrix)
    
    return lda_model, lda_output, vectorizer, tfidf_matrix, feature_names

def get_enhanced_topic_words(model, feature_names, n_top_words=15):
    """获取增强的主题关键词并生成主题名称"""
    topic_words = {}
    topic_names = {}
    
    # 扩展的主题名称映射规则，增加更多细分主题
    theme_keywords = {
        'basics_syntax': ['syntax', 'operator', 'expression', 'statement', 'indentation', 'comment', 'variable', 'type', 'value', 'literal'],
        'basics_structures': ['loop', 'for', 'while', 'if', 'else', 'condition', 'list', 'dict', 'tuple', 'set', 'comprehension', 'slice'],
        'basics_functions': ['function', 'def', 'return', 'parameter', 'argument', 'lambda', 'scope', 'closure', 'decorator', 'generator'],
        'oop': ['class', 'object', 'method', 'attribute', 'property', 'inheritance', 'polymorphism', 'encapsulation', 'instance', 'static'],
        'data_science': ['data', 'dataframe', 'pandas', 'numpy', 'polars', 'analysis', 'csv', 'datum', 'column', 'group', 'aggregate', 'polar', 'miss'],
        'web_frontend': ['html', 'css', 'javascript', 'frontend', 'dom', 'ajax', 'react', 'vue', 'angular', 'template', 'ui', 'design'],
        'web_backend': ['django', 'flask', 'fastapi', 'backend', 'api', 'rest', 'graphql', 'endpoint', 'authentication', 'authorization'],
        'web_automation': ['selenium', 'browser', 'scraping', 'crawler', 'automation', 'bot', 'headless', 'puppeteer'],
        'database': ['database', 'sql', 'mysql', 'postgresql', 'sqlite', 'query', 'table', 'record', 'orm', 'migration'],
        'devops': ['docker', 'kubernetes', 'ci', 'cd', 'pipeline', 'deployment', 'server', 'cloud', 'aws', 'azure'],
        'tools': ['tool', 'package', 'library', 'install', 'pip', 'environment', 'virtualenv', 'poetry', 'dependency', 'management'],
        'concurrency': ['async', 'await', 'thread', 'process', 'multiprocessing', 'concurrency', 'parallel', 'locking', 'queue'],
        'testing': ['test', 'unittest', 'pytest', 'mock', 'coverage', 'tdd', 'integration', 'fixture', 'assert'],
        'file_io': ['file', 'directory', 'path', 'read', 'write', 'open', 'os', 'shutil', 'json', 'csv', 'serialization'],
        'algorithms': ['algorithm', 'structure', 'sort', 'search', 'tree', 'graph', 'recursion', 'dynamic', 'complexity', 'bigo'],
        'multimedia': ['video', 'audio', 'image', 'media', 'ffmpeg', 'opencv', 'processing', 'stream', 'recognition']
    }
    
    # 主题类别到友好名称的映射
    theme_map = {
        'basics_syntax': 'Python语法基础',
        'basics_structures': '数据结构与控制流',
        'basics_functions': '函数与作用域',
        'oop': '面向对象编程',
        'data_science': '数据分析与科学计算',
        'web_frontend': 'Web前端技术',
        'web_backend': 'Web后端开发',
        'web_automation': 'Web自动化与爬虫',
        'database': '数据库操作',
        'devops': 'DevOps与部署',
        'tools': '开发工具与环境',
        'concurrency': '并发与并行编程',
        'testing': '测试与质量保障',
        'file_io': '文件与IO操作',
        'algorithms': '算法与数据结构',
        'multimedia': '多媒体处理'
    }
    
    # 用于检测重复主题名称的字典
    used_names = set()
    
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_features_ind]
        topic_words[f"主题 {topic_idx + 1}"] = top_words
        
        # 自动生成主题名称 - 改进匹配逻辑
        topic_name = f"主题 {topic_idx + 1}"
        top_words_str = ' '.join(top_words[:10]).lower()  # 扩展到前10个词
        
        # 计算每个主题类别的匹配分数
        theme_scores = {}
        for theme, keywords in theme_keywords.items():
            score = sum(1 for keyword in keywords if keyword in top_words_str)
            if score > 0:
                theme_scores[theme] = score
        
        # 选择得分最高的主题类别
        if theme_scores:
            # 按分数排序，取前3个候选主题
            sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # 尝试找到未使用的主题名称
            selected_name = None
            for theme, score in sorted_themes:
                candidate_name = theme_map.get(theme, '综合主题')
                if candidate_name not in used_names:
                    selected_name = candidate_name
                    break
            
            # 如果所有候选名称都已使用，则使用最匹配的名称加上关键词
            if selected_name is None:
                best_theme = sorted_themes[0][0]
                base_name = theme_map.get(best_theme, '综合主题')
                # 使用前两个关键词创建唯一名称
                keyword_suffix = "_".join(top_words[:2])
                selected_name = f"{base_name}: {keyword_suffix}"
            else:
                used_names.add(selected_name)
            
            topic_name = f"主题 {topic_idx + 1}: {selected_name}"
        else:
            # 如果没有匹配，根据关键词特征生成描述性名称
            if any(word in top_words_str for word in ['python', 'code', 'program']):
                base_name = "Python编程"
            elif any(word in top_words_str for word in ['learn', 'tutorial', 'guide']):
                base_name = "学习教程"
            elif any(word in top_words_str for word in ['web', 'http', 'site']):
                base_name = "Web开发"
            elif any(word in top_words_str for word in ['data', 'analysis', 'science']):
                base_name = "数据分析"
            else:
                base_name = "综合技术"
            
            # 确保名称唯一
            if base_name in used_names:
                # 使用前两个关键词创建唯一名称
                keyword_suffix = "_".join(top_words[:2])
                base_name = f"{base_name}: {keyword_suffix}"
            else:
                used_names.add(base_name)
            
            topic_name = f"主题 {topic_idx + 1}: {base_name}"
        
        topic_names[f"主题 {topic_idx + 1}"] = topic_name
        
    return topic_words, topic_names

def create_enhanced_pie_chart(data, title):
    fig = go.Figure(data=[go.Pie(
        labels=data.index,
        values=data.values,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(
            colors=px.colors.qualitative.Set3,
            line=dict(color='#FFFFFF', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>文章数: %{value}<br>占比: %{percent}<extra></extra>'
    )])
    fig.update_layout(
        title={'text': title, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'family': 'Arial, sans-serif'}},
        showlegend=True, height=500, margin=dict(t=100, b=50, l=50, r=50),
        font=dict(family="SimHei, Microsoft YaHei, Arial Unicode MS, sans-serif") # 为Plotly图表设置字体
    )
    return fig

def create_enhanced_bar_chart(data, title, xlabel, ylabel):
    fig = go.Figure(data=[go.Bar(
        x=data.index,
        y=data.values,
        marker_color=px.colors.qualitative.Set3[:len(data)],
        text=data.values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' + ylabel + ': %{y}<extra></extra>'
    )])
    fig.update_layout(
        title={'text': title, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'family': 'Arial, sans-serif'}},
        xaxis_title=xlabel, yaxis_title=ylabel, height=500, margin=dict(t=100, b=50, l=50, r=50),
        xaxis={'tickangle': -45},
        font=dict(family="SimHei, Microsoft YaHei, Arial Unicode MS, sans-serif") # 为Plotly图表设置字体
    )
    return fig

def create_confidence_visualization(confidence_data):
    fig = go.Figure(data=[go.Bar(
        x=confidence_data.index,
        y=confidence_data.values,
        marker=dict(color=confidence_data.values, colorscale='Viridis', showscale=True, colorbar=dict(title="置信度")),
        text=[f"{x:.3f}" for x in confidence_data.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>平均置信度: %{y:.3f}<extra></extra>'
    )])
    fig.update_layout(
        title={'text': "各主题平均置信度分析", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'family': 'Arial, sans-serif'}},
        xaxis_title="主题", yaxis_title="平均置信度", height=500, margin=dict(t=100, b=50, l=50, r=50),
        xaxis={'tickangle': -45},
        font=dict(family="SimHei, Microsoft YaHei, Arial Unicode MS, sans-serif") # 为Plotly图表设置字体
    )
    return fig

# ===============================
# 主应用程序
# ===============================

def main():
    # 主标题
    st.markdown('<h1 class="main-title">📚 Real Python 博客内容主题分析仪表盘</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 1.2rem;">基于高级NLP技术的智能主题发现与内容分析平台</p>', 
                unsafe_allow_html=True)
    
    # 加载资源
    with st.spinner("🔄 正在加载NLP资源和数据..."):
        nlp, stop_words, lemmatizer = load_nlp_resources()
        df = load_data()
    
    # 安全地显示日期范围 - 根据load_data的修改调整
    date_range_str = ""
    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']) and df['Date'].notna().any():
        try:
            min_date = df['Date'].dropna().min()
            max_date = df['Date'].dropna().max()
            if pd.notna(min_date) and pd.notna(max_date):
                 date_range_str = f"，数据时间范围：{min_date.strftime('%Y-%m')} 至 {max_date.strftime('%Y-%m')}"
        except Exception as e:
            st.warning(f"生成日期范围字符串时出错: {e}") # 更具体的错误
            date_range_str = "，日期范围信息部分可用"
    elif 'Date' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['Date']):
        date_range_str = "，日期信息不可用或格式不正确"

    st.success(f"✅ 成功加载 {len(df)} 篇文章{date_range_str}")
    
    # ===============================
    # 侧边栏 - 分析设置控制面板
    # ===============================
    
    st.sidebar.markdown('<h2 style="color: #2c3e50;">🎛️ 分析设置控制面板</h2>', unsafe_allow_html=True)
    
    # 主题数量选择
    st.sidebar.markdown("### 📊 主题建模参数")
    n_topics = st.sidebar.slider(
        "主题数量 (推荐: 7个主题)", 
        min_value=3, 
        max_value=15, 
        value=7,
        help="选择LDA模型要发现的主题数量。更多主题提供更细致的分类，但可能降低可解释性。"
    )
    
    max_features = st.sidebar.slider(
        "最大特征词数量", 
        min_value=500, 
        max_value=2000, 
        value=1000,
        help="控制用于主题建模的词汇表大小。更大的词汇表可能提供更丰富的主题描述。"
    )
    
    # 高级参数设置
    with st.sidebar.expander("🔧 高级参数设置"):
        min_df = st.slider("最小文档频率", 1, 10, 2, 
                          help="词语至少在多少篇文档中出现才被保留")
        max_df = st.slider("最大文档频率", 0.8, 0.99, 0.95, 
                          help="在超过此比例文档中出现的词语将被过滤")
    
    # 显示推荐值
    st.sidebar.info(f"💡 当前设置建议：\n- 推荐主题数：7个\n- 推荐特征词数：1000个\n- 基于数据集大小优化")
    
    # ===============================
    # 文本预处理
    # ===============================
    
    if 'enhanced_cleaned_content' not in df.columns or df['enhanced_cleaned_content'].isnull().all():
        with st.spinner("🔄 正在进行高级文本预处理..."):
            progress_bar = st.progress(0)
            cleaned_texts = []
            
            for i, content in enumerate(df['Content']):
                if pd.notna(content):
                    cleaned_text = enhanced_preprocess_text(content, nlp, stop_words, lemmatizer)
                    cleaned_texts.append(cleaned_text)
                else:
                    cleaned_texts.append("") # 处理空内容
                progress_bar.progress((i + 1) / len(df))
            
            df['enhanced_cleaned_content'] = cleaned_texts
            progress_bar.empty()
    
    # 过滤处理后的文本
    df_processed = df[df['enhanced_cleaned_content'].str.len() > 20].copy()
    
    if len(df_processed) == 0:
        st.error("⚠️ 预处理后没有有效的文本内容可供分析。请检查数据源或调整预处理参数。")
        st.stop()
    
    # ===============================
    # 训练LDA模型
    # ===============================
    
    with st.spinner("🧠 正在训练优化的LDA主题模型..."):
        lda_model, lda_output, vectorizer, tfidf_matrix, feature_names = train_optimized_lda_model(
            df_processed['enhanced_cleaned_content'], n_topics, max_features, min_df, max_df
        )
    
    # 分配主题
    df_processed.loc[:, 'dominant_topic'] = lda_output.argmax(axis=1)
    df_processed.loc[:, 'topic_probability'] = lda_output.max(axis=1)
    
    # 获取主题词汇和名称
    top_topic_words, topic_names = get_enhanced_topic_words(lda_model, feature_names, 15)
    
    st.success("✅ 高级主题模型训练完成！")
    
    # ===============================
    # 主内容区域
    # ===============================
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 主题概览", "📊 分布分析", "🔍 详细分析", "📈 趋势分析", "📋 数据统计"
    ])
    
    # ===============================
    # Tab 1: 主题概览
    # ===============================
    
    with tab1:
        st.markdown('<h2 class="section-header">🎯 智能主题发现概览</h2>', unsafe_allow_html=True)
        
        # 动态主题卡片布局
        cols_per_row = 3
        for i in range(0, len(top_topic_words), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                topic_idx = i + j
                if topic_idx < len(top_topic_words):
                    topic_key = list(top_topic_words.keys())[topic_idx]
                    topic_name = topic_names[topic_key]
                    words = top_topic_words[topic_key]
                    article_count = len(df_processed[df_processed['dominant_topic'] == topic_idx])
                    
                    with col:
                        # 主题卡片
                        st.markdown(f"""
                        <div class="topic-card">
                            <h3 style="color: #2c3e50; margin: 0 0 1rem 0;">{topic_name}</h3>
                            <div class="topic-keywords">
                                <strong>核心关键词：</strong><br>
                                {', '.join(words[:6])}
                            </div>
                            <p><strong>📄 文章数量：</strong> {article_count} 篇</p>
                            <p><strong>📝 简要描述：</strong> 涵盖 {words[0]} 相关的 {words[1]} 技术和应用</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # ===============================
    # Tab 2: 分布分析
    # ===============================
    
    with tab2:
        st.markdown('<h2 class="section-header">📊 主题分布深度分析</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 增强饼图
            topic_counts = df_processed['dominant_topic'].value_counts()
            topic_counts.index = [topic_names[f"主题 {i + 1}"] for i in topic_counts.index]
            
            st.subheader("📈 各主题文章分布")
            fig_pie = create_enhanced_pie_chart(topic_counts, "主题文章分布")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 增强柱状图
            st.subheader("📊 主题文章数量统计")
            fig_bar = create_enhanced_bar_chart(topic_counts, "主题文章数量", "主题", "文章数量")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # 置信度分析
        st.subheader("🎯 主题置信度深度分析")
        avg_confidence = df_processed.groupby('dominant_topic')['topic_probability'].mean()
        avg_confidence.index = [topic_names[f"主题 {i + 1}"] for i in avg_confidence.index]
        
        fig_conf = create_confidence_visualization(avg_confidence)
        st.plotly_chart(fig_conf, use_container_width=True)
        
        # 置信度统计
        st.info(f"""
        📊 **置信度统计信息:**
        - 平均置信度: {df_processed['topic_probability'].mean():.3f}
        - 最高置信度: {df_processed['topic_probability'].max():.3f}
        - 低置信度文章 (<0.3): {len(df_processed[df_processed['topic_probability'] < 0.3])} 篇
        - 高置信度文章 (>0.7): {len(df_processed[df_processed['topic_probability'] > 0.7])} 篇
        """)
    
    # ===============================
    # Tab 3: 详细分析
    # ===============================
    
    with tab3:
        st.markdown('<h2 class="section-header">🔍 主题详细深度分析</h2>', unsafe_allow_html=True)
        
        # 主题选择
        selected_topic_name = st.selectbox(
            "🎯 选择要分析的主题",
            options=list(topic_names.values()),
            help="选择一个主题进行深入分析"
        )
        
        # 获取选中主题的索引
        selected_topic_id = None
        for key, name in topic_names.items():
            if name == selected_topic_name:
                selected_topic_id = int(key.split()[-1]) - 1
                break
        
        if selected_topic_id is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"📄 {selected_topic_name} - 相关文章列表")
                
                # 过滤和排序文章
                topic_articles = df_processed[df_processed['dominant_topic'] == selected_topic_id].sort_values(
                    by='topic_probability', ascending=False
                ).head(20)
                
                # 显示文章表格
                for idx, row in topic_articles.iterrows():
                    confidence = row['topic_probability']
                    confidence_color = 'green' if confidence > 0.7 else 'orange' if confidence > 0.4 else 'red'
                    
                    with st.expander(f"📄 {row['Title']} (置信度: {confidence:.3f})"):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            # 安全地显示日期
                            try:
                                if pd.api.types.is_datetime64_any_dtype(df['Date']):
                                    date_str = row['Date'].strftime('%Y-%m-%d')
                                else:
                                    date_str = str(row['Date'])
                            except:
                                date_str = "日期未知"
                            
                            st.write(f"**📅 发布日期:** {date_str}")
                            if 'URL' in row and pd.notna(row['URL']):
                                st.write(f"**🔗 原文链接:** [{row['URL']}]({row['URL']})")
                            
                            # 内容预览
                            content_preview = row['Content'][:300] + "..." if len(row['Content']) > 300 else row['Content']
                            st.write(f"**📝 内容预览:** {content_preview}")
                        
                        with col_b:
                            # 置信度条形图
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <strong>置信度</strong><br>
                                <div style="background: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 10px 0;">
                                    <div style="background: {confidence_color}; height: 20px; width: {confidence*100}%; border-radius: 10px;"></div>
                                </div>
                                <span style="color: {confidence_color}; font-weight: bold;">{confidence:.1%}</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            with col2:
                st.subheader(f"☁️ {selected_topic_name} - 词云")
                
                # 生成词云
                topic_words = top_topic_words[f"主题 {selected_topic_id + 1}"]
                word_freq = {word: len(topic_words) - i for i, word in enumerate(topic_words)}
                
                try:
                    wordcloud = WordCloud(
                        width=400, 
                        height=300, 
                        background_color='white',
                        colormap='viridis',
                        max_words=30,
                        relative_scaling=0.5,
                        min_font_size=12
                    ).generate_from_frequencies(word_freq)
                    
                    fig_wc, ax_wc = plt.subplots(figsize=(8, 6))
                    ax_wc.imshow(wordcloud, interpolation='bilinear')
                    ax_wc.axis("off")
                    ax_wc.set_title(f"{selected_topic_name} 关键词云", 
                                   fontsize=14, fontweight='bold', pad=20)
                    st.pyplot(fig_wc)
                except Exception as e:
                    st.error(f"词云生成失败: {e}")
                
                # 关键词列表
                st.subheader("🔑 核心关键词排序")
                for i, word in enumerate(topic_words[:10]):
                    st.write(f"{i+1}. **{word}**")
    
    # ===============================
    # Tab 4: 趋势分析
    # ===============================
    
    with tab4:
        st.markdown('<h2 class="section-header">📈 主题时间趋势分析</h2>', unsafe_allow_html=True)
        
        if 'Year' in df_processed.columns and df_processed['Year'].nunique() > 1:
            # 年度趋势
            yearly_trends = df_processed.groupby(['Year', 'dominant_topic']).size().reset_index(name='文章数量')
            yearly_trends['主题名称'] = yearly_trends['dominant_topic'].apply(
                lambda x: topic_names[f"主题 {x + 1}"]
            )
            
            fig_trend = px.line(
                yearly_trends,
                x='Year',
                y='文章数量',
                color='主题名称',
                title='各主题文章发布年度趋势',
                markers=True,
                height=500
            )
            fig_trend.update_layout(
                title={'x': 0.5, 'xanchor': 'center'},
                xaxis_title="年份",
                yaxis_title="文章发布数量"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 月度热力图
            if 'YearMonth' in df_processed.columns:
                st.subheader("📅 主题发布月度热力图")
                monthly_data = df_processed.groupby(['YearMonth', 'dominant_topic']).size().unstack(fill_value=0)
                monthly_data.columns = [topic_names[f"主题 {i + 1}"] for i in monthly_data.columns]
                
                fig_heatmap = px.imshow(
                    monthly_data.T,
                    title="主题月度发布热力图",
                    color_continuous_scale="Viridis",
                    height=400
                )
                fig_heatmap.update_layout(title={'x': 0.5, 'xanchor': 'center'})
                st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("📅 数据中缺少足够的时间信息来进行趋势分析")
    
    # ===============================
    # Tab 5: 数据统计
    # ===============================
    
    with tab5:
        st.markdown('<h2 class="section-header">📋 综合数据统计信息</h2>', unsafe_allow_html=True)
        
        # 关键指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📄 总文章数</h3>
                <h2>{len(df_processed)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 主题数量</h3>
                <h2>{n_topics}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📚 词汇表大小</h3>
                <h2>{len(feature_names)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_confidence = df_processed['topic_probability'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎲 平均置信度</h3>
                <h2>{avg_confidence:.3f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # 详细统计
        st.subheader("📊 详细数据统计")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 📈 文章长度分析")
            length_stats = df_processed['content_length'].describe()
            st.write(length_stats)
            
            # 文章长度分布
            fig_length = px.histogram(
                df_processed, x='content_length', 
                title="文章字符长度分布",
                nbins=30
            )
            st.plotly_chart(fig_length, use_container_width=True)
        
        with col2:
            st.write("### 🔤 词数统计分析")
            word_stats = df_processed['word_count'].describe()
            st.write(word_stats)
            
            # 词数分布
            fig_words = px.histogram(
                df_processed, x='word_count', 
                title="文章词数分布",
                nbins=30
            )
            st.plotly_chart(fig_words, use_container_width=True)
        
        # 高频词汇分析
        st.subheader("🔤 高频关键词统计")
        
        all_words = []
        for text in df_processed['enhanced_cleaned_content']:
            all_words.extend(text.split())
        
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(20)
        
        word_df = pd.DataFrame(top_words, columns=['词汇', '频次'])
        
        fig_freq = px.bar(
            word_df, x='词汇', y='频次',
            title="高频词汇排行榜 (Top 20)",
            color='频次',
            color_continuous_scale='viridis'
        )
        fig_freq.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_freq, use_container_width=True)
        
        # 下载区域
        st.subheader("💾 数据导出")
        
        # 准备下载数据
        download_df = df_processed[[
            'Title', 'Date', 'dominant_topic', 'topic_probability', 'content_length', 'word_count'
        ]].copy()
        download_df['主题名称'] = download_df['dominant_topic'].apply(
            lambda x: topic_names[f"主题 {x + 1}"]
        )
        download_df['主题关键词'] = download_df['dominant_topic'].apply(
            lambda x: ', '.join(top_topic_words[f"主题 {x + 1}"][:5])
        )
        
        # 确保Date列是字符串格式以便CSV导出
        if 'Date' in download_df.columns and pd.api.types.is_datetime64_any_dtype(download_df['Date']):
            download_df['Date'] = download_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('日期解析失败')
        elif 'Date' in download_df.columns:
            download_df['Date'] = download_df['Date'].astype(str).fillna('日期解析失败')

        csv = download_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 下载完整分析结果 (CSV)",
            data=csv,
            file_name=f"real_python_topic_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # 显示结果预览
        with st.expander("📊 查看分析结果预览"):
            st.dataframe(download_df, use_container_width=True)

if __name__ == "__main__":
    main()
