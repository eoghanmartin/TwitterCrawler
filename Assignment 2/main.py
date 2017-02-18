#!/usr/bin/env python

from __future__ import division
import tweepy, time, sys, json, pdb

#325946633986641920

def removeDuplicates (words_list):
	word_counts = {}
	#initialize dict
	for word in words_list:
		word_counts[word] = 0
	#create dict values
	for word in words_list:
		word_counts[word] += 1
	#delete duplicate words
	for word in word_counts:
		if word_counts[word] > 1:
			i = 0
			for remove_word in words_list:
				if remove_word == word:
					words_list.pop(i)
				i += 1
			words_list.append(word)

	return words_list

def jacardDistance (tweetA, tweetB):
	wordsA = tweetA['text'].split()
	wordsB = tweetB['text'].split()

	wordsA = removeDuplicates(wordsA)
	wordsB = removeDuplicates(wordsB)

	union = len(wordsA) + len(wordsB)
	intersection = 0

	for wordA in wordsA:
		for wordB in wordsB:
			if wordA == wordB:
				intersection += 1

	jacard = float((union - intersection) / union)

	return jacard

class Cluster:
	def __init__(self, seed_id, tweet_json):
		self.ID = seed_id
		self.tweet = tweet_json
		self.tweets = []

if __name__ == '__main__':

	tweets_file=open('Tweets.json','r')
	tweets_txt=tweets_file.readlines()
	tweets_file.close()

	tweets_json = []

	for tweet in tweets_txt:
		tweets_json.append(json.loads(tweet))

	initial_seeds=open('InitialSeeds.txt','r')
	seeds=initial_seeds.readlines()
	initial_seeds.close()

	seed_list = []
	for seed in seeds:
		seed = seed[:-1]
		if ',' in seed:
			seed = seed[:-1]
		seed_list.append(seed)

	num_clusters = len(seed_list)
	clusters = []

	loop_count = 1

	while 1:
		clusters = []
		for seed in seed_list:
			for tweet in tweets_json:
				#pdb.set_trace()
				if str(tweet['id']) == seed:
					clusters.append(Cluster(seed, tweet))

		#initialise cluster objects
		for cluster in clusters:
			cluster.tweets = []

		#fill clusters
		for tweet in tweets_json:
			#set benchmark value for distance to the closest seed for this tweet.
			min_distance = jacardDistance(tweet, clusters[0].tweet)
			if min_distance != 0:
				closest_cluster = 0
			else:
				min_distance = jacardDistance(tweet, clusters[1].tweet)
				closest_cluster = 1
			#iterate through each seed and calculate the distance from this tweet.
			i = 0
			for cluster in clusters:
				distance = jacardDistance(tweet, cluster.tweet)
				if distance < min_distance and distance != 0:
					min_distance = distance
					closest_cluster = i
				i += 1
			#The seed that's closest gets the tweet added to it's cluster.
			clusters[closest_cluster].tweets.append(tweet)


		centroids = []
		#compute centroids
		for cluster in clusters:
			total_distance = 0
			#benchmark distance. Calculate accumulative distance from random tweet to all other tweets in cluster.
			tweets_in_cluster = cluster.tweets
			if len(tweets_in_cluster) > 0:
				tweet = tweets_in_cluster[0]
				for tweet_compare in tweets_in_cluster:
					distance = jacardDistance(tweet, cluster.tweet)
					total_distance += distance
				#benchmark min distance from randiom tweet to compare against.
				min_dist = total_distance
				min_dist_tweet = tweet
				#calculate accumulative distances TO each tweet in cluster FOR each tweet in the cluster.
				for tweet in tweets_in_cluster:
					total_distance = 0
					for tweet_compare in tweets_in_cluster:
						if str(tweet['id']) != str(tweet_compare['id']):
							distance = jacardDistance(tweet, cluster.tweet)
							total_distance += distance
					if total_distance < min_dist:
						min_dist = total_distance
						min_dist_tweet = tweet
				#The tweet with the lowest accumulative distance is considered the new centroid.
				centroids.append(str(min_dist_tweet['id']))
			else:
				centroids.append(str(cluster.tweet['id']))

		#pdb.set_trace()

		#compare centroids with seeds_list
		seed_count = 0
		for seed in seed_list:
			if seed in centroids:
				seed_count += 1
		#if they are the same, we're done.
		if seed_count >= 25:
			print "Completed in " + str(loop_count) + " loops."
			break
		#set seed_list to list of new centroids and compute clusters and centroids again.
		else:
			seed_list = centroids
			loop_count += 1
			print str(loop_count)

	clusters_file=open('clusters.json','w')
	for cluster in clusters:
		tweet_ids = []
		for tweet in cluster.tweets:
			tweet_ids.append(str(tweet['id']))
		cluster_json = {'cluster_id': str(cluster.tweet['id']), 'tweet_ids': tweet_ids}
		clusters_file.write(json.dumps(cluster_json))
		clusters_file.write('\n')
	clusters_file.close()