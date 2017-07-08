import json
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def baseline_model():
	# create model
	model = Sequential()
	model.add(Dense(17, input_dim=17, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal'))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model

def main():
    X = []
    Y = []
    
    with open('../input_data.json') as data_file:    
        X = json.load(data_file)
    with open('../target.json') as data_file:    
        Y = json.load(data_file)
        
    seed = 7
    np.random.seed(seed)
    estimators = []
    estimators.append(('standardize', StandardScaler()))
    estimators.append(('mlp', KerasRegressor(build_fn=baseline_model, epochs=50, batch_size=5, verbose=0)))
    pipeline = Pipeline(estimators)
    kfold = KFold(n_splits=10, random_state=seed)
    results = cross_val_score(pipeline, X[0:2000], Y[0:2000], cv=kfold)
    print("Standardized: %.2f (%.2f) MSE" % (results.mean(), results.std()))
    
if __name__ == "__main__":
    main()