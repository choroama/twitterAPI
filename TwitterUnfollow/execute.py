import tweepy
import time

# 定数
TWITTER_API_CONFIGURATION_FILE_NAME = "twitterAPIConfig.csv"
FOLLOW_INTERVAL_SEC = 10  # フォローからフォローまでの最低間隔(垢BAN対策)


def execute():
    """
    全実行処理
    要件
    ・自らのフォローユーザ一覧を取得し、フォロバのないユーザーをフォロー解除する
    要確認事項
    ・フォロー解除時も10秒間隔が必要か。あるいはもっと長時間である必要があるか
    """
    api = create_api(os.getcwd() + "/" + TWITTER_API_CONFIGURATION_FILE_NAME)
    friends = api.friends()
    # フォローしてない人はフォロー解除
    for friend in friends:
        if not friend.followed:
            api.destroy_friendship(friend.id)
            time.sleep(FOLLOW_INTERVAL_SEC)


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
