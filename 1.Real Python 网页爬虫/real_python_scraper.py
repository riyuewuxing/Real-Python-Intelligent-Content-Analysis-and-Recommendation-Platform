import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

BASE_URL = "https://realpython.com"
BLOG_PAGE_URL = BASE_URL + "/blog/"
MAX_PAGES_TO_SCRAPE = 1 # 用于测试，稍后可以增加

# 更新CSV文件路径，保存到共享数据目录
CSV_FILENAME = "../shared_data/real_python_courses_analysis.csv"

REQUEST_DELAY = 2 # 秒，避免过于频繁请求

# 定义不希望抓取的URL模式列表
EXCLUDED_URL_PATTERNS = [
    "/learning-paths/",
    "/search",
    "/quizzes/",
    "/community/",
    "/office-hours/",
    "/podcasts/",
    "/ref/",
    "/mentor/",
    # 根据需要可以添加更多明确不抓取的路径
    # 例如： "/static/", "/careers/", "/about/"
]

def get_article_details(article_url):
    """
    抓取单个文章页面的标题、课程时长、关键词。
    根据新发现，课程文章使用 span[title="Course duration"] 显示时长，
    但不是每个文章都有课程时长。
    关键词使用精确的选择器逻辑抓取，基于JavaScript提取代码的逻辑。
    正文内容抓取部分已暂时注释。
    """
    try:
        print(f"Fetching article details from: {article_url}")
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # 获取文章标题
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        
        # 获取课程时长 - 使用新发现的选择器，但注意它可能不存在
        duration_tag = soup.select_one('span[title="Course duration"]')
        duration = duration_tag.get_text(strip=True) if duration_tag else "N/A"
        
        # 抓取关键词标签 - 使用更精确的选择器逻辑（基于您提供的JavaScript代码）
        keywords = []
        
        # 1. 尝试找到包含文章标题的父容器 div.col-md-11.col-lg-8.article.with-headerlinks
        article_content_div = soup.select_one('div.col-md-11.col-lg-8.article.with-headerlinks')
        
        if article_content_div:
            print("成功找到文章内容的父容器")
            
            # 2. 在这个文章内容容器内部，查找包含日期和标签的 div.mb-0
            info_div = article_content_div.select_one('div.mb-0')
            
            if info_div:
                print("成功找到文章信息容器 div.mb-0")
                
                # 3. 在这个 info_div 内部，查找包含标签的特定 span 元素
                tags_container_span = info_div.select_one('span.d-inline.d-md-block')
                
                if tags_container_span:
                    print("成功找到包含标签的 span 容器")
                    
                    # 4. 在这个 tags_container_span 内部，查找所有具有指定类的 <a> 标签
                    desired_tags = tags_container_span.select('a.badge.badge-light.text-muted[data-previewable]')
                    
                    if desired_tags:
                        keywords = [tag.get_text(strip=True) for tag in desired_tags]
                        print(f"使用精确选择器找到标签: {keywords}")
                    else:
                        print("警告：在预期的容器中没有找到 'badge' 标签")
                else:
                    print("警告：未能找到包含标签的 span.d-inline.d-md-block 元素")
            else:
                print("警告：未能找到文章信息容器 div.mb-0")
        else:
            print("警告：未能找到文章内容的父容器，尝试使用备用方法")
            # 如果精确选择器失败，使用原来的简单选择器作为备用
            keyword_tags = soup.select('a.badge')
            if keyword_tags:
                keywords = [tag.get_text(strip=True) for tag in keyword_tags]
                print(f"使用备用选择器找到标签: {keywords}")
        
        if keywords:
            print(f"最终提取到的关键词: {keywords}")
        else:
            print("未找到任何关键词标签")
        
        # 获取文章内容
        article_body_tag = soup.find("div", class_="article-body")
        if not article_body_tag:
            # 如果找不到 article-body，尝试找 article
            article_body_tag = soup.find("div", class_="article")
        
        content = article_body_tag.get_text(strip=True) if article_body_tag else "N/A"
        
        if not title_tag or not article_body_tag:
            print(f"Warning: Could not find title or body for {article_url}. Title found: {'Yes' if title_tag else 'No'}, Body found: {'Yes' if article_body_tag else 'No'}")

        if not title_tag:
            print(f"Warning: Could not find title for {article_url}.")

        return title, duration, keywords, content
    except requests.RequestException as e:
        print(f"Error fetching article {article_url}: {e}")
        return "N/A", "N/A", []
    except Exception as e:
        print(f"An unexpected error occurred while fetching details for {article_url}: {e}")
        return "N/A", "N/A", []

