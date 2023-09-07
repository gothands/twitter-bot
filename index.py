import tweepy
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Authentication
CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# Check if user is following @handsy_io
def is_following(user):
    return api.show_friendship(source_screen_name=user, target_screen_name='handsy_io')[0].following

# Stream Listener
class HandsyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text = status.text.lower()
        user = status.user.screen_name

        # Check if the tweet is a challenge
        if '@handsy_io challenge' in text:
            if is_following(user):
                if 'challenge you for' in text:
                    recipient = user
                else:
                    recipient = text.split('@handsy_io challenge ')[1].split(' for ')[0].replace('@', '').strip()

                # Check if recipient is following
                if is_following(recipient):
                    # Ask the recipient to reply with "accept" or "decline"
                    api.update_status(f"@{recipient} Do you accept the challenge? Reply with 'accept' or 'decline'.", in_reply_to_status_id=status.id)
                else:
                    api.update_status(f"@{recipient} Please follow @handsy_io first and then reply to the challenge.", in_reply_to_status_id=status.id)
            else:
                api.update_status(f"@{user} Please follow @handsy_io first to trigger matches. [Link to follow](https://twitter.com/handsy_io)", in_reply_to_status_id=status.id)

        # Check if the recipient accepted the challenge
        elif 'accept' in text and status.in_reply_to_status_id:
            original_tweet = api.get_status(status.in_reply_to_status_id)
            if original_tweet.user.screen_name == 'handsy_io':
                if is_following(user):
                    game_link = f"https://handsy.io?joinGame=#{random.randint(1000, 9999)}"
                    api.send_direct_message(recipient_id=status.user.id_str, text=game_link)
                    api.update_status(f"@{user} User accepted. Sending game link in DMs.", in_reply_to_status_id=status.id)
                else:
                    api.update_status(f"@{user} Try again but follow @handsy_io first.", in_reply_to_status_id=status.id)

    def on_error(self, status_code):
        if status_code == 420:
            return False

# Stream
listener = HandsyStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=listener)
stream.filter(track=['@handsy_io challenge', '@handsy_io accept'])

# Note: This script is a basic implementation and might need further refinement and error handling for production use.
