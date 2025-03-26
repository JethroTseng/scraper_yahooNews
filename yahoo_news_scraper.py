import requests
from bs4 import BeautifulSoup
import time
import json
import sys

def scrape_yahoo_stock_news():
    url = "https://tw.stock.yahoo.com/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        print("Fetching main page...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save the HTML to debug later if needed
        with open('yahoo_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Main page fetched successfully. Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different selectors that might work with Yahoo Taiwan's structure
        # First, let's try to find articles by looking at common structures
        news_items = []
        
        # Try multiple selectors to find articles
        article_selectors = [
            'li[class*="js-stream-content"]',  # Original selector
            'div[class*="Pos(r)"] > div > ul > li',  # Another common pattern
            'div.Cf.Pos\\(r\\)',  # Another possibility
            'div[data-test-locator="mega"]',  # Another possible container
            'li[class^="js-stream-content"]',  # Another variant
            'div[class*="NewsStream"] li',  # News stream items
            'h3[class*="Fw(b)"]',  # Direct headline selector
            'div.Pos\\(r\\) article',  # Article elements
            'ul[class*="List"] > li'  # List items in a List
        ]
        
        # Try each selector until we find articles
        articles = []
        for selector in article_selectors:
            articles = soup.select(selector)
            if articles:
                print(f"Found {len(articles)} articles using selector: {selector}")
                break
        
        if not articles:
            # Fallback: find all h3 elements which are likely to be headlines
            articles = soup.find_all('h3')
            print(f"Fallback: Found {len(articles)} h3 elements that might be headlines")
        
        print(f"Total articles found: {len(articles)}")
        
        # Limit to 10 articles
        articles = articles[:10]
        
        for i, article in enumerate(articles):
            try:
                print(f"\nProcessing article {i+1}...")
                
                # Find headline - try different approaches
                headline = "No headline found"
                headline_elem = article.find('h3')
                if headline_elem:
                    headline = headline_elem.text.strip()
                else:
                    # If article itself is an h3
                    if article.name == 'h3':
                        headline = article.text.strip()
                    # Try to find any text that might be a headline
                    else:
                        all_text = article.get_text(strip=True)
                        if all_text:
                            headline = all_text[:100]  # Take first 100 chars as headline
                
                print(f"Headline: {headline}")
                
                # Find link - look for the closest a tag
                news_url = None
                if article.name == 'a':
                    news_url = article.get('href')
                else:
                    link_elem = article.find('a')
                    if link_elem:
                        news_url = link_elem.get('href')
                    else:
                        # Try to find a parent that's a link
                        parent_link = article.find_parent('a')
                        if parent_link:
                            news_url = parent_link.get('href')
                
                # Make sure URL is absolute
                if news_url and not news_url.startswith(('http://', 'https://')):
                    news_url = f"https://tw.stock.yahoo.com{news_url}" if news_url.startswith('/') else f"https://tw.stock.yahoo.com/{news_url}"
                
                print(f"URL: {news_url}")
                
                # Get summary
                summary = "No summary available"
                summary_elem = article.find('p')
                if summary_elem:
                    summary = summary_elem.text.strip()
                
                print(f"Summary: {summary}")
                
                # Get content only if we have a URL
                content = ""
                if news_url:
                    try:
                        print(f"Fetching article content from: {news_url}")
                        news_response = requests.get(news_url, headers=headers)
                        news_response.raise_for_status()
                        
                        # Save article HTML for debugging if needed
                        with open(f'article_{i+1}.html', 'w', encoding='utf-8') as f:
                            f.write(news_response.text)
                        
                        news_soup = BeautifulSoup(news_response.text, 'html.parser')
                        
                        # Try multiple selectors for content
                        content_selectors = [
                            'div[class*="caas-body"]',  # Original selector
                            'div[data-test-locator="articleBody"]',  # Another possible selector
                            'article[class*="caas-container"]',  # Article container
                            'div.caas-body',  # Direct class
                            'div.canvas-body'  # Another possible class
                        ]
                        
                        article_content = None
                        for selector in content_selectors:
                            content_elements = news_soup.select(selector)
                            if content_elements:
                                article_content = content_elements[0]
                                print(f"Found content using selector: {selector}")
                                break
                        
                        if article_content:
                            paragraphs = article_content.find_all('p')
                            if paragraphs:
                                content = "\n".join([p.text.strip() for p in paragraphs])
                            else:
                                # If no paragraphs, take all text from the content div
                                content = article_content.get_text(strip=True)
                        
                        print(f"Content length: {len(content)} characters")
                        
                        # Avoid hitting the server too frequently
                        time.sleep(1)
                    except Exception as e:
                        content = f"Error fetching content: {str(e)}"
                        print(f"Error fetching article content: {str(e)}")
                
                news_items.append({
                    "headline": headline,
                    "summary": summary,
                    "content": content,
                    "url": news_url
                })
                
                print(f"Scraped article {i+1}: {headline}")
                
            except Exception as e:
                print(f"Error processing article {i+1}: {str(e)}")
                # Continue with the next article even if this one fails
        
        # Save results to a file
        with open('yahoo_news_results.json', 'w', encoding='utf-8') as f:
            json.dump(news_items, f, ensure_ascii=False, indent=4)
            
        print(f"\nCompleted scraping. Total articles saved: {len(news_items)}")
        return news_items
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        # Print full traceback for better debugging
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("Starting Yahoo Taiwan Stock News scraper...")
    try:
        results = scrape_yahoo_stock_news()
        
        # Display results in console
        for i, item in enumerate(results, 1):
            print(f"\n--- Article {i} ---")
            print(f"Headline: {item['headline']}")
            print(f"Summary: {item['summary']}")
            print(f"URL: {item['url']}")
            print("Content (first 150 chars):", item['content'][:150] + "..." if len(item['content']) > 150 else item['content'])
            
        if not results:
            print("\nNo articles were scraped. Please check the error messages above.")
    except Exception as e:
        print(f"Unhandled error in main: {str(e)}")
        import traceback
        traceback.print_exc() 