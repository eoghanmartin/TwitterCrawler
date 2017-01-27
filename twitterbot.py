#!/usr/bin/env python
 
import tweepy, time, sys, json, pdb

filename=open('config.txt','r')
keys=filename.readlines()
filename.close()
 
CONSUMER_KEY = str(keys[1].replace(' ', '')[:-1])
CONSUMER_SECRET = str(keys[3].replace(' ', '')[:-1])
ACCESS_KEY = str(keys[5].replace(' ', '')[:-1])
ACCESS_SECRET = str(keys[7])
pdb.set_trace()

argfile = str(sys.argv[1])

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
 
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        decoded = json.loads(data)
        print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        print ''
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
	l = StdOutListener()

	filename=open(argfile,'r')
	f=filename.readlines()
	filename.close()

	for line in f:
		account_info = api.lookup_users(user_ids=[line])
		for user in account_info:

			f = open('task1.txt', 'w')
			f.write("Screen Name: %s\n" % (str(user.screen_name)))
			f.write("User Name: %s\n" % (str((user.name))))
			f.write("Account Description: %s\n" % str(user.description))
			f.write("Followers Count: %s\n" % (str(user.followers_count)))
			f.write("Statuses Count: %s\n" % (str(user.statuses_count)))
			f.write("Account URL: %s\n\n" % (str(user.url)))
			f.close()

			print "Screen Name: %s" % (user.screen_name)
			print "User Name: %s" % (user.name)
			print "Account Description: %s" % (user.description)
			print "Followers Count: %s" % (str(user.followers_count))
			print "Statuses Count: %s" % (str(user.statuses_count))
			print "Account URL: %s\n" % (str(user.url))
			
			f = open('task2.txt', 'w')
			f.write("Followers for @%s:" % (user.screen_name))
			print "Followers for @%s:" % (user.screen_name)
			for follower in tweepy.Cursor(api.followers, screen_name=user.screen_name, count=200).items():
				print "%s (%s)" % (follower.screen_name.encode('utf-8').strip(), follower.location.encode('utf-8').strip())
				f.write("%s (%s)\n" % (follower.screen_name.encode('utf-8').strip(), follower.location.encode('utf-8').strip()))
			f.write("Friends for @%s:" % (user.screen_name))
			print "\nFriends:"
			for friend in tweepy.Cursor(api.friends, screen_name=user.screen_name, count=200).items():
				f.write("%s (%s)\n" % (friend.screen_name.encode('utf-8').strip(), friend.location.encode('utf-8').strip()))
				print '%s (%s)' % (friend.screen_name.encode('utf-8').strip(), friend.location.encode('utf-8').strip())
			f.close()

		time.sleep(60*10)

	print "\nShowing all new tweets for #programming:"

	stream = tweepy.Stream(auth, l)
	stream.filter(track=['programming'])