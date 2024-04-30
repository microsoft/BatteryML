import sys
from batteryml.pipeline import Pipeline
from batteryml.visualization.plot_helper import plot_capacity_degradation, plot_cycle_attribute, plot_result

# pipeline = Pipeline(config_path='configs/baselines/sklearn/ridge/hust.yaml',workspace='workspaces')
pipeline = Pipeline(config_path='configs/baselines/nn_models/mlp/hust.yaml',
                    workspace='workspaces')
# C:\Users\User\Desktop\BP\BatteryML\your_modified_yaml_file.yaml
model, dataset = pipeline.train(device='cuda', skip_if_executed=False)

train_prediction = model.predict(dataset, data_type='train')
train_loss = dataset.evaluate(train_prediction, 'RMSE', data_type='train')
train_mape = dataset.evaluate(train_prediction, 'MAPE', data_type='train')
train_mae = dataset.evaluate(train_prediction, 'MAE', data_type='train')

test_prediction = model.predict(dataset, data_type='test')
test_loss = dataset.evaluate(test_prediction, 'RMSE', data_type='test')
test_mape = dataset.evaluate(test_prediction, 'MAPE', data_type='test')
test_mae = dataset.evaluate(test_prediction, 'MAE', data_type='test')
# test_loss_two = dataset.evaluate(test_prediction, 'MAPE', data_type='test')
print(test_prediction)
print(train_prediction)
print(f'RMSE: Train {train_loss:.2f}, test {test_loss:.2f}')
print(f'MAPE: Train {train_mape:.2f}, test {test_mape:.2f}')
print(f'MAE: Train {train_mae:.2f}, test {test_mae:.2f}')

ground_truth = dataset.test_data.label
plot_result(ground_truth, test_prediction)
