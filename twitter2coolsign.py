#!/usr/bin/python3
import sys
import twitter
import xml.etree.ElementTree as ET
from config import Config
from datetime import datetime


def getAPI():
	api = twitter.Api(consumer_key        = Config.twitter_consumerKey,
	                  consumer_secret     = Config.twitter_consumerSecret,
	                  access_token_key    = Config.twitter_access_token,
	                  access_token_secret = Config.twitter_access_token_secret)
	return api


def addToTimeline(api, twit, timeline):
	""" Build the timeline. Note that if two tweets are sent at exactly 
    the same time, only the last one will show up. This is an acceptable risk
	"""
	tweets = api.GetUserTimeline(screen_name=twit, count=Config.numTweets)
	for tweet in tweets:
		timeline[tweet.created_at_in_seconds] = {
			'text': tweet.text,
			'user': twit
		}
	return timeline


def formatRSS(timeline):
	""" Format the timeline into a fake-RSS feed. Tweets will 
    appear in reverse chronological order.
    """

	root=ET.Element('rss')
	root.attrib={'version': '2.0'}
	channel=ET.SubElement(root, 'channel')

	for timestamp in sorted(timeline, reverse=True):
		item = ET.SubElement(channel, 'item')

		user = ET.SubElement(item, 'user') 
		user.text = timeline[timestamp]['user']

		tweet = ET.SubElement(item, 'tweet')
		tweet.text = timeline[timestamp]['text']

		when = ET.SubElement(item, 'when') 
		when.text = datetime.fromtimestamp(timestamp).strftime('%c')

	return root


def main(outputfile):
	timeline = {}
	api = getAPI()

	for user in Config.twits:
		timeline = addToTimeline(api, user, timeline)

	xml = formatRSS(timeline)
	with open(outputfile,'wb') as f:
		f.write(ET.tostring(xml, encoding='us-ascii'))



if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: {} outputfile\n'.format(sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1])
