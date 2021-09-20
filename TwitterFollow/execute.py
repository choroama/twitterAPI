import pandas as pd
import os
import tweepy
import tkinter as tk
import time

# 定数
TWITTER_API_CONFIGURATION_FILE_NAME = "twitterAPIConfig.csv"
SEARCH_LIMIT_AT_ONCE = 100  # 1度のキーワード検索で検索できる上限は100件
NUMBER_OF_FAVORITES = 2  # 条件を満たすユーザーのツイートでいいねする件数
FOLLOW_INTERVAL_SEC = 10  # フォローからフォローまでの最低間隔(垢BAN対策)
FAVORITE_INTERVAL_SEC = 1  # いいねを行う間隔。短すぎるとうまくいかない場合がある


def create_window():
    # Tkクラス生成
    root = tk.Tk()
    # 画面サイズ
    root.geometry('300x200')
    # 画面タイトル
    root.title('自動フォローツール / 入力フォーム')
    # 入力フォーム部分
    lbl_keyword = tk.Label(text='キーワード')
    lbl_keyword.place(x=20, y=70)
    txt_keyword = tk.Entry(width=20)
    txt_keyword.place(x=90, y=70)
    lbl_entry_number = tk.Label(text='フォロー数')
    lbl_entry_number.place(x=20, y=100)
    txt_entry_number = tk.Entry(width=20)
    txt_entry_number.place(x=90, y=100)

    # ボタン作成
    btn = tk.Button(root, text='実行',
                    command=lambda: execute(txt_keyword.get(),
                                            txt_entry_number.get()))  # lambdaをつけないとボタン押下を待たずに実行される
    btn.place(x=120, y=170)

    # 表示
    root.mainloop()


def execute(keyword, entry_number_str):
    """
    全実行処理
    要件
    ・キーワード検索を行い、各ツイートを行っているユーザーの情報を見にいく
    ・フォロー > フォロワーのユーザーをフォローし、上から2つのツイートをいいねする
    ・フォローからフォローまでは10秒以上間隔を開ける(垢BAN対策)

    Parameters
    ----------
    :keyword 検索ワード
    :entry_number_str: str フォロー人数(入力値)

    """
    num_of_followed = 0
    entry_number = int(entry_number_str)
    api = create_api(os.getcwd() + "/" + TWITTER_API_CONFIGURATION_FILE_NAME)
    # フォロー人数に達するまで処理を行う
    while num_of_followed < int(entry_number):
        search_results = api.search(q=keyword, count=SEARCH_LIMIT_AT_ONCE)
        for result in search_results:
            # フォロワー < フォロー かつ フォローしていないユーザーの場合は所定の処理を実行
            if result.user.followers_count < result.user.friends_count and not result.user.following:
                api.create_friendship(result.user.screen_name)  # フォロー
                time.sleep(FOLLOW_INTERVAL_SEC)
                favorite_user_tweet(api, result.user.screen_name)
                num_of_followed += 1
                # 画面のカウントにフィードバックしたい
                # count.set(str(num_of_followed) + " / " + entry_number_str + " 件完了")
                if num_of_followed == int(entry_number):
                    break


def create_api(file_path):
    """
    TwitterAPIの設定ファイルを読み込み、APIインスタンスを返す

    Parameters
    ----------
    :filePath : str

    Returns
    -------
    :api
        APIインスタンス
    """
    # TwitterAPIの設定ファイルを読み込み、key-valueに詰め込む
    config_data = pd.read_csv(file_path, header=None, names=["key", "value"])
    # TwitterAPIの設定情報を取得
    consumer_key = config_data.iat[0, 1]
    consumer_secret = config_data.iat[1, 1]
    access_token = config_data.iat[2, 1]
    access_secret = config_data.iat[3, 1]

    # APIインスタンスを作成
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    return api


def favorite_user_tweet(api, username):
    """
    特定のユーザーのツイートをいいねする
    :param api:
    :param username:
    :return:
    """
    results = api.user_timeline(screen_name=username, count=NUMBER_OF_FAVORITES)
    for result in results:
        if not result.favorited:
            api.create_favorite(result.id)
            time.sleep(FAVORITE_INTERVAL_SEC)
