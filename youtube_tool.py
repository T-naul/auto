import os
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from botYTB import reply_cmt
import asyncio
import logging
import tempfile
import time


current_date = datetime.now().strftime("%Y_%m_%d")
log_filename = f"ytb_bot_{current_date}_logs.txt"
log_dir = f"{tempfile.gettempdir()}\\ybt_bot\\logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up the logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",  # Định dạng log
    datefmt="%Y-%m-%d %H:%M:%S",  # Định dạng thời gian
    filename=f'{log_dir}\\{log_filename}',  # Tên file lưu log theo ngày
    filemode="a"  # Mở file ở chế độ append (thêm vào cuối file)
)

example_rely = {
    '2': 'Thank you for watching the whole video and leaving comments. Please subscribe to our channel to motivate us to make better videos.',
    '7' : 'Thank you for leaving a comment. Hope our next videos will be suitable for you.'
}

def log_message(tk, logging_text, message):
    logging_text.insert(tk.END, message + '\n')  # Thêm log vào Text widget
    logging_text.see(tk.END)  # Cuộn đến cuối cùng để hiển thị log mới nhất
    logging_text.update_idletasks()  # Cập nhật giao diện

def get_recent_videos(youtube, channel_id, tk=None, logging_text=None):
    video_ids = []
    next_page_token = None

    while True:
        try:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=20,
                order="date",
                type="video",
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                video_ids.append(item['id']['videoId'])
            
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
        except Exception as e:
            logging.error(f"An error when get videos id: {e}")
            log_message(tk, logging_text, f"An error when get videos id: {e}")
            break

    return video_ids

async def process_comments(youtube, replied_to, video_id, tk=None, logging_text=None):
    # Set up the parameters for the API call   
    params = {
        "part":"snippet, replies",
        "videoId": video_id,
        "textFormat": "plainText",
        'maxResults': 100,
        'order': 'time',
    }

    request = youtube.commentThreads().list(**params)

    # Loop through the pages of results
    while request:
        # Execute the API call
        try:
            response = request.execute()
            end = False
            ## Loop through the comments in the current page of results
            if len(response["items"]) > 0:
                for item in response["items"]:
                    comment = item["snippet"]["topLevelComment"]
                    ## Check if the comment has not been replied to yet
                    if comment["id"] not in replied_to:
                        ## Extract the author's name and the comment text
                        author_name = comment["snippet"]["authorDisplayName"]
                        comment_text = comment["snippet"]["textDisplay"]
                        logging.info(f"Comment from {author_name}: {comment_text}")
                        log_message(tk, logging_text, f"Comment from {author_name}: {comment_text}")
                        try:
                            if comment_text in example_rely.keys():
                                response_text = example_rely[comment_text]
                            else:
                                response_text = await reply_cmt(comment_text) 

                                ## Reply to the comment
                                youtube.comments().insert(
                                    part="snippet",
                                    body={
                                        "snippet": {
                                            "parentId": comment['id'],
                                            "textOriginal": response_text
                                        }
                                    }
                                ).execute()

                                replied_to.add(comment["id"])
                                logging.info(f"Replied to {comment['id']} with: {response_text}")
                                log_message(tk, logging_text, f"Replied to {comment['id']} with: {response_text}")
                        except Exception as e:
                            logging.error(f"Error when get text reply: {e}")
                            log_message(tk, logging_text, f"Error when get text reply: {e}")  
                    else:
                        ## If the comment has already been replied to, end the loop
                        end = True
                        break
            if end:
                break
            # Check if there are more pages of results
            if "nextPageToken" in response:
                # Set up the parameters for the next page of results
                request = youtube.commentThreads().list(**params,pageToken=response["nextPageToken"])
            else:
                # If there are no more pages of results, exit the loop
                request = None
        except Exception as e:
            logging.error(f"An error when get comments: {e}")
            log_message(tk, logging_text, f"An error when get comments: {e}")
            break

def bot_run(temp_reply_dir, youtube, video_id, tk, logging_text):
    try:
        with open(f"{temp_reply_dir}\\replied_to_{video_id}.pickle", "rb") as f:
            replied_to = pickle.load(f)
    except FileNotFoundError:
        replied_to = set()
    asyncio.run(process_comments(youtube, replied_to, video_id, tk, logging_text))

    with open(f"{temp_reply_dir}\\replied_to_{video_id}.pickle", "wb") as f:
            pickle.dump(replied_to, f)

def bot_ytb(tk, logging_text, running, video_id):
    log_message( tk, logging_text,"Starting the app")
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    temp_settings_dir = f"{tempfile.gettempdir()}\\ybt_bot\\settings"
    client_secrets_file = f'{temp_settings_dir}\\client_secret.json'

    flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            scopes=SCOPES
            )

    try:
        # Try to load the credentials from the pickle file
        with open(f"{temp_settings_dir}\\credentials.pickle", "rb") as f:
            creds = pickle.load(f)
    except FileNotFoundError:
        creds = flow.run_local_server(port=8080)
        with open(f"{temp_settings_dir}\\credentials.pickle", "wb") as f:
            pickle.dump(creds, f)

    try:
        youtube = build('youtube', 'v3', credentials=creds)

        try: 
            response = youtube.channels().list(
                            part="id",
                            mine=True
                        ).execute()
            CHANNEL_ID = response['items'][0]['id']
        except:
            CHANNEL_ID = "UCo3Savl7UdNKFVFFnbUZHWA"

        temp_reply_dir = f"{tempfile.gettempdir()}\\ybt_bot\\replied_to"
        if not os.path.exists(temp_reply_dir):
            os.makedirs(temp_reply_dir)

        if video_id:
            bot_run(temp_reply_dir, youtube, video_id, tk, logging_text)
        else:
            while running[0]:
                recent_videos = get_recent_videos(youtube, CHANNEL_ID, tk, logging_text)
                
                for temp_video_id in recent_videos:
                    logging.info(f"Process comment in video: {temp_video_id}")
                    log_message(tk, logging_text, f"Process comment in video: {temp_video_id}")
                    bot_run(temp_reply_dir, youtube, temp_video_id, tk, logging_text)
                
                logging.info(f"Process all video wait the next scan (1min)...")
                log_message(tk, logging_text, f"Process all video wait the next scan (1min)...")
                time.sleep(60)
        
        log_message(tk, logging_text, "Processing paused or completed.\n")
    except Exception as e:
        logging.error(f"Main error: {e}")
        log_message(tk, logging_text, f"Main error: {e}")

