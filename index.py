import tweepy
import random
import os
import time
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from events import SessionEventListener, GameEventListener

load_dotenv()

# Authentication
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Session mapping to associate sessionId with Twitter profile
session_mapping = {}
game_mapping = {}
address_mapping = {}
game_tweet_mapping = {}

def generate_session_id():
    return random.randint(100000, 999999)

def generate_game_id():
    return random.randint(1000, 9999)

# Check if user is following @handsy_io
def is_following(user):
    return client.show_friendship(source_screen_name=user, target_screen_name='handsy_io')[0].following

def extract_bet_amount(text):
    # Regular expression to capture the format "challenge you for X ETH" where X is the bet amount
    match = re.search(r'challenge.*?for\s+(\d+\s*ETH)', text)
    return match.group(1) if match else None

def check_is_challenge(text):
    return '@handsy_io' in text and 'challenge' in text

def check_if_accept(text):
    return '@handsy_io' in text and 'accept' in text

def get_challenge_recipient(status):
    # Extract mentions from the tweet
    mentions = [mention['username'] for mention in status.entities['mentions']]
    
    # Remove 'handsy_io' from mentions as it's not the recipient
    mentions = [mention for mention in mentions if mention != 'handsy_io']
    
    # If there's a mention in the tweet, return the first mention as the recipient
    if mentions:
        return mentions[0]
    
    # If the tweet is a reply, return the author of the original tweet as the recipient
    if status.in_reply_to_status_id:
        original_tweet = client.get_tweet(status.in_reply_to_status_id)
        return original_tweet.author_id
    
    # If no recipient is found, return None
    return None

#default to address if no twitter handle is found in the mappings
def get_twitter_handle_from_address(address):
    if address in address_mapping:
        sessionId = address_mapping[address]
        if sessionId in session_mapping:
            return session_mapping[sessionId]
    return address

# Event listener callback function
def on_session(session_id, user_address):
    # Store the mapping
    address_mapping[user_address] = session_id
    #log
    print(f"Session {session_id} created for {user_address}")  

def on_game_start(game_id, addressA, addressB):
    #log
    print(f"Game {game_id} started for {addressA} and {addressB}")
    # Tweet mentioning both participants and guiding them to check their DMs with @handsy_io
    client.create_tweet(status=f"@{get_twitter_handle_from_address(addressA)} @{get_twitter_handle_from_address(addressB)} Game started! Please check your DMs with @handsy_io for the game link.", in_reply_to_status_id=game_tweet_mapping[game_id])

def on_game_end(game_id, addressA, addressB, winner):
    #log
    print(f"Game {game_id} ended for {addressA} and {addressB} with result {winner}")
    # Tweet mentioning both participants and guiding them to check their DMs with @handsy_io
    client.create_tweet(status=f"@{get_twitter_handle_from_address(addressA)} @{get_twitter_handle_from_address(addressB)} Game ended! Winner is {get_twitter_handle_from_address(winner)}.", in_reply_to_status_id=game_tweet_mapping[game_id])

def on_status(status):
    text = status.text.lower()
    user = status.author_id

    # Check if the tweet is a challenge
    if check_is_challenge(text):
        bet_amount = extract_bet_amount(text)
        if bet_amount:
            if is_following(user):
                recipient = get_challenge_recipient(status)
                
                # Ask the recipient to reply with "accept" or "decline"
                client.create_tweet(status=f"@{recipient} Do you accept the challenge for {bet_amount}? Reply with 'accept' or 'decline'. Make sure to follow @handsy_io before replying.", in_reply_to_status_id=status.id)
                    #client.create_tweet(status=f"@{recipient} Please follow @handsy_io first and then reply to the challenge.", in_reply_to_status_id=status.id)
            else:
                client.create_tweet(status=f"@{user} Please follow @handsy_io first to trigger matches. [Link to follow](https://twitter.com/handsy_io)", in_reply_to_status_id=status.id)

    # Check if the recipient accepted the challenge
    elif check_if_accept(text) and status.in_reply_to_status_id:
        original_tweet = client.get_tweet(status.in_reply_to_status_id)
        if original_tweet.author_id == 'handsy_io':
            if is_following(user):
                bet_amount = extract_bet_amount(original_tweet.text)
                if bet_amount:
                    # Send DM to both challenger and recipient
                    challenger = original_tweet.author_id  # Corrected this line

                    # Generate game and session IDs
                    game_id = generate_game_id()
                    challenger_session_id = generate_session_id()
                    recipient_session_id = generate_session_id()
                    
                    # Store the mapping
                    session_mapping[challenger_session_id] = user
                    session_mapping[recipient_session_id] = recipient
                    game_mapping[challenger_session_id] = game_id
                    game_mapping[recipient_session_id] = game_id

                    # Send game and session IDs to both challenger and recipient
                    challenger_link = f"https://handsy.io?joinGame={game_id}&sessionId={challenger_session_id}&betAmount={bet_amount}"
                    recipient_link = f"https://handsy.io?joinGame={game_id}&sessionId={recipient_session_id}&betAmount={bet_amount}"
                    
                    client.send_direct_message(recipient_id=user, text=challenger_link)
                    client.send_direct_message(recipient_id=recipient, text=recipient_link)
                    
                    # Tweet mentioning both participants and guiding them to check their DMs with @handsy_io
                    created_tweet = client.create_tweet(status=f"@{challenger} @{user} Challenge accepted! Please check your DMs with @handsy_io for the game link.", in_reply_to_status_id=status.id)
                    game_tweet_mapping[game_id] = created_tweet.id
                else:
                    client.create_tweet(status=f"@{user} Error processing the challenge. Please try again.", in_reply_to_status_id=status.id)
            else:
                client.create_tweet(status=f"@{user} Try again but follow @handsy_io first.", in_reply_to_status_id=status.id)

# Create event listeners
session_listener = SessionEventListener()
game_listener = GameEventListener()

# Start polling
last_fetch_time = datetime.now() - timedelta(minutes=1)  # Start from 1 minute ago
while True:
    #fetch and handle relevant session events
    events = session_listener.fetch_recent_events()
    for event in events:
        session_listener.handle_event(event, on_session)

    #fetch and handle relevant game events
    events = game_listener.fetch_recent_game_start_events()
    for event in events:
        game_listener.handle_event(event, on_game_start)
    
    events = game_listener.fetch_recent_game_end_events()
    for event in events:
        game_listener.handle_event(event, on_game_end)

    #fetch and handle relevant tweets
    tweets = client.search_recent_tweets(query="@handsy_io challenge OR @handsy_io accept", start_time=last_fetch_time.isoformat())
    for tweet in tweets.data:
        on_status(tweet)
    last_fetch_time = datetime.now()
    time.sleep(60)  # Poll every minute
