#!/usr/bin/env python

from KMeansClustering import KMeans

if __name__ == '__main__':
	k_means = KMeans('InitialSeeds.txt', 'Tweets.json')
	k_means.generateClusters()
	k_means.writeClustersToFile('clusters.json')
	k_means.checkResults('CorrectClusteringResults.txt')