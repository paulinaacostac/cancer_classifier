
from sklearn.utils import shuffle
import torch
from torch.utils import data
import pickle
import wandb
import math
import pprint
import train
import config



#train_dataset = dataset.SpectraDataset("../pickle_files/test_specs.pkl",50000)

#train_generator = torch.utils.data.DataLoader(train_dataset,batch_size=4,shuffle=True)

#wandb.init(project="ModsClassifier")
if __name__ == "__main__":
    # You can change the number of GPUs per trial here:
    sweep_config = {
    'method': 'random'
    }

    metric = {
    'name': 'loss',
    'goal': 'minimize'   
    }

    sweep_config['metric'] = metric

    parameters_dict = {
    'optimizer': {
        'values': ['adam']
        },
    'layer1_size': {
        'values': [1024]
        },
    'layer2_size': {
        'values': [512]
        },
    'layer3_size': {
         'values': [256]
        },
    }

    sweep_config['parameters'] = parameters_dict

    parameters_dict.update({
    'epochs': {
        'value': 20}
    })

    parameters_dict.update({
    'learning_rate': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 0,
        'max': 0.1
        },
    'batch_size': {
        # integers between 32 and 256
        # with evenly-distributed logarithms 
        'values':[64,128,256]
        }
    })

    pprint.pprint(sweep_config)

    sweep_id = wandb.sweep(sweep_config, project="ModsClassifierFinal")    

    #device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    #main(num_samples=10, max_num_epochs=10, gpus_per_trial=0)

    wandb.agent(sweep_id,train.train_classifier,count=1)

    #print("final accuracy: ",test_accuracy())
