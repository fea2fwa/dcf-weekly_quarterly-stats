import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta


load_dotenv()  # .envファイルから環境変数を読み込む
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def convert_entities_content(text):
    # 不要な単語をリスト
    special_charactors = ["&nbsp;", "&gt;"]

    # 不要な単語を削除
    for character in special_charactors:
        text = text.replace(character, "")
    
    return text

def delete_newline_charactor(text):
    # 改行文字をスペースに置き換え
    text = text.replace("\n", " ")

    return text

def convert_entities_htmltag(text):
    # &lt; を < に置き換え
    text = text.replace("&lt;", "<")
    
    # &gt; を > に置き換え
    text = text.replace("&gt;", ">")

    return text

def convert_entities_refine(text):

    text = text.replace("<th>Summary</th>", "<th><center>タイトル（URL）</center></th>")
    text = text.replace("<th>Summary (AI generated)</th>", "<th><center>要約 (AIによる作成)</center></th>")
    text = text.replace("<th>Post time</th>", "<th><center>投稿日</center></th>")

    return text

def fetch_data_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser') 


    # bs4とdatetimeで投稿時間（日本時間はtimedeltaを利用）を取得
    date_text = soup.find('p', class_='m-r-1 dell-conversation-ballon__header-date text text--normal css-1ry1tx8 css-jp8xm2').get_text(strip=True)
    original_time = datetime.strptime(date_text, "%Y年%m月%d日 %H:%M")
    new_time = original_time + timedelta(hours=9)
    post_time = new_time.strftime('%Y/%m/%d')

    # criptタグのtype "application/ld+json"からコンテンツを入手
    script_content = soup.find('script', {'type': 'application/ld+json'}).string

    # コンテンツをJSON形式でload、特殊文字が入っているのでstrict=Falseを設定
    json_data = json.loads(script_content, strict=False)

    # JSONデータからmainEntityのtextを抜き出し
    try:
        question_text = json_data["mainEntity"]["text"]
    except:
        question_text = None

    try:
        suggested_answer_text = []
        if isinstance(json_data["mainEntity"]["suggestedAnswer"], dict): # ディクショナリの場合の処理
            suggested_answer_text.append(json_data["mainEntity"]["suggestedAnswer"]["text"])
        
        elif isinstance(json_data["mainEntity"]["suggestedAnswer"], list): # リストの場合の処理
            for answer in json_data["mainEntity"]["suggestedAnswer"]:
                suggested_answer_text.append(answer["text"])    
        else:
            print("No suggested answer found.")
    except Exception as e:
        print(f"suggested answer取得に失敗したか、該当項目が存在しませんでした：{e}")

    try:
        accepted_answer_text = []
        if isinstance(json_data["mainEntity"]["acceptedAnswer"], dict): # ディクショナリの場合の処理
            accepted_answer_text.append(json_data["mainEntity"]["acceptedAnswer"]["text"])
        
        elif isinstance(json_data["mainEntity"]["acceptedAnswer"], list): # リストの場合の処理
            for answer in json_data["mainEntity"]["acceptedAnswer"]:
                accepted_answer_text.append(answer["text"])    
        else:
            print("No accepted answer found.")
    except Exception as e:
        print(f"accepted answer取得に失敗したか、該当項目が存在しませんでした：{e}")

    whole_text = ""
    whole_text += "[質問]"
    whole_text += question_text
    whole_text += "[提案された回答]"

    for content in suggested_answer_text:
        cleaned_text =convert_entities_content(content)
        whole_text += cleaned_text
    
    whole_text += "[受け入れられた良い回答]"
    
    for content in accepted_answer_text:
        cleaned_text = convert_entities_content(content)
        whole_text += cleaned_text

    return(whole_text, post_time)


def main():
    # 取得ファイル名と取得するプロダクト情報を決定
    excel_file_name = "./excel-data/Q1FY26.xlsx"
    target_product = "VxRail"

    ### タイトルとそのタイトルにURLを埋め込んだDataFrameを作成するセクション ###
    # エクセルファイルを読み込む
    df_title = pd.read_excel(excel_file_name)

    

    # E列の値が「URL」の場合に、F列の文字列にB列のURL情報をHTMLで埋め込む
    for i in range(len(df_title)):
        if df_title.loc[i, "Product"] == target_product:
            df_title.loc[i, "Summary"] = "<a href=\"{0}\">{1}</a>".format(df_title.loc[i, "Thread #"], df_title.loc[i, "Summary"])

    df_title = df_title.loc[df_title["Product"] == target_product]

    print(df_title.head(10))

    df_title = df_title[["Summary"]]

    print(df_title.head(10))
    print(df_title.shape)
    

    ### コンテンツの内容を読み込み、その内容をGemini APIに渡して要約を作成して、更にそのコンテンツの書き込み日をDataFrameにするセクション ###
    # エクセルファイルを読み込む
    df = pd.read_excel(excel_file_name)

    # VxRailに関するコンテンツのみを抽出
    df = df.loc[df["Product"] == target_product]

    # df_summary = pd.DataFrame(columns=["Summary (AI generated)"])
    summary_list = []
    post_time_list = []
    for url in df["Thread #"]:
        try:
            row_text, post_time = fetch_data_from_url(url)
            response = model.generate_content(f"次の文章を200文字以内で要約して:{row_text}")
            print(post_time)
            print(response.text)
            summary_list.append(delete_newline_charactor(response.text))
            post_time_list.append(post_time)
        except Exception as e:
            print(f"URLからのデータ取得かThread内容の取得に失敗しました：{e}")
            summary_list.append("（情報取得に失敗しました。当該コンテンツは削除されている、もしくはURLが変更されている可能性があります。）")
            post_time_list.append("N/A")

 
    df_summary = pd.DataFrame({"Summary (AI generated)": summary_list, "Post time": post_time_list})                                      
    print(df_summary.head(10))
    print(df_summary.shape)

    df_title.reset_index(drop=True, inplace=True)
    df_summary.reset_index(drop=True, inplace=True)
    
    output_df = pd.concat([df_title, df_summary], axis=1)

    print(output_df)

    # HTMLのテーブル形式で表示する
    html = output_df.to_html(index=False)

    # タグを特殊文字から修正
    html = convert_entities_htmltag(html)

    # タイトルなどの微調整
    html = convert_entities_refine(html)


    html_output = open(f"./html-data/htmltext_{target_product}.txt", "w+", encoding="UTF-8")
    html_output.write(html)
    html_output.close()

    

if __name__ == "__main__":
    main()



