import requests
from bs4 import BeautifulSoup

def fetch_rich_text_block(url):
    index = 1
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        response.encoding = 'utf-8'
        html = open("mvwealth.txt", "w",encoding="utf-8") 

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        #print("Soup",soup.prettify())
        for link in soup.find_all(class_="bwl-faq-container-3346259882"):
            #print(link)
            lb = link.find('label')
            a = "问题" +str(index) + ": " + lb.text.replace("问：", "")         
            html.write("<h3>"+"问题" +str(index) + ": <b>" + lb.text.replace("问：", "") + "</b></h3>\n")   
            rich_text_block = link.find_all('p')
            #html.write("<b>" + bl.text.replace("答：", "") + "</b>\n")
            html.write( "<b>回答：</b> "+      "\n")
            for bl in rich_text_block:
                #print(bl)
                if bl.text != "":
                    print(bl.text)     
                    cc = bl.text.replace("答：", "")               
                    html.write(cc + "\n")              
           
           
            html.write("\n")
            index += 1

        # Find the element with the class "rich-text-block w-richtext"
        rich_text_block = soup.find(class_="baf_content")

        if rich_text_block:
            #print("Rich Text Block Found",rich_text_block)
            return rich_text_block.get_text(strip=True)
        else:
            return "No rich-text-block found."

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the rich-text block: {e}")
        return None

# Example usage
post_url = "https://www.msunfinancial.com/post/buy-critical-illness-insurance-with-a-donate-for-good-mentality"
post_url = "https://mvwealth.ca/faq/"
rich_text = fetch_rich_text_block(post_url)

if rich_text:
    print("Rich Text Block Content:")
    #print(rich_text)
   
