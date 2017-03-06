#!/usr/bin/env python

from __future__ import division
import tweepy, time, sys, json, pdb

def removeDuplicates (words_list):
	list_copy = []
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
			for remove_word in words_list:
				if remove_word == word:
					words_list.remove(word)
			words_list.append(word)

	return words_list

class KMeans:
	def __init__(self, initial_seeds_filename, tweets_filename):
		self.seed_list = self.initSeedList(initial_seeds_filename)
		self.tweets = self.loadTweets(tweets_filename)
		self.clusters = self.initClusters()
		self.num_clusters = len(self.seed_list)

	def loadTweets(self, tweets_filename):
		tweets = []
		tweets_file=open(tweets_filename,'r')
		tweets_txt = tweets_file.readlines()
		tweets_file.close()
		for tweet in tweets_txt:
			tweets.append(json.loads(tweet))
		return tweets

	def initSeedList(self, seeds_file):
		seed_list = []
		initial_seeds=open(seeds_file,'r')
		seed_list_txt=initial_seeds.readlines()
		initial_seeds.close()

		for seed in seed_list_txt:
			seed_list.append(seed.split(',')[0].strip('\n'))
		return seed_list

	def jacardDistance (self, tweetA, tweetB):
		wordsA = tweetA['text'].split()
		wordsB = tweetB['text'].split()
		allWords = list(wordsA)
		allWords.extend(wordsB)

		allWords = removeDuplicates(allWords) #list(set(allWords)) doesn't seem to work here...
		wordsA = list(set(wordsA))
		wordsB = list(set(wordsB))

		union = len(allWords)
		intersection = 0

		for wordA in wordsA:
			if wordA in wordsB:
				intersection += 1

		jacard = float((union - intersection) / union)

		return jacard

	def checkResults(self, results_filename):
		correct_results = open(results_filename, 'r')
		ground_results = []
		for line in correct_results:
			ground_results.append(line.split(':')[1].strip('\n').split(','))
		correct_results.close()
		perfect = 1
		for cluster in self.clusters:
			tweet_ids = []
			for tweet in cluster.tweets:
				tweet_ids.append(str(tweet['id']))
			if tweet_ids not in ground_results:
				print '\nIncorrect - Cluster: ' + str(cluster.centroid) + ' is incorrect.'
				perfect = 0
		if perfect == 0:
			print "\nAlgorithm has a problem."
		else:
			print "\nResults match the results in " + results_filename + " for K-Means clustering."

	def initClusters(self):
		clusters = []
		for seed in self.seed_list:
			for tweet in self.tweets:
				if str(tweet['id']) == seed:
					clusters.append(Cluster(seed, tweet))
		for cluster in clusters:
			cluster.tweets = []
		return clusters

	def computeCentroids(self):
		centroids = []
		#compute centroids
		for cluster in self.clusters:
			total_distance = 0
			#benchmark distance. Calculate accumulative distance from random tweet to all other tweets in cluster.
			tweets_in_cluster = cluster.tweets
			if len(tweets_in_cluster) > 0:
				tweet = tweets_in_cluster[0]
				for tweet_compare in tweets_in_cluster:
					distance = self.jacardDistance(tweet, cluster.tweet)
					total_distance += distance
				#benchmark min distance from randiom tweet to compare against.
				min_dist = total_distance
				min_dist_tweet = tweet
				#calculate accumulative distances TO each tweet in cluster FOR each tweet in the cluster.
				for tweet in tweets_in_cluster:
					total_distance = 0
					for tweet_compare in tweets_in_cluster:
						distance = self.jacardDistance(tweet, cluster.tweet)
						total_distance += distance
					if total_distance < min_dist:
						min_dist = total_distance
						min_dist_tweet = tweet
				#The tweet with the lowest accumulative distance is considered the new centroid.
				centroids.append(str(min_dist_tweet['id']))
			else:
				centroids.append(str(cluster.tweet['id']))
		return centroids

	def generateClusters(self):
		while 1:
			self.clusters = self.initClusters()
			#fill clusters
			for tweet in self.tweets:
				#set benchmark value for distance to the closest seed for this tweet.
				min_distance = self.jacardDistance(tweet, self.clusters[0].tweet)
				closest_cluster = 0
				#iterate through each seed and calculate the distance from this tweet.
				i = 0
				for cluster in self.clusters:
					distance = self.jacardDistance(tweet, cluster.tweet)
					if distance < min_distance and distance != 0:
						min_distance = distance
						closest_cluster = i
					i += 1
				#The seed that's closest gets the tweet added to it's cluster.
				self.clusters[closest_cluster].tweets.append(tweet)
			
			centroids = self.computeCentroids()
			#compare centroids with seeds_list
			seed_count = 0
			for seed in self.seed_list:
				if seed in centroids:
					seed_count += 1
			#if they are the same, we're done.
			if seed_count == self.num_clusters:
				i = 1
				for cluster in self.clusters:
					cluster.ID = i
					i += 1
				print "\nK-Means clustering complete."
				break
			else:
				#set seed_list to list of new centroids and compute clusters and centroids again.
				self.seed_list = centroids

	def writeClustersToFile(self, clusters_filename):
		clusters_file=open(clusters_filename,'w')
		for cluster in self.clusters:
			tweet_ids = []
			for tweet in cluster.tweets:
				tweet_ids.append(str(tweet['id']))
			cluster_json = {'cluster_id': str(cluster.ID), 'tweet_ids': tweet_ids}
			clusters_file.write(json.dumps(cluster_json))
			clusters_file.write('\n')
		clusters_file.close()

	def generateMatrixFromClusters(self):
		matrix = {}
		for cluster in self.clusters:
			for tweet in cluster.tweets:
				twitter_user = self.getTwitterUserFromTweetId(str(tweet['id']))
				if twitter_user == 0:
					break
				if twitter_user not in matrix:
					matrix[str(twitter_user)] = self.getClaimsMadeByTwitterUser(twitter_user)
		return matrix

	def getTwitterUserFromTweetId(self, tweet_id):
		for tweet in self.tweets:
			if str(tweet['id']) == tweet_id:
				return str(tweet['from_user_id'])
		return 0

	def getClaimsMadeByTwitterUser(self, twitter_user):
		claims = []
		for cluster in self.clusters:
			for tweet in cluster.tweets:
				if twitter_user == str(tweet['from_user_id']):
					claims.append(cluster.ID)
		return claims

class Cluster:
	def __init__(self, seed_id, tweet_json):
		self.centroid = seed_id
		self.tweet = tweet_json
		self.tweets = []
		self.ID = 0