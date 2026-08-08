import requests
from bs4 import BeautifulSoup

def fetch_rich_text_block(url):
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        response.encoding = 'utf-8'

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element with the class "rich-text-block w-richtext"
        rich_text_block = soup.find(class_="rich-text-block w-richtext")

        if rich_text_block:
            print("Rich Text Block Found",rich_text_block)
            return rich_text_block.get_text(strip=True)
        else:
            return "No rich-text-block found."

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the rich-text block: {e}")
        return None



def fetch_all_urls(url):
    try:
        # Send a GET request to the blog URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags with href attributes
        links = soup.find_all('a', href=True)

        urls = [link['href'] for link in links]

        return urls

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URLs: {e}")
        return []

# Example usage
blog_url = "https://www.msunfinancial.com/blog"
urls = fetch_all_urls(blog_url)

print("All URLs:")

with open("output.txt", "w", encoding="utf-8") as file:
       

    for url in urls:
        print(url)
        if('post' in url):
            rich_text = fetch_rich_text_block( "https://www.msunfinancial.com" +url)

            if rich_text:
                print("Rich Text Block Content:")
                print(rich_text)
                file.write("https://www.msunfinancial.com" +url)
                file.write("\n")
                file.write(rich_text)
                file.write("\n\n")


#https://hc-llp.ca/zh/category/blogs-simplified-chinese/family-morality-prose/
#https://hc-llp.ca/zh/category/blogs-simplified-chinese/tax-business-corp/