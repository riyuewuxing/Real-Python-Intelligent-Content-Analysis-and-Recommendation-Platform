from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

# 设置 EdgeDriver 路径
edge_driver_path = "D:\\edgedriver\\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)

# 设置 Edge 的 options（非 Chrome）
options = Options()
options.add_argument("--headless")  # 可选：无头模式
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# 启动 Edge 浏览器
driver = webdriver.Edge(service=service, options=options)

# 打开主页
driver.get("https://realpython.com/")
time.sleep(random.uniform(3, 5))

# 提取卡片元素
cards = driver.find_elements(By.CSS_SELECTOR, "div.card")
print(f"共找到 {len(cards)} 篇文章")

results = []

for idx, card in enumerate(cards, start=1):
    try:
        title_el = card.find_element(By.CSS_SELECTOR, "h2.card-title")
        title = title_el.text.strip()
        url = title_el.find_element(By.TAG_NAME, "a").get_attribute("href")

        date = card.find_element(By.CSS_SELECTOR, "p.card-text small span").text.strip()
        tags = card.find_elements(By.CSS_SELECTOR, "a.badge")
        keywords = [tag.text.strip() for tag in tags]

        print(f"第 {idx} 篇文章：{title}")
        print(f"链接：{url}")
        print(f"关键词：{keywords}")

        # 访问详情页
        driver.get(url)
        time.sleep(random.uniform(2, 4))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 正文内容提取
        article_div = soup.find("div", class_="article")
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
        else:
            content = ""

        results.append({
            "title": title,
            "url": url,
            "date": date,
            "keywords": ", ".join(keywords),
            "content": content
        })

        # 返回主页
        driver.get("https://realpython.com/")
        time.sleep(random.uniform(1.5, 3))

    except Exception as e:
        print(f"❌ 抓取第 {idx} 篇失败：{e}")
    print("-" * 60)

driver.quit()

# 保存为 CSV
df = pd.DataFrame(results)
df.to_csv("realpython_articles.csv", index=False, encoding="utf-8-sig")
print("✅ 抓取完成，已保存为 realpython_articles.csv")
