import os
import time
import praw
import redis
import tweepy
import datetime
import requests
from getmedia import get_media
from getsettings import get_settings


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
        raise ValueError(f'invalid truth value {val}')


def get_reddit_posts(subreddit_info: praw.reddit.models.Subreddit, settings: dict) -> dict:
    post_dict = {}
    print('[ OK ] Getting posts from Reddit...')
    for submission in subreddit_info.hot(limit=int(settings['general']['post_limit'])):
        if (submission.over_18 and strtobool(settings['general']['nsfw_posts_allowed']) is False):
            # Skip over NSFW posts if they are disabled in the config file
            print(f'[ OK ] Skipping {submission.id} because it is marked as NSFW')
        elif (submission.is_self and strtobool(settings['general']['self_posts_allowed']) is False):
            # Skip over NSFW posts if they are disabled in the config file
            print(f'[ OK ] Skipping {submission.id} because it is a self post')
        elif (submission.spoiler and strtobool(settings['general']['spoilers_allowed']) is False):
            # Skip over posts marked as spoilers if they are disabled in the config file
            print(f'[ OK ] Skipping {submission.id} because it is marked as a spoiler')
        elif (submission.stickied):
            print(f'[ OK ] Skipping {submission.id} because it is stickied')
        else:
            # Create dict
            post_dict[submission.id] = submission
    return post_dict


def get_twitter_caption(submission: praw.reddit.models.Submission, settings: dict):
    # Create string of hashtags
    hashtag_string = ''
    if settings['general']['hashtags']:
        # Parse list of hashtags
        HASHTAGS = settings['general']['hashtags']
        HASHTAGS = [x.strip() for x in HASHTAGS.split(',')]
    else:
        HASHTAGS = ''
    if HASHTAGS:
        for hashtag in HASHTAGS:
            # Add hashtag to string, followed by a space for the next one
            hashtag_string += '#' + hashtag + ' '
    # Set the Twitter max title length for 280, minus the length of the shortlink and hashtags, minus one for the space between title and shortlink
    twitter_max_title_length = 280 - len(submission.shortlink) - len(hashtag_string) - 1
    # Create contents of the Twitter post
    if len(submission.title) < twitter_max_title_length:
        twitter_caption = f'{submission.title} {hashtag_string}{submission.shortlink}'
    else:
        twitter_caption = f'{submission.title[:twitter_max_title_length-3]}... {hashtag_string}{submission.shortlink}'
    return twitter_caption


def setup_connection_reddit(subreddit: str, settings: dict):
    print('[ OK ] Setting up connection with Reddit...')
    r = praw.Reddit(
        user_agent='Tootbot',
        client_id=settings['reddit']['agent'],
        client_secret=settings['reddit']['client_secret'])
    return r.subreddit(subreddit)


def duplicate_check(id: str, settings: dict):
    r = redis.Redis(host=settings['redis']['host'], port=settings['redis']['port'], db=0, password=settings['redis']['password'])
    return r.get(id)


def log_post(id: str, post_url: str, settings: dict):
    r = redis.Redis(host=settings['redis']['host'], port=settings['redis']['port'], db=0, password=settings['redis']['password'])
    r.set(id, post_url)
    r.set(f"{id}:timestamp", datetime.datetime.now().isoformat())


def make_post(post_dict: dict, settings: dict):
    post = next((post for post in post_dict if not duplicate_check(post, settings)), None)
    post_id = post_dict[post].id
    media_file = get_media(post_dict[post].url, settings)
    # Post on Twitter
    # Make sure the post contains media, if MEDIA_POSTS_ONLY in config is set to True
    if ((settings['media']['media_posts_only'] and media_file) or not settings['media']['media_posts_only']):
        try:
            auth = tweepy.OAuthHandler(settings['twitter']['consumer_key'], settings['twitter']['consumer_secret'])
            auth.set_access_token(settings['twitter']['access_token'], settings['twitter']['access_token_secret'])
            twitter = tweepy.API(auth)
            # Generate post caption
            caption = get_twitter_caption(post_dict[post], settings)
                # Post the tweet
            if (media_file):
                print(f'[ OK ] Posting this on Twitter with media attachment: {caption}')
                media = twitter.media_upload(filename=media_file)
                assert media, "Couldn't load media"
                tweet = twitter.update_status(status=caption, media_ids=[media.media_id_string])
                # Clean up media file
                try:
                    os.remove(media_file)
                    print(f'[ OK ] Deleted media file at {media_file}')
                except Exception as e:
                    print(f'[ERR ] Error while deleting media file: {str(e)}')
            else:
                print('[ OK ] Posting this on Twitter: {caption}')
                tweet = twitter.update_status(status=caption)
            # Log the tweet
            log_post(post_id, f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}/', settings)
        except Exception as e:
            print(f'[ERR ] Error while posting tweet: {str(e)}')
            # Log the post anyways
            log_post(post_id, f'Error while posting tweet: {str(e)}', settings)
    else:
        print('[WARN] Twitter: Skipping', post_id, 'because non-media posts are disabled or the media file was not found')
        # Log the post anyways
        log_post(post_id, 'Twitter: Skipped because non-media posts are disabled or the media file was not found', settings)


def check_updates():
    # Check for updates
    try:
        response = requests.get("https://raw.githubusercontent.com/isthistechsupport/tootbot/update-check/current-version.txt")
        new_version = float(response.text)
        current_version = 3.0  # Current version of script
        if (current_version < new_version):
            print(f'[WARN] A new version of Tootbot ({str(new_version)}) is available! (you have {str(current_version)})')
            print('[WARN] Get the latest update from here: https://github.com/isthistechsupport/tootbot/releases')
        else:
            print(f'[ OK ] You have the latest version of Tootbot ({str(current_version)})')
    except Exception as e:
        print(f'[ERR ] Error while checking for updates: {str(e)}')


def main():
    check_updates()
    settings = get_settings()
    # Run the main script
    while True:
        # Continue with script
        try:
            subreddit = setup_connection_reddit(settings['general']['subreddit_to_monitor'], settings)
            post_dict = get_reddit_posts(subreddit, settings)
            make_post(post_dict, settings)
        except Exception as e:
            print('[ERR ] Error in main process:', str(e))
        print(f'[ OK ] Sleeping for {int(settings["general"]["delay_between_posts"])} seconds')
        time.sleep(int(settings['general']['delay_between_posts']))
        print('[ OK ] Restarting main process...')


if __name__ == '__main__':
    main()