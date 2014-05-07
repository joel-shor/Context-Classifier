import logging
import numpy as np



#from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv


def check_classifier(train_index, test_index, X,Y,Classifier, room,bin_size):

    correct_dp = []
    
    classifier = Classifier(X[train_index,:],Y[train_index],room,bin_size)
    
    for i in range(len(test_index)):
        x = X[test_index[i],:]
        y = Y[test_index[i],0]
        result = classifier.classify(x)
        correct_dp.append(result[y])
        
    # Process
    correct_dp = np.array(correct_dp)
    
    return correct_dp