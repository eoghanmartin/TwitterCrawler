#!/usr/bin/env python
 
import tweepy, time, sys, json, pdb

#import config file, not included in git repo
filename=open('config.txt','r')
keys=filename.readlines()
filename.close()
 
#Add custom keys here
CONSUMER_KEY = str(keys[1].replace(' ', '')[:-1])
CONSUMER_SECRET = str(keys[3].replace(' ', '')[:-1])
ACCESS_KEY = str(keys[5].replace(' ', '')[:-1])
ACCESS_SECRET = str(keys[7])

#pdb.set_trace()

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

if __name__ == '__main__':
	filename = open("user_IDs.txt",'r')
	ids = filename.readlines()
	filename.close()

	task1 = open('task1.txt', 'w')
	task2 = open('task2.txt', 'w')

	for line in ids:
		account_info = api.lookup_users(user_ids=[line])
		for user in account_info:
			task1.write("Screen Name: %s\n" % (str(user.screen_name)))
			task1.write("User Name: %s\n" % (str((user.name))))
			task1.write("Account Description: %s\n" % str(user.description))
			task1.write("Followers Count: %s\n" % (str(user.followers_count)))
			task1.write("Statuses Count: %s\n" % (str(user.statuses_count)))
			task1.write("Account URL: %s\n\n" % (str(user.url)))

			print "Screen Name: %s" % (user.screen_name)
			print "User Name: %s" % (user.name)
			print "Account Description: %s" % (user.description)
			print "Followers Count: %s" % (str(user.followers_count))
			print "Statuses Count: %s" % (str(user.statuses_count))
			print "Account URL: %s\n" % (str(user.url))
			
			task2.write("Followers for @%s:" % (user.screen_name))
			print "Followers for @%s:\n" % (user.screen_name)
			followers = tweepy.Cursor(api.followers, screen_name=user.screen_name, count=20).pages()
			page = next(followers)
			for follower in page:
				print "%s (%s)" % (follower.screen_name.encode('utf-8').strip(), follower.location.encode('utf-8').strip())
				task2.write("%s (%s)\n" % (follower.screen_name.encode('utf-8').strip(), follower.location.encode('utf-8').strip()))
			task2.write("Friends for @%s:\n" % (user.screen_name))
			print "\nFriends:"
			friends = tweepy.Cursor(api.friends, screen_name=user.screen_name, count=20).pages()
			page = next(friends)
			for friend in page:
				print "%s (%s)" % (friend.screen_name.encode('utf-8').strip(), friend.location.encode('utf-8').strip())
				task2.write("%s (%s)\n" % (friend.screen_name.encode('utf-8').strip(), friend.location.encode('utf-8').strip()))
	task2.close()
	task1.close()

	task3 = open('task3.txt', 'w')

	print "\nWeather keyword:\n"
	task3.write("\nWeather keyword:\n")

	weatherTweets = tweepy.Cursor(api.search, q="weather", count=50).pages()
	page = next(weatherTweets)
	for tweet in page:
		task3.write(tweet.text.encode('utf-8').strip() + "\n\n")
		print tweet.text.encode('utf-8').strip()

	print "\nCoordinates tweets:\n"
	task3.write("\nCoordinates tweets:\n")

	coordinateTweets = tweepy.Cursor(api.search, geocode= "41.63,-86.33,20km", count=50).pages()
	#pdb.set_trace()
	page = next(coordinateTweets)
	for tweet in page:
		#pdb.set_trace()
		task3.write(tweet.text.encode('utf-8').strip() + "\n\n")
		print tweet.text.encode('utf-8').strip()#[-86.33,41.63,-86.20,41.74]
	task3.close()