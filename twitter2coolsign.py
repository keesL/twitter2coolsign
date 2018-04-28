#!/usr/bin/python3
""" Pull the timeline of a collection of twitter users and format it into an RSS feed that can be read by Coolsign digital diplay software.

Requires the python-twitter library:
	https://python-twitter.readthedocs.io/en/latest/#

Created 2018, Kees Leune <kees@leune.org>

"""
import re
import sys
import twitter
import xml.etree.ElementTree as ET
from config import Config
from datetime import datetime


def getAPI():
	""" Retrieve API instance. Information for setting up these keys and secrets can be found at https://python-twitter.readthedocs.io/en/latest/getting_started.html
	"""
	api = twitter.Api(consumer_key		= Config.twitter_consumerKey,
					  consumer_secret	 = Config.twitter_consumerSecret,
					  access_token_key	= Config.twitter_access_token,
					  access_token_secret = Config.twitter_access_token_secret,
                      tweet_mode="extended")
	return api


def cleanup(tweet):
	""" Clean up the tweet so it displays better """

	# remove URLs from tweet body
	tweet=re.sub("http.+([ ]|$)", "", tweet)

	# Ugly way to remove unicode
	tweet = tweet.replace(u"\u2019", "'")
	return tweet.strip()


def addToTimeline(api, twit, timeline):
	""" Build the timeline. Note that if two tweets are sent at exactly 
	the same time, only the last one will show up. This is an acceptable risk.
	"""
	tweets = api.GetUserTimeline(screen_name=twit, count=Config.numTweets)
	for tweet in tweets:
		timeline[tweet.created_at_in_seconds] = {
			'text': cleanup(tweet.full_text),
			'user': '@'+twit.strip()
		}
	return timeline


def formatRSS(timeline):
	""" Format the timeline into a fake-RSS feed. Tweets will 
	appear in reverse chronological order.
	"""

	root=ET.Element('rss')
	root.attrib={'version': '2.0'}
	channel=ET.SubElement(root, 'channel')

	count=0
	for timestamp in sorted(timeline, reverse=True):
		item = ET.SubElement(channel, 'item')

		user = ET.SubElement(item, 'user') 
		user.text = timeline[timestamp]['user']

		tweet = ET.SubElement(item, 'tweet')
		tweet.text = timeline[timestamp]['text']

		when = ET.SubElement(item, 'when') 
		when.text = datetime.fromtimestamp(timestamp).strftime('%c')

		count += 1
		if count == Config.maxPublish:
			break

	return root


def main(outputfile):
	""" Main function; ties everything together """
	timeline = {}
	api = getAPI()

	for user in Config.twits:
		timeline = addToTimeline(api, user, timeline)

	xml = formatRSS(timeline)
	with open(outputfile,'wb') as f:
		f.write(ET.tostring(xml, encoding='us-ascii'))



if __name__ == "__main__":
	""" Make sure we're invoked correctly. """
	if len(sys.argv) < 2:
		sys.stderr.write('Usage: {} outputfile\n'.format(sys.argv[0]))
		sys.exit(1)

	main(sys.argv[1])
