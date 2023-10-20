from lxml import etree
import time
from selenium_initialization import initialize_selenium

def main():
    driver = initialize_selenium()
    driver.get('https://garde-enfant-fonpeps-audiens.org/')
    time.sleep(2)

    page_source = driver.page_source

    # save page source into a file html
    with open('page_source.html', 'w') as f:
        f.write(page_source)
    
    # load file and read it with lxml
    with open('page_source.html', 'r') as f:
        page_source = f.read()
    tree = etree.HTML(page_source)

    # get the meta description
    meta_description = tree.xpath('//h1[@class="banner-title"]')
    print(meta_description[0].text)


    driver.quit()

if __name__ == '__main__':
    main()