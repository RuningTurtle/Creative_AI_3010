import praw
import pdb
import re
import os
import random
from creative_ai.reddit.wavLinks import *
from prawcore import NotFound

def test_sub_exists(sub):
    # Tests if a sub-reddit exists or not
    reddit = praw.Reddit('garden_music_bot')
    exists_status = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists_status = False
    return exists_status

def reddit_write():
    # Writes message and gets sub-reddit input
    print('\nOur bot randomly selects previously generated video game music and comments on posts that include the word "music".')
    print("**Limited to 1 post every 10 minutes by Reddit post frequency rules**")
    sub_reddit_entry = input("Please enter a SubReddit you would like our bot to post a comment in: ")
    reddit = praw.Reddit('garden_music_bot')

    # Determines if post has already been commented on
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Keeps calling for valid sub-reddit input until one is given
    sub_reddit = sub_reddit_entry
    while not test_sub_exists(sub_reddit):
        print("Invalid SubReddit")
        sub_reddit = input("Try again: ")

    # Posts random song with message to post on entered subreddit
    subreddit = reddit.subreddit(sub_reddit)
    for submission in subreddit.hot(limit=100):
        if submission.id not in posts_replied_to:
            if re.search("music", submission.title, re.IGNORECASE):
                path = 'C:\\EECS_Projects/Creative_AI_3010_Repository/creative_ai/wav'
                submission.reply("Speaking of music, what do you think of this new song that I made?\n"
                 + random.choice(links))
                print("Bot replying to : ", submission.title)
                posts_replied_to.append(submission.id)
                break

    # Writes post id to txt file to keep track of comments
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
