import os
import praw
import toml
import redis
import tweepy
from pathlib import Path
from logger import log_message
from getmedia import get_imgur_endpoint


def load_general_settings(settings_path: Path):
    """Gets general settings (from env vars, config file, or defaults in decreasing priority)"""
    try:
        # Load base config dict
        settings = toml.load('settings.toml.template')
        # Check for specific config file
        if settings_path.exists():
            try:
                settings = toml.load(settings_path)
            except Exception as e:
                log_message('Error while reading config file', 2, e)
                exit()
        # Load general config vars
        if os.getenv('TOOTBOT_GENERAL_DELAY_BETWEEN_POSTS'):
            settings['general']['delay_between_posts'] = os.environ['TOOTBOT_GENERAL_DELAY_BETWEEN_POSTS']
        if os.getenv('TOOTBOT_GENERAL_POST_LIMIT'):
            settings['general']['post_limit'] = os.environ['TOOTBOT_GENERAL_POST_LIMIT']
        if os.getenv('TOOTBOT_GENERAL_SUBREDDIT_TO_MONITOR'):
            settings['general']['subreddit_to_monitor'] = os.environ['TOOTBOT_GENERAL_SUBREDDIT_TO_MONITOR']
        if os.getenv('TOOTBOT_GENERAL_NSFW_POSTS_ALLOWED'):
            settings['general']['nsfw_posts_allowed'] = os.environ['TOOTBOT_GENERAL_NSFW_POSTS_ALLOWED']
        if os.getenv('TOOTBOT_GENERAL_SPOILERS_ALLOWED'):
            settings['general']['spoilers_allowed'] = os.environ['TOOTBOT_GENERAL_SPOILERS_ALLOWED']
        if os.getenv('TOOTBOT_GENERAL_SELF_POSTS_ALLOWED'):
            settings['general']['self_posts_allowed'] = os.environ['TOOTBOT_GENERAL_SELF_POSTS_ALLOWED']
        if os.getenv('TOOTBOT_GENERAL_HASHTAGS'):
            settings['general']['hashtags'] = os.environ['TOOTBOT_GENERAL_HASHTAGS']
        # Load media config vars
        if os.getenv('TOOTBOT_MEDIA_MEDIA_FOLDER'):
            settings['media']['media_folder'] = os.environ['TOOTBOT_MEDIA_MEDIA_FOLDER']
        if os.getenv('TOOTBOT_MEDIA_MEDIA_POSTS_ONLY'):
            settings['media']['media_posts_only'] = os.environ['TOOTBOT_MEDIA_MEDIA_POSTS_ONLY']

        # Out of all necessary values up to here, the one that can't be defaulted is the subreddit to monitor. Check for it
        assert settings['general']['subreddit_to_monitor'], 'Subreddit to monitor must be a non empty string'
        return settings
    except Exception as e:
        log_message(f'Error while getting configs', 1, e)
        exit()


def load_reddit_creds(reddit_secret_path: Path):
    """Setup and verify Reddit access"""
    if os.getenv('TOOTBOT_REDDIT_AGENT') and os.getenv('TOOTBOT_REDDIT_CLIENT_SECRET'):
        return {'reddit': {
                'agent': os.environ['TOOTBOT_REDDIT_AGENT'],
                'client_secret': os.environ['TOOTBOT_REDDIT_CLIENT_SECRET']
            }
        }
    elif not reddit_secret_path.exists():
        log_message('API keys for Reddit not found. Please enter them below (see wiki if you need help).', 3)
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        REDDIT_AGENT = ''.join(input("[ .. ] Enter Reddit agent: ").split())
        REDDIT_CLIENT_SECRET = ''.join(
            input("[ .. ] Enter Reddit client secret: ").split())
        # Make sure authentication is working
        try:
            reddit_client = praw.Reddit(
                user_agent='Tootbot', client_id=REDDIT_AGENT, client_secret=REDDIT_CLIENT_SECRET)
            test = reddit_client.subreddit('announcements')
            assert test, 'Log in test failed'
            # It worked, so save the keys to a file
            reddit_config = {'reddit': {
                    'agent': REDDIT_AGENT,
                    'client_secret': REDDIT_CLIENT_SECRET
                }
            }
            with open(reddit_secret_path, 'w') as reddit_file:
                toml.dump(reddit_config, reddit_file)
            return reddit_config
        except Exception as e:
            log_message('Error while logging into Reddit', 1, e)
            exit()
    else:
        # Read API keys from secret file
        return toml.load(reddit_secret_path)


