import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta



def convert_entities_content(text):
    # 不要な単語をリスト
    special_charactors = ["&nbsp;", "&gt;", "‎"]

    # 不要な単語を削除
    for character in special_charactors:
        text = text.replace(character, "")
    
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
            accepted_answer_text.append("\n")
        
        elif isinstance(json_data["mainEntity"]["acceptedAnswer"], list): # リストの場合の処理
            for answer in json_data["mainEntity"]["acceptedAnswer"]:
                accepted_answer_text.append(answer["text"]) 
                accepted_answer_text.append("\n")   
        else:
            print("No accepted answer found.")
    except Exception as e:
        print(f"accepted answer取得に失敗したか、該当項目が存在しませんでした：{e}")
        accepted_answer_text.append("(受け入れられた良い回答は無し)\n")

    whole_text = ""
    whole_text += "[質問]\n"
    whole_text += question_text
    whole_text += "\n\n[提案された回答]\n"

    for content in suggested_answer_text:
        cleaned_text =convert_entities_content(content)
        whole_text += cleaned_text
    
    whole_text += "\n\n[受け入れられた良い回答]\n"
    
    for content in accepted_answer_text:
        cleaned_text = convert_entities_content(content)
        whole_text += cleaned_text
    
    return(whole_text, post_time)


def main():
    # 取得ファイル名を指定
    excel_file_name = "./excel-data/Q1FY26.xlsx"

    # エクセルファイルを読み込む
    df = pd.read_excel(excel_file_name)

    # 現在の日時を取得
    now = datetime.now()

    # 日付と時刻のフォーマットを指定
    date_format = "%Y%m%d_%H%M"
    formatted_date = now.strftime(date_format)

    file_name = "./text-data/dcf-content_{}.txt".format(formatted_date)

    with open(file_name, "a+", encoding="utf-8") as file:

        # 読みだした情報をテキストファイルに追記していく
        for url in df["Thread #"]:
            try:
                row_text, post_time = fetch_data_from_url(url)
                print(row_text)
                index_list = df[df["Thread #"] == url].index
                df_filtered = df.loc[index_list, ["Summary", "Product", "Category", "Question Type", "Answer resource"]]
                title = df_filtered["Summary"].iloc[0]
                product = df_filtered["Product"].iloc[0]
                category = df_filtered["Category"].iloc[0]
                qtype = df_filtered["Question Type"].iloc[0]
                aresource = df_filtered["Answer resource"].iloc[0]

                print(title)
                print(type(title))
                print("\n\n\n\n\n")
                print(product)
                print("\n\n\n\n\n")

                row_text = convert_entities_content(row_text)
                title = convert_entities_content(title)

                print(row_text)

                file.write(f"---\n\nタイトル: {title}\n本文: {row_text}\n製品カテゴリ: {product}\n質問カテゴリ: {category}\n質問タイプ分類: {qtype}\n回答に利用したリソース: {aresource}\n\n\n")
        

            except Exception as e:
                print(f"URLからのデータ取得かThread内容の取得に失敗しました：{e}")


if __name__ == "__main__":
    main()



