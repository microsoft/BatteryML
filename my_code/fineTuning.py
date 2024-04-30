import yaml
import torch
import optuna
import os
import pandas as pd
import sys
from batteryml.pipeline import Pipeline
import shutil

NUM_OF_TRIALS=100

if  os.path.exists("./cache"):
    shutil.rmtree("./cache")

def objective(trial, model_type, model):
    data = 'hust'
    config_dir = 'configs/baselines/'
    config_path = os.path.join(config_dir,model_type, model, f'{data}.yaml')
    with open(config_path, 'r') as stream:
        config = yaml.safe_load(stream)

    if model_type=='nn_models':
        hyperparameters = {
            # "in_channels": trial.suggest_int("in_channels", 1, 3, step=1),
            "channels": trial.suggest_int("channels", 8, 64, step=8),
            "epochs": trial.suggest_int("epochs", 100, 1000, step=100),
            "batch_size": trial.suggest_int("batch_size", 32, 256, step=32),
            "interp_dim": trial.suggest_int("interp_dim", 600, 2000, step=200),
            # "input_height": trial.suggest_int("input_height", 500, 10000, step=50),  # Adjust range as needed
            # "input_width": trial.suggest_int("input_width", 500, 10000, step=50),   # Adjust range as needed
            # "evaluate_freq": trial.suggest_int("evaluate_freq", 50, 200, step=50),
            # in_channels: 1
            # channels: 16
            # input_height: 100
            # input_width: 1000
            # epochs: 1000
            # batch_size: 128
            # evaluate_freq: 100
        }
    # config['model']['in_channels']=hyperparameters['in_channels']
    config['model']['channels'] = hyperparameters['channels']
    config['model']['epochs'] = hyperparameters['epochs']
    config['model']['batch_size'] = hyperparameters['batch_size']
    config['feature']['interp_dim'] = hyperparameters['interp_dim']
    # config['model']['evaluate_freq'] = hyperparameters['evaluate_freq']
    with open(config_path, 'w') as stream:
        yaml.safe_dump(config, stream)

    pipeline = Pipeline(config_path=config_path, workspace=f'workspaces/cnn')
    # train_loss , test_loss = pipeline.train()
    model, dataset = pipeline.train(device='cuda', skip_if_executed=False)
    train_prediction = model.predict(dataset, data_type='train')
    train_loss = dataset.evaluate(train_prediction, 'MAPE', data_type='train')
    test_prediction = model.predict(dataset, data_type='test')
    test_loss = dataset.evaluate(test_prediction, 'MAPE', data_type='test')

    # validation_loss = evaluate_model(model, validation_data)  # Replace with your evaluation function

    # return validation_loss
    return test_loss


# study = optuna.create_study(direction="minimize")
# study.optimize(objective, n_trials=2)

# best_params = study.best_params
# print(best_params)


results_dict = {}

# Define a list of model types to iterate over
nn_models = ['lstm' ,'mlp','cnn']
model_types=['sklearn','nn_models']

model_type='nn_models'
for model in nn_models:
    print("___________________________________________________"+model + "__________________________________________________")
    study = optuna.create_study(direction='minimize')
    study.optimize(lambda trial: objective(trial, model_type, model), n_trials=NUM_OF_TRIALS)
    best_params = study.best_params
    best_test_loss = study.best_value
    results_dict[model] = {'best_params': best_params, 'best_test_loss': best_test_loss}
    # results_dict[model] = {'best params': best_params, 'best values': study.best_trial.values}

# Print the best parameters and test loss for each model type
for model_type, result in results_dict.items():
    best_params = result['best_params']
    best_test_loss = result['best_test_loss']
    print(f"Model type: {model_type}")
    print(f"Best parameters: {best_params}")
    print(f"Best test loss: {best_test_loss}")
file_path = "./optuna-logs/nn_model_best_new.txt"
with open(file_path, 'w') as file:
    # Write data to the file
    file.write(str(results_dict))