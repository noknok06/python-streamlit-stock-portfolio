import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_tags import st_tags

import investment as inv

# ページ全体の幅を広げる
st.set_page_config(layout="wide")

# Google Financeから株式情報を取得する関数
def get_soup(stock_code):
    url = f'https://www.google.com/finance/quote/{stock_code}:TYO'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

# HTMLから特定の要素を取得する関数
def get_element(soup, class_txt):
    elem = soup.find_all(class_=class_txt)
    return elem

# 時価総額を数値に変換する関数
def convert_market_cap(market_cap_str):
    if market_cap_str.endswith('B'):
        return float(market_cap_str[:-1]) * 1e9  # 億（10^9）
    elif market_cap_str.endswith('T'):
        return float(market_cap_str[:-1]) * 1e12  # 兆（10^12）
    else:
        return float(market_cap_str)

# 株式情報を取得する関数
def get_stock_info(stock_code):
    soup = get_soup(stock_code)
    
    stock_value_elements = get_element(soup, "YMlKec fxKbKc")
    stock_value = stock_value_elements[0].text if stock_value_elements else "株価要素が見つかりません"

    stock_name = get_element(soup, "zzDege")
    stock_name = stock_name[0].text if stock_name else "株価要素が見つかりません"

    additional_info_elements = get_element(soup, "P6K39c")
    if additional_info_elements and len(additional_info_elements) > 6:
        market_cap_str = additional_info_elements[3].text
        market_cap = convert_market_cap(market_cap_str.replace(" JPY", ""))
        dividend_yield = additional_info_elements[6].text
    else:
        market_cap = "N/A"
        dividend_yield = "N/A"
    
    return {
        '銘柄名': stock_name,
        '株価': stock_value.replace("¥", "").replace(",", ""),
        '時価総額': market_cap,
        '配当利回': dividend_yield.replace("%", "").replace("-", "0")
    }

# 株式コード一覧をキャッシュして取得する関数
@st.cache_data
def get_stocks():
    stock_codes = pd.read_csv('Data/stock_data.csv')
    return stock_codes['コード'].tolist()

# 保存された設定をCSVファイルに書き込む関数
def save_settings(name, purchase_value, keywords):
    data = {
        '名称': [name],
        '購入金額': [purchase_value],
        'キーワード': [",".join(keywords)]
    }
    df = pd.DataFrame(data)
    df.to_csv(f'Data/{name}.csv', index=False)

# CSVファイルから設定を読み込む関数
def load_settings(name):
    try:
        df = pd.read_csv(f'Data/{name}.csv')
        pv = df.iloc[0]['購入金額']
        kws = df.iloc[0]['キーワード'].split(',') if isinstance(df.iloc[0]['キーワード'], str) else []
        return pv, kws
    except Exception as e:
        st.error(f"設定の読み込み中にエラーが発生しました: {e}")
        return None, None

@st.experimental_dialog("Cast your vote")
def save_favorite():
    save_name = st.text_input("保存する名称を入力してください")
    if st.button("保存"):
        save_settings(save_name, st.session_state.purchase_value, st.session_state.keywords)
        st.success(f'"{save_name}" として設定を保存しました。')
        st.rerun()

@st.experimental_dialog("Cast your vote")
def call_favorite():
    
    data_files = os.listdir('Data')
    load_name = st.selectbox("保存した設定を選択してください", options=[''] + [filename.split('.')[0] for filename in data_files if filename.endswith('.csv')])    
    if st.button("呼び出し"):
        pv, kws = load_settings(load_name)
        if pv and kws:
            st.session_state.purchase_value = pv
            st.session_state.keywords = kws
        else:
            st.warning(f'"{load_name}" の設定を読み込めませんでした。')
        st.rerun()

