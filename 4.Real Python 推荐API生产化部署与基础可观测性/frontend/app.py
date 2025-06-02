import streamlit as st
import requests

# 设置API基础URL
API_BASE_URL = "http://127.0.0.1:8000"  # 本地开发地址
# API_BASE_URL = "http://api:8000"  # Docker Compose网络中的服务名称

# 应用标题
st.title("Real Python 文章推荐系统")
st.markdown("基于内容相似度的文章推荐引擎")

# 健康检查
def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            return response.json()["status"] == "ok"
        return False
    except:
        return False

# 获取推荐文章
def get_recommendations(article_id, top_n=5):
    try:
        response = requests.post(
            f"{API_BASE_URL}/recommend",
            json={"article_id": article_id, "top_n": top_n}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"API请求失败: {e}")
        return None

# 主应用逻辑
def main():
    # 显示API状态
    if check_api_health():
        st.success("✅ API服务运行正常")
    else:
        st.error("❌ API服务不可用")
        return

    # 文章ID输入
    article_id = st.number_input(
        "输入文章ID", 
        min_value=0, 
        value=0,
        help="输入要查找相似文章的文章ID"
    )
    
    # 推荐数量选择
    top_n = st.slider(
        "推荐数量", 
        min_value=1, 
        max_value=10, 
        value=5
    )
    
    # 获取推荐按钮
    if st.button("获取推荐文章"):
        if article_id <= 0:
            st.warning("请输入有效的文章ID")
            return
            
        with st.spinner("正在查找相似文章..."):
            result = get_recommendations(article_id, top_n)
            
        if result and result["recommendations"]:
            st.success(f"找到 {len(result['recommendations'])} 篇相关文章")
            for i, rec in enumerate(result["recommendations"]):
                with st.expander(f"#{i+1}: {rec['title']}"):
                    st.markdown(f"**文章ID**: {rec['article_id']}")
                    st.markdown(f"**标题**: {rec['title']}")
                    st.markdown(f"**链接**: [{rec['url']}]({rec['url']})")
        elif result:
            st.warning("未找到相关文章")
        else:
            st.error("获取推荐失败")

if __name__ == "__main__":
    main()
