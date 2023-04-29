
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import dataset
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")
db = dataset.connect('sqlite:///zulutrade.db')

entryURL = 'https://www.zulutrade.com/trader/425490/trading?t=10000&m=1'
driver = webdriver.Chrome(options=options)


def dbPost(data: dict, table):
    db[f'{table}'].upsert(data, ['url'])


def index(page, url):
    soup = bs(page, 'lxml')
    name = soup.find(class_='righrName ms-3').text
    rank = soup.find(
        class_='regular me-3 mb-0').text.replace(' ZuluRank', '').replace('#', '')

    data = dict(url=url, name=name, rank=rank)
    dbPost(data, 'Indexs')


def scrape(page):
    soup = bs(page, 'lxml')

    table = soup.find('table', class_='table currencyTable')
    rows = table.find_all('tr')

    # Define an empty list to hold the dictionaries
    data = []

    # Loop through the rows and extract the column values as a dictionary
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            status = "Sell" if cols[0].find(
                class_='status sell').text else "Buy"

            record = {
                'Name': cols[0].find('p', {'class': 'medium'}).text,
                'Buy/Sell':   status,
                'Date Opened': cols[0].find(class_='mb-0 midgray f-11 medium').text,
                'Date Closed': cols[1].text.strip(),
                'STD LOTS': cols[2].text,
                'OPEN': cols[3].find('b').text,
                'CLOSE': cols[3].find_all('span')[0].text,
                'HIGH': cols[4].text,
                'LOW': cols[5].text,
                'ROLL': cols[6].text,
                'PROFIT': cols[7].find('b').text,
                'TOTAL': cols[8].find('b').text,
            }
            data.append(record)

    # Print the result
    print(data[0])


def pageination(url):
    driver.get(url)
    for i in range(1000):
        index(page=driver.page_source, url=driver.current_url)

        if i != 0:
            input = driver.find_element(
                By.CSS_SELECTOR, '#main-wrapper > section.blockElement.bg-white.pt-md-3.border-bottom.position-sticky.sndHeader > div > div > div:nth-child(1) > div > div.d-flex.align-items-center.stickyRight > div > a:nth-child(2) > i > svg')
        else:
            input = driver.find_element(
                By.CSS_SELECTOR, '#main-wrapper > section.blockElement.bg-white.pt-md-3.border-bottom.position-sticky.sndHeader > div > div > div:nth-child(1) > div > div.d-flex.align-items-center.stickyRight > div > a > i > svg')

        webdriver.ActionChains(driver).click(input).perform()

        time.sleep(1.5)

    driver.quit()


def screenshot(url, name):
    driver.get(url)
    time.sleep(1)
    driver.execute_script("document.body.style.zoom='55%'")
    driver.execute_script("window.scrollBy(0, 50);")
    time.sleep(1)
    input = driver.find_element(
        By.CSS_SELECTOR, '#main-wrapper > section.blockElement.overViewInvestors.space.pt-3 > div > div > div.col-12.col-xl-8 > div > div.row.mb-3.viewTabOne > div.col-12.col-md-7 > div > p')

    time.sleep(1)
    driver.save_screenshot(f'{name}.png')
    time.sleep(1)


# if __name__ == '__main__':
#     driver.get(entryURL)
#     time.sleep(2)
#     input = driver.find_element(
#         By.LINK_TEXT, 'Portfolio')

#     webdriver.ActionChains(driver).click(input).perform()
#     time.sleep(2)
#     scrape(driver.page_source)

if __name__ == '__main__':
    array = db.query('select url, name from Indexs;')
    for each in array:
        screenshot(name=each['name'], url=each['url'])
        print(each['name'])
    driver.quit()
