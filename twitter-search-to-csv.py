#!/usr/bin/env python

from clint.arguments import Args
from clint.textui import puts, indent
import configparser
import tablib
from TwitterSearch import *

config = configparser.ConfigParser()
config.read('config.ini')
auth = config['TWITTER']
for key in ('API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET'):
    if key not in auth:
        raise Exception(
            'Missing config value "%s", please create config.ini using config.ini.sample. Visit https://apps.twitter.com/' % key)

args = Args().grouped
try:
    SEARCH_SPEC = args['--search']
except KeyError:
    raise Exception('Missing --search parameter, try export.py --search "#something since:2014-01-01 until:2014-02-02"')
RESULT_COUNT = 100

puts(u"Searching for: {0}".format(' '.join(SEARCH_SPEC.all)))
search = TwitterSearch( consumer_key = '', consumer_secret = '', access_token = '', access_token_secret = '' )


tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
tso.set_keywords(SEARCH_SPEC.all)  # let's define all words we would like to have a look for
# tso.setLanguage('en')
tso.set_count(RESULT_COUNT)
tso.set_include_entities(False)

user_fields = ['screen_name', 'utc_offset', 'description', 'location']
tweet_fields = ['created_at', 'text', 'retweet_count', 'favorite_count']

sheet = tablib.Dataset(headers=['id'] + user_fields + tweet_fields)

search.search_tweets_iterable(tso)
queries = 0
puts(u"Fetching results:")
with indent(3):
    try:
        for tweet in search:
            if search.get_statistics()['queries'] != queries:
                puts('Fetched {0} tweets'.format(search.get_statistics()['tweets']))
                queries = search.get_statistics()['queries']
            data = [tweet['id_str']]
            for key in user_fields:
                data.append(tweet['user'][key])
            for key in tweet_fields:
                data.append(tweet[key])
            sheet.append(data)
    except TwitterSearchException as e:  # take care of all those ugly errors if there are some
        print(e)


filename = u'twitter-search-%s.csv' % (' '.join(SEARCH_SPEC.all))
with open(filename, 'wb') as f:
    f.write(sheet.csv)

puts(u"Saved {0} results to {1}".format(sheet.height, filename))
