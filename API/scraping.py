import requests
from bs4 import BeautifulSoup

def get_soup(url):

    # ページの内容を取得
    response = requests.get(url)
    content = response.content

    # BeautifulSoupを使って解析
    soup = BeautifulSoup(content, 'lxml')

    return soup

def get_top10(soup, selector):

    # 暴騰・急騰銘柄TOP 10
    elements = soup.select(selector)

    res_array = []

    trs = elements[0].find_all('tr')
    for tr in trs:
        try:  
            no = tr.contents[1].text
            company_name = tr.contents[5].text
            rate_of_up = tr.contents[9].text
            # print("No：" + str(no) + " 会社名：" + str(company_name) + " 率：" + str(rate_of_up))
            res_array.append([no, company_name, rate_of_up])
        except:
            pass

    return res_array

def update_array(arr, company_code, company_name, fund):
    """
    配列内で会社情報を管理します。

    Parameters:
    arr (list): 銘柄コード、会社名、カウントが格納されるリスト
    company_code (str): 追加する会社の銘柄コード
    company_name (str): 追加する会社の会社名
    """
    found = False
    for item in arr:
        if item[0] == company_code and item[1] == company_name:
            item[2] += 1  # カウントを増やす
            item[3].append(fund)
            found = True
            break

    if not found:
        arr.append([company_code, company_name, 1, [fund]])  # 新しい要素として追加

def get_html(url, selector, element):
    """
    指定したURLから要素を取得します。

    Parameters:
    url (str): 取得対象のURL
    selector (str): 取得対象のセレクタ
    element (str): 取得対象のエレメント

    Returns:
    list: 取得対象のエレメントのリスト
    """
    response = requests.get(url)
    content = response.content

    soup = BeautifulSoup(content, 'lxml')

    res_selector = soup.select(selector)

    if len(res_selector) == 0:
        return None

    elements = res_selector[0].find_all(element)

    return elements

# # スクレイピング対象のURL
# url = "https://nikkeiyosoku.com/stock/twitter/"
# selector = "body > div:nth-child(5) > div > div.col-sm-12.col-md-9 > div.section > div:nth-child(5) > table > tbody"

# res_array = get_top10(url, selector)
# print(res_array)