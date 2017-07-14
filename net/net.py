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
	model.add(Dense(8, kernel_initializer='normal'))
	model.add(Dense(4, kernel_initializer='normal'))
	model.add(Dense(1, kernel_initializer='normal'))
    
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model

def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def main():
    X = []
    Y = []
    
    with open('../input_data.json') as data_file:    
        X = json.load(data_file)
    with open('../target.json') as data_file:    
        Y = json.load(data_file)
        
    y_values = []
    x_values = []
    np_Y = np.array(Y)
    mean = np.mean(np_Y)
    std = np.std(np_Y)
    for point_index, data_point in enumerate(X):
        
        if True: #abs(Y[point_index] - mean) < 2 * std: 
            x_values.append(data_point)
            y_values.append(Y[point_index])
            
       
    print(len(y_values))
    print(np.std(np.array(y_values)))
    seed = 100
    np.random.seed(seed)
    estimators = []
    estimators.append(('standardize', StandardScaler()))
    estimators.append(('mlp', KerasRegressor(build_fn=baseline_model, epochs=34, batch_size=25, verbose=2)))
    pipeline = Pipeline(estimators)
    kfold = KFold(n_splits=5, random_state=seed)
    #results = cross_val_score(pipeline, x_values, y_values, cv=kfold)
    pipeline.fit(x_values[0:5000], y_values[0:5000])
    #print("Standardized: %.2f (%.2f) MSE" % (results.mean(), results.std()))
    print(pipeline.score(x_values[5000:10000], y_values[5000:10000]))
    print(list(pipeline.predict(x_values[5010:5030])))
    print(y_values[5010:5030])
    
if __name__ == "__main__":
    main()