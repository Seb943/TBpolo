# Article II : Build and train a DL model for price forecasting
from keras.models import Sequential
from keras.layers import Dense
import os
import pandas as pd
import numpy as np
import pickle as pk
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

list_nPCs = [10, 15, 20, 25, 30, 35, 40]
stoploss = 0.05
takeprofit = 0.1

# (a) Load previously built datasets : we just need train sets and validation sets here
trainset_final = pd.read_csv('./Data/TrainSet_final_stoploss{}_takeprofit{}.csv'.format(stoploss, takeprofit))
trainset = pd.read_csv('./Data/TrainSet_stoploss{}_takeprofit{}.csv'.format(stoploss, takeprofit))

validation_set_final = pd.read_csv('./Data/ValidationSet_final_stoploss{}_takeprofit{}.csv'.format(stoploss, takeprofit))
validation_set = pd.read_csv('./Data/ValidationSet_stoploss{}_takeprofit{}.csv'.format(stoploss, takeprofit))

# (b) Build and train several models different amounts of PCs
for nPCs in list_nPCs:
    print(nPCs)
    X = trainset_final.iloc[:, :nPCs]
    y = trainset["result"]

    # Build model and train it
    classifier = Sequential()
    #First Hidden Layer
    classifier.add(Dense(32, activation='relu', kernel_initializer='random_normal', input_dim=nPCs))
    #Second, third and fourth  hidden Layers
    classifier.add(Dense(32, activation='relu', kernel_initializer='random_normal'))
    classifier.add(Dense(16, activation='relu', kernel_initializer='random_normal'))
    classifier.add(Dense(16, activation='relu', kernel_initializer='random_normal'))

    #Output Layer
    classifier.add(Dense(1, activation='sigmoid', kernel_initializer='random_normal'))
    #Compiling the neural network
    classifier.compile(optimizer ='adam',loss='binary_crossentropy', metrics =['accuracy'])
    #Fitting the data to the training dataset
    classifier.fit(X,y, batch_size=500, epochs=75, verbose =1)

    pk.dump(classifier, open("./Models/DL_model_{}PC_stoploss{}_takeprofit{}.pkl".format(nPCs, stoploss, takeprofit),"wb"))

# (c) Test onto the testset : we compare all models and store results in a csv file
accuracies, nPCs_list = [], []
for nPCs in list_nPCs:
    print(nPCs)
    with open("./Models/DL_model_{}PC_stoploss{}_takeprofit{}.pkl".format(nPCs, stoploss, takeprofit), 'rb') as f:
        clf = pk.load(f)
    # Compute predictions on testset
    preds = (clf.predict(validation_set_final.iloc[:, :nPCs]) > 0.5)*1

    # Assess accuracy on Bullish predictions only (because we will only perform Bullish trades IRL) : we prioritize selectivity
    validation_set1 = validation_set[preds == 1].copy()
    accuracies.append(np.mean(preds == list(validation_set1['result'])))
    nPCs_list.append(nPCs)

recap = pd.DataFrame({'nPCs' : list(nPCs_list), 'Accuracy' : (list(accuracies))})
recap.to_csv('./Results/Comparative_All_models_stoploss{}_takeprofit{}.csv'.format(stoploss, takeprofit), index = False)
print(recap)