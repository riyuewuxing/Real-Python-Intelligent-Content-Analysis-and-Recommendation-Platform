# Real Python 博客内容主题分析仪表盘 📚

这是一个基于自然语言处理(NLP)和机器学习技术开发的智能主题分析系统，专门用于分析Real Python博客文章的内容主题。

## 项目概述 🎯

此项目中使用潜在狄利克雷分配(LDA)主题模型来自动识别和分析博客文章中的主要主题，并通过交互式Web仪表盘展示分析结果。

### 核心功能

- **📊 智能主题发现**: 使用LDA算法自动识别文章中的潜在主题
- **🎨 交互式可视化**: 通过饼图、柱状图、词云等多种方式展示主题分布
- **📈 时间趋势分析**: 分析主题随时间的变化趋势
- **🔍 深度主题分析**: 提供详细查看每个主题的文章和关键词功能
- **💾 结果导出**: 支持分析结果的CSV格式下载

## 技术栈 🛠️

- **前端框架**: 使用Streamlit
- **数据处理**: 采用Pandas, NumPy
- **机器学习**: 使用Scikit-learn (LDA主题模型)
- **自然语言处理**: 采用NLTK, SpaCy
- **数据可视化**: 使用Plotly, Matplotlib, WordCloud
- **主题可视化**: 采用pyLDAvis

## 安装说明 📦

### 1. 环境要求

- Python 3.8+
- 建议使用虚拟环境

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv_topic_analyzer

# 激活虚拟环境
# Windows:
venv_topic_analyzer\Scripts\activate
# macOS/Linux:
source venv_topic_analyzer/bin/activate
```

### 3. 安装依赖

```bash
# 安装Python包
pip install -r requirements.txt

# 下载NLTK数据包
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# 下载SpaCy英文模型
python -m spacy download en_core_web_sm
```

### 4. 数据准备

确保项目目录下有 `real_python_courses_analysis.csv` 文件，该文件应包含以下列：
- `Title`: 文章标题
- `Content`: 文章完整内容
- `Date`: 文章发布日期
- `URL`: 文章链接（可选）

## 使用方法 🚀

### 启动应用

```bash
streamlit run topic_dashboard_enhanced.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

### 操作指南

1. **设置参数**: 在左侧边栏调整提供的主题数量和特征词数量
2. **查看主题概览**: 观察自动发现的主题和关键词
3. **分析主题分布**: 通过图表了解各主题的文章分布情况
4. **探索时间趋势**: 查看分析的主题随时间的变化（如有日期数据）
5. **深入主题分析**: 选择具体主题查看提供的相关文章和词云
6. **下载结果**: 导出分析结果为CSV文件

## 功能详解 📋

### 主题概览
- 展示前3个主要主题的关键词
- 侧边栏显示所有主题的详细关键词列表

### 主题分布分析
- **饼图**: 各主题文章数量占比图
- **柱状图**: 各主题文章数量统计图
- **置信度分析**: 提供的各主题平均置信度评估

### 时间趋势分析
- 分析各主题文章发布的时间趋势
- 识别热门主题的时间变化模式

### 主题详细分析
- 提供选择特定主题查看相关文章列表的功能
- 生成主题关键词词云
- 显示文章置信度排序

### 统计信息
- 提供总文章数、主题数量、词汇表大小等关键指标
- 提供高频关键词排行榜

## 项目结构 📁

```
Real Python 博客内容主题分析仪表盘/
├── topic_dashboard_enhanced.py    # 主程序文件
├── requirements.txt                # 依赖包列表
├── README.md                       # 项目说明文档
└── real_python_courses_analysis.csv  # 数据文件
```

## 主要算法 🧠

### LDA主题模型
- **算法**: 使用的潜在狄利克雷分配(Latent Dirichlet Allocation)
- **特征提取**: 使用的TF-IDF向量化
- **参数优化**: 进行的文档-主题先验和主题-词汇先验调优

### 文本预处理流程
1. **清理**: 移除HTML标签和特殊字符
2. **标准化**: 转换为小写并规范化空格
3. **分词**: 使用SpaCy进行智能分词
4. **过滤**: 移除停用词和低质量词汇
5. **词形还原**: 将词汇还原为基本形式

## 性能优化 ⚡

- **缓存机制**: 使用Streamlit缓存减少重复计算
- **增量处理**: 支持大规模文本数据的分批处理
- **内存优化**: 使用高效的数据结构和算法实现

## 故障排除 🔧

### 常见问题

1. **SpaCy模型未找到**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **NLTK数据包缺失**
   ```python
   import nltk
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

3. **内存不足**
   - 建议减少`max_features`参数
   - 建议分批处理大型数据集

## 扩展功能 🚀

### 未来改进方向
- 计划支持多语言文本分析
- 计划集成更多主题模型算法(如BERTopic)
- 计划添加更多内容分析功能
- 计划支持实时数据流分析
- 计划部署到云端平台

## 贡献指南 🤝

欢迎提交Issue和Pull Request来改进此项目！

### 开发环境设置
1. Fork此项目仓库
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 许可证 📄

项目采用MIT许可证 - 详见LICENSE文件

## 联系方式 📧

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 确保您的数据文件包含足够的文本内容以获得有意义的主题分析结果。建议至少有50篇以上的文章且每篇文章内容超过100个词。 