def get_blog_posts_from_page(page_url):
    """
    从博客列表页面抓取文章信息（URL, 标题, 日期）。
    使用 div.card-body 作为每个文章块的入口。
    使用 span.mr-2 选择器获取日期。
    """
    print(f"Scraping blog list page: {page_url}")
    posts_data = []
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        article_blocks = soup.select("div.card-body")
        print(f"Found {len(article_blocks)} potential article blocks on {page_url} using 'div.card-body'.")

        if not article_blocks:
            print(f"No article blocks found on {page_url} using selector 'div.card-body'. Check selector or page structure.")
            print(soup.prettify()[:5000]) 
            return posts_data

        for block in article_blocks:
            a_tag = block.select_one("a")
            article_url = ""
            title = "N/A"
            date = "N/A"  # 默认日期为N/A

            if a_tag:
                article_url = a_tag.get("href")
                if article_url and not article_url.startswith("http"):
                    article_url = BASE_URL + article_url
                
                title_tag = a_tag.select_one("h2.card-title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                elif block.select_one("h2.card-title"): 
                    title_tag = block.select_one("h2.card-title")
                    title = title_tag.get_text(strip=True)
                
                # 根据新发现，从列表页获取日期，使用span.mr-2选择器
                date_tag = block.select_one("span.mr-2")
                if date_tag:
                    date = date_tag.get_text(strip=True)
            else: 
                title_tag = block.select_one("h2.card-title")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                print(f"Warning: Found a card-body without a direct <a> tag for URL. Title: {title}")

            # 更新的过滤条件
            is_excluded = False
            if article_url: 
                for pattern in EXCLUDED_URL_PATTERNS:
                    if pattern in article_url:
                        is_excluded = True
                        break
            
            if article_url and title != "N/A" and "realpython.com/" in article_url and not is_excluded:
                posts_data.append({
                    "url": article_url,
                    "list_title": title,
                    "list_date": date  # 添加日期到数据中
                })
            else:
                if not article_url and a_tag:
                    article_url_for_log = a_tag.get("href", "N/A")
                    if not article_url_for_log.startswith("http") and article_url_for_log != "N/A":
                         article_url_for_log = BASE_URL + article_url_for_log
                else:
                    article_url_for_log = article_url if article_url else "N/A"
                print(f"Skipping non-article or incomplete block: Title='{title}', Date='{date}', URL='{article_url_for_log}'")

        print(f"Successfully extracted {len(posts_data)} articles from {page_url}.")
        return posts_data

    except requests.RequestException as e:
        print(f"Error fetching page {page_url}: {e}")
        return posts_data
    except Exception as e:
        print(f"An unexpected error occurred on page {page_url}: {e}")
        return posts_data

def main():
    all_articles_data = []
    
    for page_num in range(1, MAX_PAGES_TO_SCRAPE + 1):
        if page_num == 1:
            current_page_url = BLOG_PAGE_URL
        else:
            current_page_url = f"{BLOG_PAGE_URL}page/{page_num}/" # Real Python 分页结构
        
        print(f"\n--- Scraping Page {page_num} ---")
        
        # 从列表页获取初步信息
        posts_on_page = get_blog_posts_from_page(current_page_url)
        
        if not posts_on_page:
            print(f"No posts found on page {page_num}. Stopping further pagination.")
            break # 如果某一页没有文章了，就停止

        for post_info in posts_on_page:
            print(f"Processing article: {post_info.get('list_title', 'Unknown Title')}")
            time.sleep(random.uniform(REQUEST_DELAY / 2, REQUEST_DELAY * 1.5)) # 随机延迟
            
            # 获取文章详情页内容，现在返回四个值：标题、课程时长、关键词和正文内容
            detail_title, course_duration, keywords, article_content = get_article_details(post_info["url"])

            # 整合所有信息，只保留用户需要的字段
            article_data = {
                "Title": detail_title if detail_title != "N/A" else post_info["list_title"],
                "URL": post_info["url"],
                "Date": post_info["list_date"],
                "Course Duration": course_duration,  # 课程时长，可能为N/A
                "Keywords": ", ".join(keywords) if keywords else "N/A",  # 将关键词列表转换为逗号分隔的字符串
                "Content": article_content,  # 正文内容
            }
            all_articles_data.append(article_data)
            print(f"Processed and added: {detail_title if detail_title != 'N/A' else post_info.get('list_title', 'Unknown Title')}")
            if post_info["list_date"] != "N/A":
                print(f"Date: {post_info['list_date']}")
            if course_duration != "N/A":
                print(f"Course duration: {course_duration}")
            if keywords:
                print(f"Keywords: {', '.join(keywords)}")

        print(f"--- Finished Page {page_num} ---")
        if page_num < MAX_PAGES_TO_SCRAPE:
             print(f"Waiting for {REQUEST_DELAY} seconds before next page...")
             time.sleep(REQUEST_DELAY)


    if all_articles_data:
        df = pd.DataFrame(all_articles_data)
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(CSV_FILENAME)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"Created directory: {output_dir}")
            
            df.to_csv(CSV_FILENAME, index=False, encoding="utf-8-sig")
            print(f"\nSuccessfully scraped {len(all_articles_data)} articles.")
            print(f"Data saved to {CSV_FILENAME}")
            print(f"Absolute path: {os.path.abspath(CSV_FILENAME)}")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    else:
        print("\nNo articles were scraped. CSV file not created.")

if __name__ == "__main__":
    main()
