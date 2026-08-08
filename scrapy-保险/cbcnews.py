import requests
from bs4 import BeautifulSoup

url = "https://www.ctvnews.ca/"
def fetch_urls(url):

    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    response.encoding = 'utf-8'

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    #print("Soup",soup.prettify())

    # Find the element with the class "rich-text-block w-richtext"
    #rich_text_block = soup.find(class_="rich-text-block w-richtext")
    rich_text_block = soup.find("body")
    #print("Rich Text Block",rich_text_block)
    if rich_text_block:
        print("Rich Text Block Found",rich_text_block)
    
    else:
        print("No rich-text-block found.") 

    top_table_list = rich_text_block.find_all("article", class_="b-top-table-list-xl")

    for it in top_table_list:
        # Extract the title and link from each article
        title = it.find("p",class_="c-paragraph") 
        link = it.find("a")["href"]
        
        # Print the title and link
        print(f"Title: {title}")
        print(f"Link: {link}")
        print("-" * 40)  # Separator for readability


def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find("div", class_="c-article__content")
        
        if content:
            return content.get_text(strip=True)
        else:
            return "No content found."
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the content: {e}")
        return None