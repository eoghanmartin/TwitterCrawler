#!/usr/bin/env python
# coding=utf-8

from __future__ import division
import tweepy, time, sys, json, pdb, os

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

class EstModel():
	def __init__(self, matrix):
		self.matrix = matrix
		self.count_sources = len(matrix)
		self.count_measured_variables = self.getAmountMeasuredVars()
		self.a = self.initAi()
		self.b = self.initBi()
		self.d = 0.5 # Algorithm line 1
		self.Z = dict.fromkeys(range(1,self.count_measured_variables+2)) # Computed values from equation 11
		self.H = dict.fromkeys(range(1,self.count_measured_variables+2)) # Optimal decision vector converged from Z(t,j)
		self.E = dict.fromkeys(self.matrix.keys()) # Optimal estimation vector of source reliability

	def getAmountMeasuredVars(self):
		max_val = 0
		for source_id in self.matrix:
			if self.matrix[source_id] > max_val:
				max_val = self.matrix[source_id]
		return max_val

	def calcSi(self, i):
		# num reports from si / total num of measured variables
		return len(self.matrix[i]) / float(self.count_measured_variables)

	def initAi(self):
		# Algorithm line 1; ai = si
		a = {}
		for i in self.matrix.keys():
			a[i] = self.calcSi(i)
		return a

	def initBi(self):
		# Algorithm line 1; bi = si * 0.5
		b = {}
		for i in self.matrix.keys():
			b[i] = self.calcSi(i) * 0.5
		return b

	def calcNextAi(self, s):
		# Equation 17
		numerator = sum([self.Z[j] for j in self.Z if j in self.matrix[s]])
		denominator = sum(self.Z.values())
		return numerator / float(denominator)

	def calcNextBi(self, s):
		# Equation 17
		Ki = len(self.matrix[s])
		N = self.count_measured_variables
		numerator = sum([self.Z[j] for j in self.Z if j in self.matrix[s]])
		denominator = sum(self.Z.values())
		return (Ki - numerator) / float(N - denominator)

	def calcNextDi(self, s):
		# Equation 17
		numerator = sum(self.Z.values())
		return numerator / float(self.count_measured_variables)

	def calcA(self, j):
		# Equation 12
		# Conditional probability regarding observations about the jth measured variable
		# and current estimation of the parameter theta given the jth measured variable
		# is true
		PI = 1
		for i in self.matrix:
			if j in self.matrix[i]:
				PI *= self.a[i]
			else:
				PI *= (1-self.a[i])
		return PI

	def calcB(self, j):
		# Equation 12
		# Conditional probability regarding observations about the jth measured variable
		# and current estimation of the parameter theta given the jth measured variable
		# is false
		PI = 1
		for i in self.matrix:
			if j in self.matrix[i]:
				PI *= self.b[i]
			else:
				PI *= (1-self.b[i])
		return PI

	def calcZ(self, j):
		# Equation 11
		numerator = self.calcA(j) * self.d
		denominator = self.calcA(j) * self.d + self.calcB(j) * (1 - self.d)
		return numerator / float(denominator)

	def calcSourceReliability(self, s):
		# Equation 5
		return self.a[s] * self.d / float(self.calcSi(s))

	def expectationMaximization(self):
		t = 0
		while t < 20:
			# Expectation step: Compute the expected log likelihood function where the expectation is taken with respect
			# to the computed conditional distribution of the latent variables given the current settings and observed data. 

			# Algorithm lines 3 - 5
			for j in self.Z:
				self.Z[j] = self.calcZ(j)

			# Maximization step: Find the parameters that maximize the Q function in the E-step to be used as the estimate
			# of theta for the next iteration.

			# Algorithm lines 6 - 10
			for i in self.matrix:
				self.a[i] = self.calcNextAi(i)
				self.b[i] = self.calcNextBi(i)
				self.d = self.calcNextDi(i)
			t += 1

		# Algorithm lines 15 - 21
		for j in self.Z:
			if self.Z[j] >= 0.5:
				self.H[j] = 1
			else:
				self.H[j] = 0

		# Algorithm lines 22 - 24
		for i in self.matrix:
			self.E[i] = self.calcSourceReliability(i)

if __name__ == '__main__':

	matrix_file = 'SCMatrix_Test1.txt'
	matrix = readSCMatrixFile(matrix_file)
	matrix_CSVfile=open('matrix.csv','w')
	#Writing matrix to CSV file
	#for source_id in matrix:
	#	matrix_CSVfile.write(str(source_id)+',')
	#	for idx, val in enumerate(matrix[source_id]):
	#		matrix_CSVfile.write(str(idx) + ':' + str(val) + ',')
	#	matrix_CSVfile.write("\r\n")
	#matrix_CSVfile.close()

	td = EstModel(matrix)
	td.expectationMaximization()
	#td.verifyTruth()

	###ALGORITHM
	#Initialize theta (ai = si, bi = 0.5 × si, d = Random number in (0, 1) )
	#while theta(t) does not converge do
	#	for j = 1 : N do
	#		compute Z(t, j) based on Equation (11)
	#	end for
	#	theta(t+1) = theta(t)
	#	for i = 1 : M do
	#		compute a(t+1)i, b(t+1)i, d(t+1) based on Equation (17)
	#		update a(t)i, b(t)i, d(t) with a(t+1)i, b(t+1)i, d(t+1) in theta(t+1)
	#	end for
	#	t = t + 1
	#end while
	#Let Z(c)j = converged value of Z(t, j)
	#Let a(c)i = converged value of a(t)i; b(c)i = converged value of b(t)i; d(c) = converged value of d(t)
	#for j = 1 : N do
	#	if Z(c)j ≥ 0.5 then
	#		hj is true
	#	else
	#		hj is false
	#	end if
	#end for
	#for i = 1 : M do
	#	calculate ei from a(c)i, b(c)i and d(c) based on Equation (5)
	#end for
	#Return the computed optimal estimates of measured variables Cj = hj and source reliability ei