
import requests
from bs4 import BeautifulSoup

index = 0

def get_html(url):
    global index
# Send a GET request to the specified URL
    #url = "https://canwagroup.com/%e8%87%aa%e9%9b%87%e4%ba%ba%e5%a3%ab%e7%9a%84%e7%a8%8e%e5%8a%a1%e7%94%b3%e6%8a%a5/"
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    response.encoding = 'utf-8'

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text.split('-')[0].strip().replace("/","_").replace(" ","_").replace(":","_").replace("?","_").replace("！","_").replace("！","_") \
    .replace("？","_").replace("：","_").replace(" ","_").replace('\"',"_").replace(")","_").replace("[","_").replace("]","_").replace("{","_").replace("}","_").replace("<","_").replace(">","_")
    #print("Soup",soup.prettify())

    # Find the element with the class "rich-text-block w-richtext"
    #rich_text_block = soup.find(class_="rich-text-block w-richtext")
    rich_text_block = soup.find("div", class_="elementor-element elementor-element-7b77d8ef post-content elementor-widget elementor-widget-theme-post-content")
    #print("Rich Text Block",rich_text_block)
    if rich_text_block:
        #print("Rich Text Block Found",rich_text_block)
        rich_text = rich_text_block.find("div", class_="elementor-widget-container")
        #print("Rich Text",rich_text.text)
        with open(title+ ".txt", "w", encoding="utf-8") as file:
            file.write(rich_text.text)
            index += 1
    
    else:
        print("No rich-text-block found.") 

def get_urls(url):
    # Send a GET request to the specified URL
    #url = "https://canwagroup.com/category/%e8%b4%a2%e7%a8%8e%e5%ad%a6%e9%99%a2/%e5%8a%a0%e6%8b%bf%e5%a4%a7%e4%b8%aa%e4%ba%ba%e7%a8%8e%e5%8a%a1/"
    #https://canwagroup.com/category/%e8%b4%a2%e7%a8%8e%e5%ad%a6%e9%99%a2/%e5%8a%a0%e6%8b%bf%e5%a4%a7%e4%b8%aa%e4%ba%ba%e7%a8%8e%e5%8a%a1/page/2/

    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    response.encoding = 'utf-8'

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    #print("Soup",soup.prettify())

    # Find the element with the class "rich-text-block w-richtext"
    #rich_text_block = soup.find(class_="rich-text-block w-richtext")
    links = soup.find_all('a',class_="elementor-post__read-more", href=True)
    for r in links:
        #print("Link",r['href'])
        get_html(r['href'])
    #print("Rich Text Block",rich_text_block)
    #https://canwagroup.com/category/%E8%B4%A2%E7%A8%8E%E5%AD%A6%E9%99%A2/%E5%8A%A0%E6%8B%BF%E5%A4%A7%E4%B8%AA%E4%BA%BA%E7%A8%8E%E5%8A%A1/page/18/

if __name__ == "__main__":
    #url = "https://canwagroup.com/%e8%87%aa%e9%9b%87%e4%ba%ba%e5%a3%ab%e7%9a%84%e7%a8%8e%e5%8a%a1%e7%94%b3%e6%8a%a5/"
    #get_html(url)
    url = "https://canwagroup.com/category/%e8%b4%a2%e7%a8%8e%e5%ad%a6%e9%99%a2/%e5%8a%a0%e6%8b%bf%e5%a4%a7%e4%b8%aa%e4%ba%ba%e7%a8%8e%e5%8a%a1/page/12"
    get_urls(url)
    for i in range(17, 19):
        print(i)
        url = f"https://canwagroup.com/category/%e8%b4%a2%e7%a8%8e%e5%ad%a6%e9%99%a2/%e5%8a%a0%e6%8b%bf%e5%a4%a7%e4%b8%aa%e4%ba%ba%e7%a8%8e%e5%8a%a1/page/{i}/"
        #get_urls(url)