# メインのStreamlitアプリケーション
def main():
    
    if 'invest' not in st.session_state:
        st.session_state.invest = False
    if 'purchase_value' not in st.session_state:
        st.session_state.purchase_value = 0.0
    if 'keywords' not in st.session_state:
        st.session_state.keywords = []
    # purchase_value = 0.0  # 初期化
    # keywords = []  # 初期化
    
    stocks = get_stocks()
    
    ############################################# side ###########################################################################################
    ############################################# side ###########################################################################################
    ############################################# side ###########################################################################################    
    
    container = st.sidebar.container(border=True)
    container.subheader('投資信託検索')
    page = int(container.selectbox(
        "対象ページ数",
        ("1", "2", "3", "4", "5", "6")))
    kinds_dict = {'人気' : 'popular', 'つみたてNISAおすすめ' : 'recommend_nisa', 'つみたてNISA利回り' : 'yield_nisa', '新NISA成長投資枠おすすめ' : 'recommend_nisa_growth', '新NISA成長投資枠利回り' : 'yield_nisa_growth', 'シャープレシオ' : 'sharpe_ratio'}
    kinds = container.selectbox(
        "カテゴリー",
        ("人気", "つみたてNISAおすすめ", "つみたてNISA利回り", "新NISA成長投資枠おすすめ", "新NISA成長投資枠利回り", "シャープレシオ"))
    kinds = kinds_dict[kinds]
    kinds2_dict = {'全て' : '', '国内株式' : '?fund_type=jp_stock', '国際株式' : '?fund_type=intl_stock', 'インデックス型' : '?fund_type=index'}
    kinds2 = container.selectbox(
        "株式種類",
        ("全て", "国内株式", "国際株式", "インデックス型"))
    kinds2 = kinds2_dict[kinds2]

    if container.button('検索実行') or st.session_state.invest == True:
        inv.Investment.create_invest(page, kinds, kinds2)
    
    ############################################# main ###########################################################################################
    ############################################# main ###########################################################################################
    ############################################# main ###########################################################################################    
    
    purchase_value = st.number_input("購入金額を入力してください(万)", min_value=0.0, value=st.session_state.purchase_value)
    
    # 呼び出し機能
    if st.sidebar.button("呼び出し機能"):
        call_favorite()
        
    keywords = st_tags(
        label='# Enter Keywords:',
        text='Press enter to add more',
        suggestions=stocks,
        # key='1',
        value=st.session_state.keywords  # 初期値を設定
    )
    
    data = []
    # if len(keywords) == 0:
    #     st.stop()
        
    for k in keywords:
        stock_info = get_stock_info(k)
        data.append(stock_info)
    
    try:
        df = pd.DataFrame(data)
        total_market_cap = df['時価総額'].sum()
        df['加重平均'] = df['時価総額'] / total_market_cap
        df['購入株数'] = (df['加重平均'] * purchase_value * 10000 / df['株価'].astype(float)).round()
        df['購入金額'] = (df['購入株数'] * df['株価'].astype(float)).round()
        df['配当金額'] = (df['配当利回'].astype(float) * df['購入株数'] * df['株価'].astype(float) / 100).round()
        
        df = df[['銘柄名', '株価', '時価総額', '加重平均', '購入金額', '購入株数', '配当利回', '配当金額']]
        
        with st.expander("銘柄詳細"):
            st.dataframe(df)
        
    except:
        pass

    # 保存機能
    if st.sidebar.button("保存機能"):
        st.session_state.keywords = keywords
        save_favorite()

    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("合計購入額")
            st.write(df['購入金額'].sum())

        with col2:
            st.write("合計配当額")
            st.write(df['配当金額'].sum())
        
        source = df[["銘柄名", "加重平均"]]
        chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
            color=alt.Color(field="銘柄名", type="nominal"),
            theta=alt.Theta(field="加重平均", type="quantitative"),
        )
        
        st.subheader('加重平均比率', divider='rainbow')
        st.altair_chart(chart, use_container_width=True)
    except:
        pass

if __name__ == "__main__":
    main()
