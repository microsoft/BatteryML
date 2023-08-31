<div align="center">  
  <img src="./image/Logo_RGB.png" width="300"> 
</div>  

# BatteryML: An Open-Source Tool for Machine Learning on Battery Degradation

## Introduction

The performance degradation of lithium batteries is a complex electrochemical process, involving factors such as the growth of solid electrolyte interface, lithium precipitation, loss of active materials, etc. Furthermore, this inevitable performance degradation can have a significant impact on critical commercial scenarios, such as causing 'range anxiety' for electric vehicle users and affecting the power stability of energy storage systems. Therefore, effectively analyzing and predicting the performance degradation of lithium batteries to provide guidance for early prevention and intervention has become a crucial research topic.

To this end, we open source the BatteryML tool to facilitate the research and development of machine learning on battery degradation.
We hope BatteryML can empower both battery researchers and data scientists to gain deeper insights from battery degradation data and build more powerful models for accurate predictions and early interventions.

## Framework

<img src="./image/framework.png" width="800">


## Highlights:
- **Open-source and Community-driven:** BatteryML is an open-source project for battery degradation modeling, encouraging contributions and collaboration from the communities of both computer science and battery research to push the frontiers of this crucial field.
- **A Comprehensive Dataset Collection:** BatteryML includes a comprehensive dataset collection, allowing easy accesses to most publicly available battery data.
- **Preprocessing and Feature Engineering:** Our tool offers built-in data preprocessing and feature engineering capabilities, making it easier for researchers and developers to prepare ready-to-use battery datasets for machine learning.
- **A Wide Range of Models:** BatteryML already includes most classic models in the literature, enabling developers to quickly compare and benchmark different approaches.
- **Extensible and Customizable:** BatteryML provides flexible interfaces to support further extensions and customizations, making it a versatile tool for potential applications in battery research.

## Quick Start

Install the dependencies

```shell
pip install -r requirements.txt
```

Download the raw data and run preprocessing scripts according to this [instruction](./data_prepare.md).

You only need to set up the data, feature, models .etc in the config file then run the following code
```python
from scripts.pipeline import Pipeline

pipeline = Pipeline(config_path=`path/to/your/config`,
                    device='cuda',
                    metric='RMSE',
                    workspace='workspaces'

train_loss , test_loss = pipeline.train()
```

Besides, we have prepared an example, [baseline](./baseline.ipynb).



## BatteryML capabilities in a glance

## Documentation

By leveraging BatteryML, researchers can gain valuable insights into the latest advancements in battery prediction and materials science, enabling them to conduct experiments efficiently and effectively. We invite you to join us in our journey to accelerate battery research and innovation by contributing to and utilizing BatteryML for your research endeavors.
