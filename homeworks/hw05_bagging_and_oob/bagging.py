import numpy as np

class SimplifiedBaggingRegressor:
    def __init__(self, num_bags, oob=False):
        self.num_bags = num_bags
        self.oob = oob
        
    def _generate_splits(self, data: np.ndarray):
        '''
        Generate indices for every bag and store in self.indices_list list
        '''
        self.indices_list = []
        data_length = len(data)
        for bag in range(self.num_bags):
            indices = np.random.choice(data_length, size=data_length, replace=True)
            self.indices_list.append(indices)
        
    def fit(self, model_constructor, data, target):
        '''
        Fit model on every bag.
        Model constructor with no parameters (and with no ()) is passed to this function.
        
        example:
        
        bagging_regressor = SimplifiedBaggingRegressor(num_bags=10, oob=True)
        bagging_regressor.fit(LinearRegression, X, y)
        '''
        self.data = data
        self.target = target
        self._generate_splits(data)
        assert len(set(list(map(len, self.indices_list)))) == 1, 'All bags should be of the same length!'
        assert list(map(len, self.indices_list))[0] == len(data), 'All bags should contain `len(data)` number of elements!'
        self.models_list = []
        for bag in range(self.num_bags):
            model = model_constructor()
            data_bag = data[self.indices_list[bag]]
            target_bag = target[self.indices_list[bag]]
            model.fit(data_bag, target_bag)  # Fit the model
            self.models_list.append(model)  # store fitted models here
        
        if self.oob:
            self.data = data
            self.target = target
        
    def predict(self, data):
        '''
        Get average prediction for every object from passed dataset
        '''
        predictions = np.zeros((len(data), self.num_bags))
        for i, model in enumerate(self.models_list):
            predictions[:, i] = model.predict(data)
        return np.mean(predictions, axis=1)
    
    def _get_oob_predictions_from_every_model(self):
        '''
        Generates list of lists, where list i contains predictions for self.data[i] object
        from all models, which have not seen this object during training phase
        '''
        list_of_predictions_lists = [[] for _ in range(len(self.data))]
        for i, indices in enumerate(self.indices_list):
            oob_indices = set(range(len(self.data))) - set(indices)
            for oob_index in oob_indices:
                list_of_predictions_lists[oob_index].append(self.models_list[i].predict(self.data[oob_index].reshape(1, -1))[0])

        
        self.list_of_predictions_lists = np.array(list_of_predictions_lists, dtype=object)
    
    def _get_averaged_oob_predictions(self):
        '''
        Compute average prediction for every object from training set.
        If object has been used in all bags on training phase, return None instead of prediction
        '''
        self._get_oob_predictions_from_every_model()
        self.oob_predictions = []
        for predictions in self.list_of_predictions_lists:
            if predictions:  # If there are predictions to average
                self.oob_predictions.append(np.mean(predictions))
            else:
                self.oob_predictions.append(None)  # No predictions available
        self.oob_predictions = np.array(self.oob_predictions)
        
        
    def OOB_score(self):
        '''
        Compute mean square error for all objects, which have at least one prediction
        '''
        self._get_averaged_oob_predictions()
        squared_errors = []
        for i in range(len(self.oob_predictions)):
            if self.oob_predictions[i] is not None:
                squared_errors.append((self.oob_predictions[i] - self.target[i]) ** 2)
        return np.mean(squared_errors) if squared_errors else None