import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# csvoutput=open("sprinklrJapanese.csv", "w+", encoding="UTF-8")　＃Linuxの場合はこっち
csvoutput=open("sprinklrJapanese.csv", "w+", encoding="UTF-8-sig")

def fetch_data_from_url(url):
    response = requests.get(url)
    print(f"レスポンスは{response}")
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.title.string if soup.title else "No Title Found"
    title = title.strip(" | DELL Technologies")
    if "解決済み:" in title:
        title = title.strip("解決済み: ")

    # criptタグのtype "application/ld+json"からコンテンツを入手
    script_content = soup.find('script', {'type': 'application/ld+json'}).string

    # コンテンツをJSON形式でload、特殊文字が入っているのでstrict=Falseを設定
    json_data = json.loads(script_content, strict=False)

    # JSONデータからmainEntityのtextを抜き出し
    question_text = json_data["mainEntity"]["text"]

    author = json_data["mainEntity"]["author"]["name"]

    post_time_gmt = json_data["mainEntity"]["datePublished"]
    post_time = convert_datetime_format(post_time_gmt)

 

    try:
        init_reply_time_gmt = json_data["mainEntity"]["suggestedAnswer"]["dateCreated"]
        print("Suggedted taken")
    except:
        init_reply_time_gmt = json_data["mainEntity"]["dateModified"]

    try:
        init_reply_time_gmt = json_data["mainEntity"]["suggestedAnswer"][0]["dateCreated"]
        print("Suggedted 2 taken")
    except:
        pass

    try:
        init_reply_time_gmt_2 = json_data["mainEntity"]["acceptedAnswer"]["dateCreated"]
        print("Accepted taken")
    except:
        pass

    try:
        init_reply_time_gmt_2 = json_data["mainEntity"]["acceptedAnswer"][0]["dateCreated"]
        print("Accepted 2 taken")
    except:
        pass

    try:
        if init_reply_time_gmt_2 < init_reply_time_gmt:
            init_reply_time_gmt = init_reply_time_gmt_2
    except:
        pass

    init_reply_time = convert_datetime_format(init_reply_time_gmt)

    
    # 名前を抜き出す
    names = []

    # mainEntityの下の情報を取得
    main_entity = json_data["mainEntity"]

    # 質問者の名前
    names.append(main_entity["author"]["name"])

    # 回答者の名前を取得する関数
    def extract_names(answers):
        if isinstance(answers, dict):
            names.append(answers["author"]["name"])
        elif isinstance(answers, list):
            for answer in answers:
                names.append(answer["author"]["name"])

    # 回答者の名前
    extract_names(main_entity.get("acceptedAnswer", []))
    extract_names(main_entity.get("suggestedAnswer", []))

    # 重複なしの名前のリストを取得
    unique_names = list(set(names))

    # 名前のリストから質問者（author）を削除して回答者リストを作成
    repliers = [replier for replier in unique_names if replier != author]

    print(f"URL: {url}\nTitle: {title}\n\nText Content:\n{question_text}\n\nAuthor: {author}\nReplier(s): {repliers}\nPost Time: {post_time}\nAnswer Time: {init_reply_time}\n")
    print("-" * 50)

    csvoutput.write(url+"\t"+title+"\t"+author+"\t"+post_time+"\t"+init_reply_time)
    for i in range(len(repliers)):
        # リストの後ろの値から先に書き込むためにインデックスを-1からスタートする
        j = (i+1)*-1
        csvoutput.write("\t"+repliers[j])
    csvoutput.write("\n")
    csvoutput.close


def convert_datetime_format(dt_str):
    # 文字列をPythonのdatetimeオブジェクトに変換
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # UTCからJSTに変換 (+9時間)
    dt_jst = dt + timedelta(hours=9)
    
    # 新しい形式に変換
    # return dt_jst.strftime("%Y/%-m/%-d %-H:%M")  #Linuxの場合はこっち
    return f"{dt_jst.year}/{dt_jst.month}/{dt_jst.day} {dt_jst.hour}:{dt_jst.minute:02}" #Windowsの場合はこっち


def main():
    with open("url.txt", "r") as file:
        urls = file.readlines()
        for url in urls:
            # テキストファイルに空行（改行のみ）があった場合にエラーを出さないようにする
            try:
                fetch_data_from_url(url.strip())
            except:
                pass
            

if __name__ == "__main__":
    main()