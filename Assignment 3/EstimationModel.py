#!/usr/bin/env python
# coding=utf-8

from __future__ import division
import sys, json, pdb, os, random

class EstModel():
	def __init__(self, matrix):
		self.matrix = matrix

		self.sources_total = len(matrix)
		self.measured_variables_total = self.getAmountMeasuredVars()
		#Initialize theta (ai = si, bi = 0.5 × si, d = Random number in (0, 1) )
		self.ai = {}
		for source in self.matrix:
			self.ai[source] = self.si(source)
		self.bi = {}
		for source in self.matrix:
			self.bi[source] = self.si(source) * 0.5
		self.d = random.uniform(0, 1)

		self.Z = dict.fromkeys(range(1,self.measured_variables_total+2)) # Latent variables. Z determines probability of variable truth.
		
		self.h = dict.fromkeys(range(1,self.measured_variables_total+2)) # Computed claim truths (1 or 0 associated with claims)
		self.E = dict.fromkeys(self.matrix.keys()) # Source reliability dictionary

	def getAmountMeasuredVars(self):
		max_val = 0
		for source_id in self.matrix:
			if self.matrix[source_id] > max_val:
				max_val = max(self.matrix[source_id])
		return max_val - 1

	def si(self, source):
		# si = all claims by source divided by total claims
		return len(self.matrix[source]) / float(self.measured_variables_total)

	def Atj(self, j):
		prob_of_truth_when_true = 1
		for source in self.matrix:
			# if claim j is true according to source
			if j in self.matrix[source]:
				# probability of truth is multiplied by the reliability of source
				prob_of_truth_when_true = prob_of_truth_when_true * self.ai[source]
			else:
				prob_of_truth_when_true = prob_of_truth_when_true * (1-self.ai[source])
		return prob_of_truth_when_true

	def Btj(self, j):
		prob_of_truth_when_false = 1
		for i in self.matrix:
			if j in self.matrix[i]:
				prob_of_truth_when_false = prob_of_truth_when_false * self.bi[i]
			else:
				prob_of_truth_when_false = prob_of_truth_when_false * (1-self.bi[i])
		return prob_of_truth_when_false

	def Ztj(self, j):
		# Equation 11
		numerator = self.Atj(j) * self.d
		denominator = self.Atj(j) * self.d + self.Btj(j) * (1 - self.d)
		return numerator / float(denominator)

	def aiTPlusOne(self, source):
		# This is the new probability that source will report a claim to be true when it is true
		list_of_j_in_Z = []
		for claim in self.Z:
			if claim in self.matrix[source]:
				list_of_j_in_Z.append(self.Z[claim])
		sum_true_claim_probs_made_by_source = sum(list_of_j_in_Z)
		sum_all_true_claim_probs = sum(self.Z.values())
		source_prob_to_be_right = sum_true_claim_probs_made_by_source / float(sum_all_true_claim_probs)
		return source_prob_to_be_right

	def biTPlusOne(self, source):
		# This is the new probability that source will report a claim to be true when it is false
		Ki = len(self.matrix[source]) # Number of measured variables observed by the source
		N = self.measured_variables_total # Total number of measured variables
		list_of_j_in_Z = []
		for claim in self.Z:
			if claim in self.matrix[source]:
				list_of_j_in_Z.append(self.Z[claim])
		sum_true_claim_probs_made_by_source = sum(list_of_j_in_Z)
		sum_all_true_claim_probs = sum(self.Z.values())
		source_prob_to_be_wrong = (Ki - sum_true_claim_probs_made_by_source) / float(N - sum_all_true_claim_probs)
		return source_prob_to_be_wrong

	def MLE(self):
		t = 0
#		while theta(t) does not converge do
		for t in range(0,20):
			# E Step
			# Calculate probabilities of claims being true.
			# Will be very low on first couple of iterations as the source reliabilities are initialized very low.
#			for j = 1 : N do
#				compute Z(t, j) based on Equation (11)
			for claim in self.Z:
				self.Z[claim] = self.Ztj(claim)
#			end for
			# M Step
			# Update source reliabilities (ai and bi) based off of new Z values.
#			for i = 1 : M do
#				compute a(t+1)i, b(t+1)i, d(t+1) based on Equation (17)
#				update a(t)i, b(t)i, d(t) with a(t+1)i, b(t+1)i, d(t+1) in theta(t+1)
			for source in self.matrix:
				self.ai[source] = self.aiTPlusOne(source)
				self.bi[source] = self.biTPlusOne(source)
				self.d = sum(self.Z.values()) / float(self.measured_variables_total)
#			end for
			#t = t + 1
#		end while
#		for j = 1 : N do
#			if Z(c)j ≥ 0.5 then
#				hj is true
#			else
#				hj is false
#			end if
		for claim in self.Z:
			if self.Z[claim] >= 0.5:
				self.h[claim] = 1
			else:
				self.h[claim] = 0
#		end for
#		for i = 1 : M do
#			calculate ei from a(c)i, b(c)i and d(c) based on Equation (5)
		for source in self.matrix:
			self.E[source] = self.ai[source] * self.d / float(self.si(source))
#		end for

	def checkResults(self):
		truths = {}
		f = open('GroundTruth_File.txt', 'r')
		for line in f:
			measured_var_id = line.split(',')[0]
			truth = line.split(',')[1]
			truths[int(measured_var_id)] = int(truth)
		f.close()
		perfect = 1
		for truth in truths:
			if truths[truth] != self.h[truth]:
				print 'Incorrect - Truth: ' + str(truth) + ' Measured Variable ID: ' + str(truths[truth]) + ' Calculated Truth: ' + str(self.h[truth])
				perfect = 0
		if perfect == 0:
			print "\nAlgorithm has a problem."
		else:
			print "\nAll good."
			results_file = open('results.txt', 'w')
			for truth in self.h:
				results_file.write(str(truth) + ',' + str(self.h[truth]) + '\n')
			results_file.close()

	###	ALGORITHM ###

	#si = all claims by source divided by total claims

	#Initialize theta (ai = si, bi = 0.5 × si, d = Random number in (0, 1) )

	#while theta(t) does not converge do

	#	for j = 1 : N do
	#		compute Z(t, j) based on Equation (11)
	#	end for

	#	theta(t+1) = theta(t) ...?

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