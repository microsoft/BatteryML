import pandas as pd
from batteryml.pipeline import Pipeline
import os
import yaml
import shutil

config_dir = 'configs/baselines/'
data = 'hust'
result=[]
featXtractors=["DischargeModelFeatureExtractor","FullModelFeatureExtractor","VarianceModelFeatureExtractor","VoltageCapacityMatrixFeatureExtractor"]
# for method_type in os.listdir(config_dir):
method_type = 'sklearn'
if  os.path.exists("./cache"):
    shutil.rmtree("./cache")
for method in os.listdir(os.path.join(config_dir, method_type)):
    if method=='discharge_model' or method=='variance_model':
        continue
    for extractor in featXtractors:
        # method='variance_model'
        print(method, extractor)
        config_path = os.path.join(config_dir, method_type, method, f'{data}.yaml')

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Modify the config
        # if method=='gpr':
        #     extractor='VarianceModelFeatureExtractor'

        config['feature']['name']=extractor
        if extractor!="VoltageCapacityMatrixFeatureExtractor":
            if 'critical_cycles' not in config['feature']:
                config['feature']['critical_cycles']=[2,9,99]
            if 'interp_dims' not in config['feature']:
                config['feature']['interp_dims'] =1000
            if 'diff_base'  in config['feature']:
                del config['feature']['diff_base']
            if 'max_cycle_index' in config['feature']:
                del config['feature']['max_cycle_index']
            if 'cycles_to_keep' in config['feature']:
                del config['feature']['cycles_to_keep']
        else:
            # print('found')
            if 'critical_cycles' in config['feature']:
                del config['feature']['critical_cycles']
            if 'interp_dims' in config['feature']:
                del config['feature']['interp_dims']
            config['feature']['diff_base']=8
            config['feature']['max_cycle_index']=98
            config['feature']['cycles_to_keep']=98
            # break


        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

        pipeline = Pipeline(config_path=config_path,
                    workspace=f'workspaces/{method}')
        try:
            model, dataset = pipeline.train(device='cuda', skip_if_executed=False)
        except:
            result.append([method_name, extractor, None, None])
            continue
        train_prediction = model.predict(dataset, data_type='train')
        train_loss = dataset.evaluate(train_prediction, 'RMSE', data_type='train')
        # train_mae = dataset.evaluate(train_prediction, 'MAE', data_type='train')
        # train_mape = dataset.evaluate(train_prediction, 'MAPE', data_type='train')
        test_prediction = model.predict(dataset, data_type='test')
        test_loss = dataset.evaluate(test_prediction, 'RMSE', data_type='test')
        mae_loss = dataset.evaluate(test_prediction, 'MAE', data_type='test')
        mape_loss = dataset.evaluate(test_prediction, 'MAPE', data_type='test')
        method_name=method
        if method_name=='full_model':
            method_name='linear regression'
        # result.append([method_name, extractor, train_loss, test_loss])
        result.append([method_name, extractor, train_loss, test_loss, mae_loss,  mape_loss])
        # result.append([method_name, extractor, train_loss, test_loss, train_mae, mae_loss, train_mape, mape_loss])
# res = pd.DataFrame(data=result, columns=['Method','extractor', 'train_RMSE', 'test_RMSE'])
res = pd.DataFrame(data=result, columns=['Method','extractor', 'train_RMSE', 'test_RMSE', 'test_MAE', 'testMAPE'])
# res = pd.DataFrame(data=result, columns=['Method','extractor', 'train_RMSE', 'test_RMSE', 'train_MAE', 'test_MAE', 'train_MAPE', 'testMAPE'])

os.system('clear')
print(res.head)

res.to_csv("optuna-logs\sklearn_models.csv")