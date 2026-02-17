import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta
import time

url="https://www.dell.com/community/ja/conversations/%E3%82%B9%E3%83%88%E3%83%AC%E3%83%BC%E3%82%B8-%E3%82%B3%E3%83%9F%E3%83%A5%E3%83%8B%E3%83%86%E3%82%A3/dpsuite%E3%81%AEcpu%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9%E8%BF%BD%E5%8A%A0%E6%99%82%E3%81%AEavamar-ve%E3%81%AE%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/690946268ce6a621469d187e"

def fetch_data_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser') 


    # bs4とdatetimeで投稿時間（日本時間はtimedeltaを利用）を取得
    # date_text = soup.find('p', class_='m-r-1 dell-conversation-ballon__header-date text text--normal css-1ry1tx8 css-jp8xm2').get_text(strip=True)
    # original_time = datetime.strptime(date_text, "%Y年%m月%d日 %H:%M")

    meta_tag = soup.find('meta', property='article:published_time')

    if meta_tag:
        # content属性の値 (2025-11-04T00:17:42.590Z) を取得
        raw_date = meta_tag.get('content')
        
        # ISO形式の文字列をdatetimeオブジェクトに変換
        # ※末尾のZはUTC（協定世界時）を意味します
        dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
        
        # 指定の形式にフォーマット
        # %-d は0埋めなしの日にち（Windows環境では %#d）
        date_text = dt.strftime('%Y年%m月%d日%H:%M').replace(' 0', ' ')
        
        # 「04日」を「4日」にするための調整（簡易的な置換例）
        date_text = dt.strftime('%Y年%m月').replace(' 0', '') + str(dt.day) + "日" + dt.strftime(' %H:%M')

        original_time = datetime.strptime(date_text, "%Y年%m月%d日 %H:%M")
    else:
        print("該当するタグが見つかりませんでした。")

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

    # whole_text = ""
    # whole_text += "[質問]"
    # whole_text += question_text
    # whole_text += "[提案された回答]"

    # for content in suggested_answer_text:
    #     cleaned_text =convert_entities_content(content)
    #     whole_text += cleaned_text
    
    # whole_text += "[受け入れられた良い回答]"
    
    # for content in accepted_answer_text:
    #     cleaned_text = convert_entities_content(content)
    #     whole_text += cleaned_text

    # return(whole_text, post_time)


fetch_data_from_url(url)