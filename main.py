import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# telegram token
TOKEN = os.environ.get('TELEGRAM_TOKEN')
# telegram chat id
CHAT_ID = os.environ.get('CHAT_ID')
# telegram api
telegram_api = f"https://api.telegram.org/bot{TOKEN}/"
# your twitch client id
client_id = os.environ.get('CLIENT_ID')
# your twitch secret
client_secret = os.environ.get('CLIENT_SECRET')

def get_token(client_id, client_secret):
    # getting auth token
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'}
    req = requests.post(url=url, params=params)
    token = req.json()['access_token']

    return token


def get_user_data(client_id, twitch_user, token):
    # getting user data (user id for example)
    url = f'https://api.twitch.tv/helix/users?login={twitch_user}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Client-Id': f'{client_id}'}
    req = requests.get(url=url, headers=headers)
    userdata = req.json()
    userid = userdata['data'][0]['id']

    return userid


def get_stream_info(client_id, user_id, token):
    # getting stream info (by user id for example)
    url = f'https://api.twitch.tv/helix/streams?user_id={user_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Client-Id': f'{client_id}'}
    req = requests.get(url=url, headers=headers)
    streaminfo = req.json()

    return streaminfo

while True:
    file = open("channels.txt", "r")
    twitch_users = {}
    for line in file.readlines():
        name = line.split(' ')
        twitch_users[name[0]] = name[1][0]
    file.close()
  
    for streamer, status in twitch_users.items():

        token = get_token(client_id, client_secret)

        user_id = get_user_data(client_id, streamer, token)

        stream_info = get_stream_info(client_id, user_id, token)

        if len(stream_info["data"]) == 0:
            # Sent when stream is closed
            if twitch_users[streamer] == '1':
                message_text = {
                    "chat_id": CHAT_ID,
                    "disable_notification": True,
                    "text": f'{streamer} is now offline!',
                }
                response = requests.post(f"{telegram_api}sendMessage", params=message_text)
                if response.status_code == 200:
                    print("Message Sent!")
            twitch_users[streamer] = '0'
        else:
            # Sent when stream is up
            if twitch_users[streamer] == '0':
                message_text = {
                    "chat_id": CHAT_ID,
                    "disable_web_page_preview": True,
                    "text": f'{stream_info["data"][0]["user_name"]} is now live!\nTitle: {stream_info["data"][0]["title"]}\nLink: twitch.tv/{streamer}',
                }
                response = requests.post(f"{telegram_api}sendMessage", params=message_text)
                if response.status_code == 200:
                    print("Message Sent!")
                else:
                  print("Something went wrong sending the message!")
            twitch_users[streamer] = '1'

    file = open("channels.txt", "w")
    text = []
    for streamer, status in twitch_users.items():
        text.append(f"{streamer} {status}\n")
    file.writelines(text)
    file.close()
    print("Waiting 60 seconds...")
    time.sleep(60)
