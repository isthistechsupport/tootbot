# Tootbot

This is a Python bot that looks up posts from specified subreddits and automatically posts them on Twitter. It is based on Corbin Davenport's [tootbot](https://github.com/corbindavenport/tootbot). Tootbot is now used by [a wide variety of social media accounts](https://github.com/corbindavenport/tootbot/wiki/Accounts-using-Tootbot).

**Features:**

* Can post to Twitter
* Runs on any PC with Python
* Media from direct links, Gfycat, Imgur, Reddit, and Giphy is automatically attached in the social media post
* Links that do not contain media can be skipped, ideal for meme accounts
* NSFW content, spoilers, and self-posts can be filtered
* Multiple subreddits can be monitored at once

Tootbot uses the [tweepy](https://github.com/tweepy/tweepy), [PRAW](https://praw.readthedocs.io/en/latest/), and [redis-py](https://github.com/andymccurdy/redis-py) libraries, as well as the [TOML configuration language](https://toml.io/en/).

## Disclaimer

The developers of Tootbot hold no liability for what you do with this script or what happens to you by using this script. Abusing this script *can* get you banned from Twitter, so make sure to read up on proper usage of the API.

## Setup and usage

For instructions on setting up and using Tootbot, please visit [the wiki](https://github.com/corbindavenport/tootbot/wiki).

## TODO

* Document how it now uses Redis instead of a CSV.
* Add a CapRover easy deployment option