def load_imgur_creds(imgur_secret_path: Path):
    """Setup and verify Imgur access"""
    if os.getenv('TOOTBOT_IMGUR_CLIENT') and os.getenv('TOOTBOT_IMGUR_CLIENT_SECRET'):
        return {'imgur': {
                'client_id': os.environ['TOOTBOT_IMGUR_CLIENT'],
                'client_secret': os.environ['TOOTBOT_IMGUR_CLIENT_SECRET']
            }
        }
    elif not imgur_secret_path.exists():
        log_message('API keys for Imgur not found. Please enter them below (see wiki if you need help).', 3)
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        IMGUR_CLIENT = ''.join(input("[ .. ] Enter Imgur client ID: ").split())
        IMGUR_CLIENT_SECRET = ''.join(
            input("[ .. ] Enter Imgur client secret: ").split())
        # Make sure authentication is working
        try:
            test_gallery = get_imgur_endpoint('https://imgur.com/dqOyj', 'image', {'imgur': {'client_id': IMGUR_CLIENT}})
            assert test_gallery, "Log in test failed"
            # It worked, so save the keys to a file
            imgur_config = {'imgur': {
                    'client_id': IMGUR_CLIENT,
                    'client_secret': IMGUR_CLIENT_SECRET
                }
            }
            with open(imgur_secret_path, 'w') as imgur_file:
                toml.dump(imgur_config, imgur_file)
            return imgur_config
        except Exception as e:
            log_message('Error while logging into Imgur', 1, e)
            exit()
    else:
        # Read API keys from secret file
        return toml.load(imgur_secret_path)



def load_twitter_creds(twitter_secret_path: Path):
    """Setup and verify Twitter access"""
    if (os.getenv('TOOTBOT_TWITTER_ACCESS_TOKEN') and os.getenv('TOOTBOT_TWITTER_ACCESS_TOKEN_SECRET')
        and os.getenv('TOOTBOT_TWITTER_CONSUMER_KEY') and os.getenv('TOOTBOT_TWITTER_CONSUMER_SECRET')):
        return {'twitter': {
                'access_token': os.environ['TOOTBOT_TWITTER_ACCESS_TOKEN'],
                'access_token_secret': os.environ['TOOTBOT_TWITTER_ACCESS_TOKEN_SECRET'],
                'consumer_key': os.environ['TOOTBOT_TWITTER_CONSUMER_KEY'],
                'consumer_secret': os.environ['TOOTBOT_TWITTER_CONSUMER_SECRET']
            }
        }
    elif not twitter_secret_path.exists():
        # If the secret file doesn't exist, it means the setup process hasn't happened yet
        log_message('API keys for Twitter not found. Please enter them below (see wiki if you need help).', 3)
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        ACCESS_TOKEN = ''.join(input('[ .. ] Enter access token for Twitter account: ').split())
        ACCESS_TOKEN_SECRET = ''.join(input('[ .. ] Enter access token secret for Twitter account: ').split())
        CONSUMER_KEY = ''.join(input('[ .. ] Enter consumer key for Twitter account: ').split())
        CONSUMER_SECRET = ''.join(input('[ .. ] Enter consumer secret for Twitter account: ').split())
        log_message('Attempting to log in to Twitter...', 4)
        try:
            # Make sure authentication is working
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            twitter = tweepy.API(auth)
            twitter_username: str = twitter.verify_credentials().screen_name
            log_message(f'Sucessfully authenticated on Twitter as @{twitter_username}', 4)
            # It worked, so save the keys to a file
            twitter_config = {'twitter': {
                    'access_token': ACCESS_TOKEN,
                    'access_token_secret': ACCESS_TOKEN_SECRET,
                    'consumer_key': CONSUMER_KEY,
                    'consumer_secret': CONSUMER_SECRET
                }
            }
            with open(twitter_secret_path, 'w') as twitter_file:
                toml.dump(twitter_config, twitter_file)
            return twitter_config
        except Exception as e:
            log_message('Error while logging into Twitter', 1, e)
            exit()
    else:
        # Read API keys from secret file
        return toml.load(twitter_secret_path)


def load_redis_creds(redis_secret_path: Path):
    """Setup and verify Redis access"""
    if os.getenv('TOOTBOT_REDIS_HOST') and os.getenv('TOOTBOT_REDIS_PORT') and os.getenv('TOOTBOT_REDIS_PASSWORD'):
        return {'redis': {
                'host': os.environ['TOOTBOT_REDIS_HOST'],
                'port': os.environ['TOOTBOT_REDIS_PORT'],
                'password': os.environ['TOOTBOT_REDIS_PASSWORD']
            }
        }
    elif not redis_secret_path.exists():
        log_message('Redis credentials not found. Please enter them below (see wiki if you need help).', 3)
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        REDIS_HOST = ''.join(input("[ .. ] Enter Redis host: ").split())
        REDIS_PORT = int(''.join(input("[ .. ] Enter Redis port: ").split()))
        REDIS_PASSWORD = ''.join(input("[ .. ] Enter Redis password: ").split())
        # Make sure authentication is working
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
            assert r.ping(), "Connection test failed"
            # It worked, so save the keys to a file
            redis_config = {'redis': {
                    'host': REDIS_HOST,
                    'port': REDIS_PORT,
                    'password': REDIS_PASSWORD
                }
            }
            with open(redis_secret_path, 'w') as redis_file:
                toml.dump(redis_config, redis_file)
            return redis_config
        except Exception as e:
            log_message('Error while connecting to Redis', 1, e)
            exit()
    else:
        # Read API keys from secret file
        return toml.load(redis_secret_path)

def get_settings():
    general_settings = load_general_settings(Path('settings.toml'))
    reddit_creds = load_reddit_creds(Path('reddit.secret'))
    imgur_creds = load_imgur_creds(Path('imgur.secret'))
    twitter_creds = load_twitter_creds(Path('twitter.secret'))
    redis_creds = load_redis_creds(Path('redis.secret'))
    return general_settings | reddit_creds | imgur_creds | twitter_creds | redis_creds
