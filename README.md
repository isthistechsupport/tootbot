# Tootbot

This is a dockerized Python bot that looks up posts from specified subreddits and automatically posts them on Twitter. It is based on Corbin Davenport's [tootbot](https://github.com/corbindavenport/tootbot). Tootbot is now used by [a wide variety of social media accounts](https://github.com/corbindavenport/tootbot/wiki/Accounts-using-Tootbot).

## Features

* Can post to Twitter
* Runs on any PC with Docker
* Media from direct links, Imgur, Reddit, and Giphy is automatically attached in the tweet
* Links that do not contain media can be skipped, ideal for meme accounts
* NSFW content, spoilers, and self-posts can be filtered
* Multiple subreddits can be monitored at once

Tootbot uses the [tweepy](https://github.com/tweepy/tweepy), [PRAW](https://praw.readthedocs.io/en/latest/), and [redis-py](https://github.com/andymccurdy/redis-py) libraries.

## Disclaimer

The developers of Tootbot hold no liability for what you do with this script or what happens to you by using this script. Abusing this script *can* get you banned from Twitter, so make sure to read up on proper usage of the API.

## Setup and usage

### Prerequisites

* Docker

* We recommend you set up a log destination. We currently use [Papertrail](https://www.papertrail.com/). If you don't add one, localhost:514 will be used.

* A set of API keys and tokens for Reddit, Imgur, and Twitter.

### Setup

* Clone this repo

* Rename the `.env.template` file to `.env` and fill in the blanks

  * `TOOTBOT_GENERAL_SUBREDDIT_TO_MONITOR`: Name or names of the subreddits to monitor, separated by a plus (`+`). Ex: `test+example`
  
  * `TOOTBOT_GENERAL_DELAY_BETWEEN_POSTS`: Number of seconds to wait between searching for new posts to mirror. Default 900 (15 mins)
  
  * `TOOTBOT_GENERAL_POST_LIMIT`: Number of posts to pull from the front page on each search. Default 10
  
  * `TOOTBOT_GENERAL_NSFW_POSTS_ALLOWED`: Whether to mirror posts marked NSFW. All NSFW posts will be posted with the content warning setting. Default false
  
  * `TOOTBOT_GENERAL_SPOILERS_ALLOWED`: Whether to mirror posts marked spoiler. Default true
  
  * `TOOTBOT_GENERAL_SELF_POSTS_ALLOWED`: Whether to mirror self posts. Default true
  
  * `TOOTBOT_GENERAL_HASHTAGS`: Hashtags to add to every tweet, separated by a comma. Ex: `test,example` produces `Title #test #example redd.it/abcde1 `
  
  * `TOOTBOT_MEDIA_MEDIA_FOLDER`: Name of media folder inside container. Default media
  
  * `TOOTBOT_MEDIA_MEDIA_POSTS_ONLY`: Whether to only mirror posts with media content. Default false
  
  * `TOOTBOT_REDDIT_AGENT`: The Reddit client agent
  
  * `TOOTBOT_REDDIT_CLIENT_SECRET`: The Reddit client secret
  
  * `TOOTBOT_IMGUR_CLIENT`: The Imgur client ID
  
  * `TOOTBOT_IMGUR_CLIENT_SECRET`: The Imgur client secret
  
  * `TOOTBOT_TWITTER_ACCESS_TOKEN`: The Twitter access token
  
  * `TOOTBOT_TWITTER_ACCESS_TOKEN_SECRET`: The Twitter access token secret
  
  * `TOOTBOT_TWITTER_CONSUMER_KEY`: The Twitter consumer key
  
  * `TOOTBOT_TWITTER_CONSUMER_SECRET`: The Twitter consumer secret
  
  * `TOOTBOT_REDIS_HOST`: The Redis host. Default redisdb
  
  * `TOOTBOT_REDIS_PORT`: The Redis port. Default 6379
  
  * `TOOTBOT_REDIS_PASSWORD`: The Redis password. It's advised to change this to a random password. Default password.
  
  * `TOOTBOT_LOG_DESTINATION`: The log destination to send logs to. Default localhost
  
  * `TOOTBOT_LOG_PORT`: The log port of the above destination URL. Default 514
  
* Run `docker compose up`

* Done!

## License

This code is open sourced under the [GPL license v3](LICENSE.txt)
