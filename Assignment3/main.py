#!/usr/bin/env python
# coding=utf-8

import sys, json, pdb, os

sys.path.append('../Assignment2/')
from EstimationModel import EstModel
from KMeansClustering import KMeans

def readSCMatrixFile(filename):
	matrix_file=open(filename,'r')
	matrix_lines=matrix_file.readlines()
	matrix = {}
	for line in matrix_lines:
		source_id, measured_variable_id = [int(x) for x in line.split(',')]
		if source_id not in matrix:
			matrix[source_id] = {}
		matrix[source_id][measured_variable_id] = 1
	matrix_file.close()
	return matrix

def writeMatrixToFile(matrix):
	matrix_CSVfile=open('matrix.csv','w')
	matrix_CSVfile.write("Source ID, Claims...\n")
	for source_id in matrix:
		matrix_CSVfile.write(str(source_id)+',')
		for claim in matrix[source_id]:
			matrix_CSVfile.write(str(claim) + ',')
		matrix_CSVfile.write("\n")
	matrix_CSVfile.close()

if __name__ == '__main__':

	### TASK 1 ###

	matrix_file = 'SCMatrix_Submit.txt'
	matrix = readSCMatrixFile(matrix_file)
	#writeMatrixToFile(matrix)

	estimation_model_using_SCMatrixFile = EstModel(matrix)
	estimation_model_using_SCMatrixFile.MLE()
	# Used for test data with ground truths
	#estimation_model_using_SCMatrixFile.checkResults('GroundTruth_File.txt')
	estimation_model_using_SCMatrixFile.writeResultsTask1('ResultsTask1.txt')

	### TASK 2 ###

	k_means = KMeans('../Assignment2/InitialSeeds.txt', '../Assignment2/Tweets.json')
	k_means.generateClusters()
	k_means.writeClustersToFile('../Assignment2/clusters.json')
	k_means.checkResults('../Assignment2/CorrectClusteringResults.txt')

	clusters_matrix = k_means.generateMatrixFromClusters()
	#writeMatrixToFile(clusters_matrix)
	estimation_model_using_twitter_data = EstModel(clusters_matrix)
	estimation_model_using_twitter_data.MLE()
	estimation_model_using_twitter_data.writeResultsTask2('ResultsTask2.txt')