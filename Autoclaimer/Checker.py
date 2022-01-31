import pycurl, requests, datetime

from time import sleep
from threading import Thread, Lock, active_count
from random import choice, randint
from requests import patch
from colorama import Fore, init
from discord_webhook import DiscordWebhook, DiscordEmbed

init()
magenta = Fore.MAGENTA
green = Fore.GREEN
white = Fore.WHITE
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
cyan = Fore.CYAN
spinners = ["/", "-", "\\", "|"]

accounts = [i.strip() for i in open("Settings\\Targets.txt") if i]

class static(object):
    def __init__(self):
        super(static, self).__init__()
        self.attempts, self.rs, self.count, self.rl = 0, 0, 0, 0
        self.started = True
        self.user_list = []

    def discord_webhook(self, username):
        webhook = DiscordWebhook(url="WEBHOOK URL HERE")
        embed = DiscordEmbed(
            title="Claimed!",
            color=randint(1, 16777215),
            url="https://www.twitter.com/%s/" % username
        )
        embed.set_thumbnail(url="https://i.pinimg.com/originals/bd/96/f8/bd96f89f997c140392a922f1dd5349b5.png")
        embed.set_description("@" + username)
        webhook.add_embed(embed)
        webhook.execute()

class autoclaimer(Thread):
    def __init__(self, twitter):
        super(autoclaimer, self).__init__()
        self.twitter = twitter
        self.started = True

    def twitter_connection(self):
        try:
            self._conn = pycurl.Curl()
            self._conn.setopt(pycurl.ENCODING, 'gzip')
            self._conn.setopt(pycurl.SSL_VERIFYPEER, 0)
            self._conn.setopt(pycurl.SSL_VERIFYHOST, 0)
            self._conn.setopt(pycurl.TIMEOUT, 1)
            return self._conn
        except: pass

    def twitter_resp(self, url, username, data, headers):
        try:
            if data:
                self._conn.setopt(pycurl.POSTFIELDS, data)

            self._conn.setopt(pycurl.URL, url)
            self._conn.setopt(pycurl.HTTPHEADER, headers)
            self._conn.perform_rs()
            code = self._conn.getinfo(pycurl.RESPONSE_CODE)
            return code, username

        except:
            self._conn.close()
            self.twitter_connection()
            pass

    def run(self):
        sleep(0.3)
        self.twitter_connection()
        while self.twitter.started:
            try:
                username = choice(accounts)
                resp, user = self.twitter_resp('https://pop-api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=1&max_id=0' % username, username, data=None, headers=["X-CSRF-Token: 83368f29e6d092aacef9e4b10b0185ab",
                "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA", "User-Agent: Mozilla/5.0"])

                if resp == 404:
                    Lock().acquire()
                    cc, _ = self.twitter_resp("https://pop-api.twitter.com/1.1/account/settings.json", None, data="screen_name=%s" % user, headers=["X-CSRF-Token: 83368f29e6d092aacef9e4b10b0185ab",
                    "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA", "User-Agent: Mozilla/5.0", "Cookie: auth_token=%s; ct0=83368f29e6d092aacef9e4b10b0185ab" % self.twitter.authtoken])

                    if cc == 200:
                        self.twitter.discord_webhook(user)
                        print("\n\n[Reply] Claimed: @%s %s      " % (username, " " * 10))
                        self.twitter.started = False
                        exit(0)
                    
                    if resp == 429:
                        self.twitter.rl += 1

                    else:
                        print("\n\n[Reply] Missed: %s %s       " % (user, cc, " " * 10))
                        accounts.remove(user)
                        sleep(3)
                        Lock().release()

                else: self.twitter.attempts += 1
            except: pass

class rs_counter(Thread):
    def __init__(self, twitter):
        super(rs_counter, self).__init__()
        self.twitter = twitter

    def run(self):
        while True:
            before = self.twitter.attempts
            sleep(1)
            self.twitter.rs = self.twitter.attempts - before

class updateStats(Thread):
    def __init__(self, twitter):
        super(updateStats, self).__init__()
        self.twitter = twitter

def getInput(prompt):
        print(prompt, end="")
        return input()

def main():
    try:
        print('[Title] Twitter Autoclaimer | Version: 1.0\n')
        request = static()
        request.authtoken = getInput('[Input] Auth Token: ')
        for _ in range(int(getInput('[Input] Threads: '))):

            trd = autoclaimer(request)
            trd.setDaemon(True)
            trd.start()

        rs = rs_counter(request)
        rs.setDaemon(True)
        rs.start()

        us = updateStats(request)
        us.setDaemon(True)
        us.start()
        print()

        while request.started:
            try:
                print("[Stats] Requests: {:,} | R/s: {:,} | RL/s: {:,} ".format(request.attempts, request.rs, request.rl), end='\r', flush=True)

            except KeyboardInterrupt:
                print("\n\n[Reply] Exited... %s" % (" " * 35))
                request.started = False
                exit(0)
    except: pass

main()
