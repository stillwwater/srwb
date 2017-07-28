#!/usr/bin/env python

"""
This script reads comments from the top n posts from a subreddit
and collects the frequency in which words are used.

Run the script by passing it the following arguments:
> srwb.py [username] [subreddit] [# of posts]

[username]   - Your reddit username (required to request data from the API)
[subreddit]  - The subreddit you wish to gather data from
[# of posts] - How many posts to analyze
"""

import json
import re
import requests
import sys
import threading
import time
import tqdm

from os import path

OUTPUT = "word_data.csv"


def safe_file_name(file):
    i = 1
    while path.isfile(file):
        f, ext = path.splitext(file)
        file = "%s (%i)%s" % (re.sub(r"\s\(\d+\)$", "", f), i, ext)
        i += 1
    return file


class WordBot:

    VERSION = 1.0

    def __init__(self, subreddit, user):
        self.client = WordBot.login(user)
        self.subreddit = subreddit
        self.all_words = {}
        self.lock = threading.Lock()
        self.results = {"tcomments": 0, "terrors": 0, "twords": 0}

    @staticmethod
    def login(user_name):
        client = requests.session()
        client.user = user_name

        return client

    def get_top_posts(self, n, after="null", links=[]):
        """ Get the top n posts from the subreddit """
        string = "/r/%s/top.json" % self.subreddit

        js = self.download_json(
            string, sort="top", t="all", limit=100, after=after)

        # Permalink for each child (post)
        [links.append(x["data"]["permalink"]) for x in js["data"]["children"]]

        print("\raquiring permalinks %i%%" %
              (len(links) / n * 100), end="")

        # Recurse until we have enough links
        if len(links) >= n:
            return links
        else:
            after = js["data"]["after"]
            return self.get_top_posts(n, after, links)

    def read_posts(self, posts):
        print("\ndownloading posts...")
        i = 0

        for p in tqdm.tqdm(posts):
            i += 1

            js = self.download_json("%s.json" % p)
            # js[0]: Post
            # js[1]: Comments
            if len(js) > 1:
                t = threading.Thread(
                    target=self.read_replies,
                    args=(js[1]["data"]["children"],))
                t.start()
                t.join()

        print("\nFinished executing %i threads..." % len(posts))

    def to_csv(self, fname):
        with open(fname, mode="a") as f:
            f.write("word,freq\n")
            [f.write("%s,%i\n" % (k, v)) for k, v in self.all_words.items()]

    def print_results(self):
        tc = self.results["tcomments"]
        te = self.results["terrors"]
        tw = self.results["twords"]

        print("total: %i comments, errors: %i (%i%% successfull)" %
              (tc, te, (tc - te) / tc * 100))

        print("words: %i (unique: %i)" % (tw, len(self.all_words.keys())))

    # --------------------------------

    def download_json(self, string, **kwargs):
        """ Download json from url """
        url = "https://reddit.com%s" % string

        header = {"user-agent": "/u/%s running a harmless data-viz bot" %
                  self.client.user}

        r = self.client.get(url, params=kwargs, headers=header)

        try:
            return json.loads(r.text)
        except json.decoder.JSONDecodeError:
            # :(
            print("\nAPI Timeout:")

            # Sleep for 5 seconds and hopefully we get another chance
            for i in reversed(range(1, 6)):
                print("\rwaiting %is" % i, end="")
                time.sleep(1)

            print("\rretrying...")
            return self.download_json(string, kwargs=kwargs)

    def read_replies(self, children):
        for c in children:
            self.lock.acquire()
            try:
                # Count words in the comment
                self.count(c["data"]["body"])
            except KeyError:
                # There is a bug (I think) in the reddit API where the API
                # will return bad data when searching through
                # 'deeply' nested comments...
                # That's why this try except block is here
                self.count(None)
                continue
            finally:
                self.lock.release()

            # Does the comment have any replies?
            replies = c["data"]["replies"]
            if replies != "":
                self.read_replies(replies["data"]["children"])

    def count(self, text):
        self.results["tcomments"] += 1

        if text is None:
            self.results["terrors"] += 1
            return

        words = re.compile(r"[a-zA-Z]+").findall(text)

        for w in words:
            w = w.lower()
            self.results["twords"] += 1

            if w in self.all_words.keys():
                self.all_words[w] += 1
                continue

            # New unique word.
            self.all_words[w] = 1


# ------------------------------------

# PART 1
# -> Go through posts from top-alltime in blocks of 100
# -> Get the permalink for each post
# -> Pass the "after" value to the next request to get the next page
#
# PART 2
# -> Get json data for each permalink
# -> Read "body" for each comment reply until there are none left
# -> Separate the body text into words and store the uniques in memory

def main(args):
    print("\nsubreddit word bot v%.1f by stillwwater\n" % WordBot.VERSION)

    if len(args) != 3:
        print(__doc__)
        sys.exit(1)

    user, subreddit, n = args
    n = int(n)

    bot = WordBot(subreddit, user)
    print("/r/%s:" % subreddit)

    posts = bot.get_top_posts(n if n % 100 == 0 else n + 100 - n % 100)
    bot.read_posts(posts)
    bot.print_results()
    out = safe_file_name(OUTPUT)
    bot.to_csv(out)

    print("\ndone, output saved to '%s'" % out)


if __name__ == "__main__":
    main(sys.argv[1:] if __file__ in sys.argv else sys.argv)
