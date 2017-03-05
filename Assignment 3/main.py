#!/usr/bin/env python
# coding=utf-8
import sys, json, pdb, os
from EstimationModel import EstModel
from EstimationModel import EstModel

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

	matrix_file = 'SCMatrix_Test1.txt'
	matrix = readSCMatrixFile(matrix_file)
	#writeMatrixToFile(matrix)

	#pdb.set_trace()

	estimation_model = EstModel(matrix)
	estimation_model.MLE()
	estimation_model.checkResults()