from __future__ import division
import numpy as np
from sklearn import datasets
import sys, os, math
# Import helper functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../")
from helper_functions import calculate_entropy, divide_on_feature, train_test_split, accuracy_score, get_random_subsets, normalize
sys.path.insert(0, dir_path + "/../unsupervised_learning/")
from principal_component_analysis import PCA

from decision_tree import DecisionTree

from sklearn.ensemble import RandomForestClassifier


class RandomForest():
	def __init__(self, n_estimators=50, max_features=None):
		self.n_estimators = n_estimators	# Number of trees
		self.max_features = max_features 	# Maxmimum number of features per tree
		self.feature_indices = []			# The indices of the features used for each tree

		# Initialize decision trees
		self.trees = []
		for _ in range(n_estimators):
			self.trees.append(DecisionTree())


	def fit(self, X, y):
		n_features = np.shape(X)[1]
		# If max_features have not been defined => select it as sqrt(n_features)
		if not self.max_features:
			self.max_features = int(math.sqrt(n_features))

		# Choose one random subset of the data for each tree
		subsets = get_random_subsets(X, y, self.n_estimators)
		for i in range(self.n_estimators):
			X_subset, y_subset = subsets[i]
			# Feature bagging (select random subsets of the features)
			idx = np.random.choice(range(n_features), size=self.max_features, replace=False)
			# Save the indices of the features for prediction
			self.feature_indices.append(idx)
			# Choose the features corresponding the the indices
			X_subset = X_subset[:, idx]
			# Fit the data to the tree
			self.trees[i].fit(X_subset, y_subset)
			# print "%s / %s" % (i, self.n_estimators)

	def predict(self, X):
		y_preds = []
		# Let each tree make a prediction on the data
		for i, tree in enumerate(self.trees):
			# Select the features that the tree has trained on
			idx = self.feature_indices[i]
			# Make a prediction based on those features
			prediction = tree.predict(X[:, idx])
			y_preds.append(prediction)
		# Take the transpose of the matrix to transform it so
		# that rows are samples and columns are predictions by the
		# estimators
		y_preds = np.array(y_preds).T
		y_pred = []
		# For each sample
		for sample_predictions in y_preds:
			# Do a majority vote over the predictions (columns)
			max_count = 0
			most_common = None
			for label in np.unique(sample_predictions):
				count = len(sample_predictions[sample_predictions == label])
				if count > max_count:
					max_count = count
					most_common = label
			y_pred.append(most_common)
		return y_pred

# Demo of decision tree
def main():
	data = datasets.load_digits()
	X = data.data
	y = data.target

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)

	clf = RandomForest(n_estimators=50)
	clf.fit(X_train, y_train)
	y_pred = clf.predict(X_test)

	print "Accuracy:", accuracy_score(y_test, y_pred)

	pca = PCA()
	pca.plot_in_2d(X_test, y_pred)


if __name__ == "__main__": main()