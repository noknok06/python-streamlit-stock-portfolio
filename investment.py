import streamlit as st
import time
import API.scraping as sc
import pandas as pd

class Investment():

    @st.cache_data
    def create_invest(page, kinds, kinds2):
        
        fund_path = []

        for page_index in range(page):
            
            time.sleep(1)

            # url = "https://itf.minkabu.jp/ranking/popular?fund_type=index&page=" + str(page_index + 1)
            url = f'https://itf.minkabu.jp/ranking/{kinds}{kinds2}&page=' + str(page_index + 1)
            selector = "#rankingList > div.pageCon_plate.page-return-cache > div:nth-child(3) > div.ly_content_wrapper.size_m > div > div.md_table_wrapper.ranking_table > div.md_table_wrapper > table > tbody"

            trs = sc.get_html(url, selector, 'a')

            if trs is None:
                continue

            for tr in trs:
                try:
                    print(tr.attrs['class'])
                    fund_path.append([tr.attrs['href'], tr.text])
                except:
                    pass

        res_composition_list = []

        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        percent_complete = 0.0
        for index, fund in enumerate(fund_path):
            time.sleep(1)

            url = "https://itf.minkabu.jp" + fund[0] + "/detailed_info"
            selector = "#detailed_info_table > div.pdf_detailed_info > div.md_card.md_box.detailed_box.all_detailed_infos.ly_content_wrapper.loading_table > div.detailedInfo_table2_box.detail_stock_box > table > tbody"

            trs = sc.get_html(url, selector, 'tr')

            if trs is None:
                continue

            for tr in trs:
                try:
                    tds = tr.find_all('td')
                    company_code = tds[1].text.replace('\n', '')
                    company_name = tds[2].text.replace('\n', '')

                    sc.update_array(res_composition_list, company_code, company_name, fund[1])

                except:
                    pass
                
            percent_complete += 1/len(fund_path)
            if percent_complete <= 1:
                my_bar.progress(percent_complete, text=progress_text)
                
        my_bar.empty()

        print(res_composition_list)

        # 1列目を基準に降順でソート
        res_composition_list = sorted(res_composition_list, key=lambda x: x[2], reverse=True)

        with st.expander("投資信託構成銘柄ランキング"):

            res_array = pd.DataFrame(
                data=res_composition_list,
                columns=[
                    "ティッカー",
                    "会社名",
                    "カウント",
                    "採用投信"
                ]
            )
            st.dataframe(res_array)
            st.session_state.invest = True