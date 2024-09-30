import os
import sys
import logging


def get_settings() -> dict[str, dict[str, str]]:
    """Gets all settings from env vars"""
    try:
        settings = {
            "general": {
                "delay_between_posts": os.getenv("TOOTBOT_GENERAL_DELAY_BETWEEN_POSTS", "900"),
                "post_limit": os.getenv("TOOTBOT_GENERAL_POST_LIMIT", "10"),
                "subreddit_to_monitor": os.environ["TOOTBOT_GENERAL_SUBREDDIT_TO_MONITOR"],
                "nsfw_posts_allowed": os.getenv("TOOTBOT_GENERAL_NSFW_POSTS_ALLOWED", "False"),
                "spoilers_allowed": os.getenv("TOOTBOT_GENERAL_SPOILERS_ALLOWED", "True"),
                "self_posts_allowed": os.getenv("TOOTBOT_GENERAL_SELF_POSTS_ALLOWED", "True"),
                "hashtags": os.getenv("TOOTBOT_GENERAL_HASHTAGS")
            },
            "media": {
                "media_folder": os.getenv("TOOTBOT_MEDIA_MEDIA_FOLDER", "media"),
                "media_posts_only": os.getenv("TOOTBOT_MEDIA_MEDIA_POSTS_ONLY", "False")
            },
            "reddit": {
                "agent": os.environ["TOOTBOT_REDDIT_AGENT"],
                "client_secret": os.environ["TOOTBOT_REDDIT_CLIENT_SECRET"],
            },
            "imgur": {
                "client_id": os.environ["TOOTBOT_IMGUR_CLIENT"],
                "client_secret": os.environ["TOOTBOT_IMGUR_CLIENT_SECRET"]
            },
            "twitter": {
                "access_token": os.environ["TOOTBOT_TWITTER_ACCESS_TOKEN"],
                "access_token_secret": os.environ["TOOTBOT_TWITTER_ACCESS_TOKEN_SECRET"],
                "consumer_key": os.environ["TOOTBOT_TWITTER_CONSUMER_KEY"],
                "consumer_secret": os.environ["TOOTBOT_TWITTER_CONSUMER_SECRET"]
            },
            "redis": {
                "host": os.environ["TOOTBOT_REDIS_HOST"],
                "port": os.environ["TOOTBOT_REDIS_PORT"],
                "password": os.environ["TOOTBOT_REDIS_PASSWORD"]
            },
            "logging": {
                "log_destination": os.getenv("TOOTBOT_LOG_DESTINATION", "localhost"),
                "log_port": os.getenv("TOOTBOT_LOG_PORT", "514")
            }
        }
        return settings
    except Exception as e:
        logging.critical(e, stack_info=True, exc_info=True)
        sys.exit(-1)
