import os
import sys
import praw
import redis
import tweepy
import tweepy.api
import tweepy.models
import logger
import logging
import datetime
import tweepy.client
from typing import Any
from pathlib import Path
from threading import Event
from getmedia import get_media
from getsettings import get_settings


settings = get_settings()


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f'Invalid boolean text {val}')


def get_reddit_posts(subreddit_info: praw.reddit.models.Subreddit) -> dict[str, praw.reddit.models.Submission]:
    """Get the valid posts from the subreddit and return them in a dictionary using their ID as the key."""
    post_dict = {}
    logging.info('Getting posts from Reddit...')
    for submission in subreddit_info.hot(limit=int(settings['general']['post_limit'])):
        if (submission.over_18 and strtobool(settings['general']['nsfw_posts_allowed']) is False):
            # Skip over NSFW posts if they are disabled in the config file
            logging.info(f'Skipping {submission.id} because it is marked as NSFW')
        elif (submission.is_self and strtobool(settings['general']['self_posts_allowed']) is False):
            # Skip over self posts if they are disabled in the config file
            logging.info(f'Skipping {submission.id} because it is a self post')
        elif (submission.spoiler and strtobool(settings['general']['spoilers_allowed']) is False):
            # Skip over posts marked as spoilers if they are disabled in the config file
            logging.info(f'Skipping {submission.id} because it is marked as a spoiler')
        elif (submission.stickied):
            logging.info(f'Skipping {submission.id} because it is stickied')
        else:
            # Append post to dict
            post_dict[submission.id] = submission
    return post_dict


def get_twitter_caption(submission: praw.reddit.models.Submission) -> str:
    """Create the caption for the Twitter post"""
    hashtags = settings['general']['hashtags'].split(',')
    hashtag_string = ' '.join([f'#{hashtag.strip()}' for hashtag in hashtags]) if hashtags else ''
    # Set the Twitter max title length for 280, minus the length of the shortlink and hashtags, minus one for the space between title and shortlink
    twitter_max_title_length = 280 - len(submission.shortlink) - len(hashtag_string) - 1
    # Create contents of the Twitter post
    if len(submission.title) < twitter_max_title_length:
        twitter_caption = f'{submission.title} {hashtag_string} {submission.shortlink}'
    else:
        twitter_caption = f'{submission.title[:twitter_max_title_length-3]}... {hashtag_string} {submission.shortlink}'
    return twitter_caption


def setup_connection_reddit(subreddit: str) -> praw.reddit.models.Subreddit:
    """Set up the connection to Reddit and return the subreddit object"""
    logging.info('Setting up connection with Reddit...')
    r = praw.Reddit(
        user_agent='raspberrypi:tootbot:v3.0.2 (by /u/isthistechsupport)',
        client_id=settings['reddit']['agent'],
        client_secret=settings['reddit']['client_secret']
    )
    return r.subreddit(subreddit)


def duplicate_check(id: str) -> bool:
    """Check if the post has already been posted"""
    try:
        r = redis.Redis(
            host=settings['redis']['host'],
            port=int(settings['redis']['port']),
            db=0, password=settings['redis']['password']
        )
        return bool(r.get(id))
    except Exception as e:
        logging.critical(e, stack_info=True, exc_info=True)
        sys.exit(-1)


def log_post(id: str, post_url: str):
    """Log the post to Redis"""
    r = redis.Redis(
        host=settings['redis']['host'],
        port=int(settings['redis']['port']),
        db=0,
        password=settings['redis']['password']
    )
    r.set(id, post_url)
    r.set(f"{id}:timestamp", datetime.datetime.now().isoformat())


def post_tweet(caption: str, media_file: Path | None = None):
    """Post the tweet to Twitter"""
    auth = tweepy.OAuth1UserHandler(
        consumer_key=settings['twitter']['consumer_key'],
        consumer_secret=settings['twitter']['consumer_secret'],
        access_token=settings['twitter']['access_token'],
        access_token_secret=settings['twitter']['access_token_secret']
    )
    twitter_api: tweepy.api.API = tweepy.API(auth)
    twitter_client: tweepy.client.Client = tweepy.Client(
        consumer_key=settings['twitter']['consumer_key'],
        consumer_secret=settings['twitter']['consumer_secret'],
        access_token=settings['twitter']['access_token'],
        access_token_secret=settings['twitter']['access_token_secret']
    )
    if media_file:
        logging.info(f'Posting this on Twitter with media attachment: {caption}')
        media: Any = twitter_api.media_upload(filename=media_file)
        assert media, "Couldn't load media to Twitter"
        tweet = twitter_client.create_tweet(text=caption, media_ids=[media.media_id])
        # Clean up media file
        try:
            os.remove(media_file)
            logging.info(f'Deleted media file at {media_file}')
        except Exception as e:
            logging.error(e, stack_info=True, exc_info=True)
    else:
        logging.info(f'Posting this on Twitter: {caption}')
        tweet = twitter_client.create_tweet(text=caption)
    return tweet


def make_post(post_dict: dict[str, praw.reddit.models.Submission]):
    """Check for new posts and post them to Twitter, if possible"""
    post = next((post for post in post_dict if not duplicate_check(post)), None)
    if not post:
        logging.info('No new posts found')
        return
    post_id = post_dict[post].id
    media_file = get_media(post_dict[post].url)
    # Make sure the post contains media, if MEDIA_POSTS_ONLY in config is set to True
    is_media_allowed_and_available = strtobool(settings['media']['media_posts_only']) and media_file
    is_non_media_allowed = not strtobool(settings['media']['media_posts_only'])
    if not is_media_allowed_and_available and not is_non_media_allowed:
        logging.warning(f'Twitter: Skipping {post_id} because non-media posts are disabled or the media file was not found')
        # Log the post anyways
        log_post(post_id, 'Twitter: Skipped because non-media posts are disabled or the media file was not found')
        return
    try:
        tweet = post_tweet(get_twitter_caption(post_dict[post]), media_file)
        # Log the tweet
        if isinstance(tweet, tweepy.client.Response):
            tweet_id = tweet.data['id']
        elif isinstance(tweet, dict):
            tweet_id = tweet['data']['id']
        else:
            tweet_id = tweet.json()['data']['id']
        log_post(post_id, f"https://twitter.com/i/web/status/{tweet_id}/")
    except Exception as e:
        logging.error(e, stack_info=True, exc_info=True)
        # Log the post anyways
        log_post(post_id, f'Error while posting tweet: {str(e.__class__)}: {str(e)}')


exit = Event()


def main():
    logger.init_logging()
    settings = get_settings()
    i = 0
    # Run the main script
    while not exit.is_set():
        # Continue with script
        i += 1
        if i > 1:
            logging.info(f'Restarting main process (iteration: {i})')
        try:
            subreddit = setup_connection_reddit(settings['general']['subreddit_to_monitor'])
            post_dict = get_reddit_posts(subreddit)
            make_post(post_dict)
        except Exception as e:
            logging.error(e, stack_info=True, exc_info=True)
        logging.info(f'Sleeping for {int(settings["general"]["delay_between_posts"])} seconds')
        exit.wait(int(settings['general']['delay_between_posts']))


def quit(signo, _):
    match signo:
        case 1: signame = 'SIGHUP'
        case 2: signame = 'SIGINT'
        case 15: signame = 'SIGTERM'
        case _: signame = 'unknown signal'
    logging.critical(f'Interrupted by {signame}, shutting down')
    exit.set()


if __name__ == '__main__':
    import signal
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit);

    main()
