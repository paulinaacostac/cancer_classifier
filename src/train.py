from sklearn.utils import shuffle
from wandb import wandb
import dataset
import torch
from torch.utils import data
import pickle
import model
from torch import nn, optim
import dataset
import config
import numpy as np

spectra_size = config.get_config(section='input', key='spec_size')
num_samples_per_class_train = config.get_config(section='input', key='num_samples_per_class_train')
num_samples_per_class_val = config.get_config(section='input', key='num_samples_per_class_val')
num_samples_per_class_test = config.get_config(section='input', key='num_samples_per_class_test')
means_path = config.get_config(section='input', key='means_path')
stds_path = config.get_config(section='input', key='stds_path')

def train_classifier(config=None):
    
    wandb_obj = wandb.init(config=config)
    config = wandb.config
    wandb_obj.name = format_run_name(config)
    
    #wandb.name = "Sweep "+str(config)
    net = model.Net(spectra_size,config.layer1_size,config.layer2_size,config.layer3_size)
    print("this train config: ",config)
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda:0"
        if torch.cuda.device_count() > 1:
            net = nn.DataParallel(net)
    net.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = build_optimizer(net, config.optimizer,0.0001)

    train_dataset = dataset.SpectraDataset("../pickle_files/train_specs.pkl",spectra_size,num_samples_per_class_train, means_path,stds_path)
    train_loader = torch.utils.data.DataLoader(train_dataset,batch_size=1024,shuffle=True,num_workers=4)
    print("train_dataset length: ",len(train_dataset))
    print("train_loader length: ",len(train_loader))

    val_dataset = dataset.SpectraDataset("../pickle_files/val_specs.pkl",spectra_size,num_samples_per_class_val, means_path,stds_path)
    val_loader = torch.utils.data.DataLoader(val_dataset,batch_size=1024,shuffle=True,num_workers=4)
    print("val_dataset length: ",len(val_dataset))
    print("val_loader length: ",len(val_loader))

    test_dataset = dataset.SpectraDataset("../pickle_files/test_specs.pkl",spectra_size,num_samples_per_class_test, means_path,stds_path)
    test_loader = torch.utils.data.DataLoader(test_dataset,batch_size=len(test_dataset),shuffle=True,num_workers=4)
    print("test_dataset length: ",len(test_dataset))
    print("test_loader length: ",len(test_loader))

    for epoch in range(config.epochs):
        net.train()
        training_loss = 0.0
        epoch_steps = 0
        correct_train = 0
        total_train = 0 # usually same as total_val
        print("epoch: ",epoch)
        for i, data in enumerate(train_loader, 0):
            #print("batch: ",i)
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, predicted = torch.max(outputs.data, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

            # print statistics
            training_loss += loss.item()
            epoch_steps += 1

            #print("batch loss: ",loss.item())

            #wandb.log({"batch loss":loss.item()})

        # Validation loss
        net.eval()
        val_loss = 0.0
        val_steps = 0
        total_val = 0
        correct_val = 0
        for i, data in enumerate(val_loader, 0):
            with torch.no_grad():
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)

                outputs = net(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total_val += labels.size(0) # len(data)
                correct_val += (predicted == labels).sum().item()

                loss = criterion(outputs, labels)
                #val_loss += loss.cpu().numpy()
                val_loss += loss.item()
                val_steps += 1

        wandb.log({"train_accuracy":(correct_train/total_train),"epoch":epoch})
        wandb.log({"train_loss":(training_loss/len(train_loader)),"epoch":epoch})
        wandb.log({"val_accuracy":(correct_val/total_val),"epoch":epoch})
        wandb.log({"val_loss":(val_loss/len(val_loader)),"epoch":epoch})

        # Test accuracy
        #torch.save(net.state_dict(), "../saved_models")
        test_acc,loss_acc = test_metrics(net,test_loader,device,criterion)
        wandb.log({"test_accuracy":(test_acc),"epoch":epoch})
        wandb.log({"test_loss":(loss_acc),"epoch":epoch})
        
        
    print("Finished Training-Validation-Testing")
    
  
def test_metrics(net,test_loader,device,criterion):
    correct = 0
    total = 0
    test_loss = 0
    with torch.no_grad():
        for data in test_loader:
            inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = net(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            loss = criterion(outputs, labels)
            test_loss += loss.item()
    return correct/total, test_loss/len(test_loader)


def build_optimizer(network,optimizer,learning_rate):
    if optimizer == "sgd":
        optimizer = optim.SGD(network.parameters(),lr=learning_rate, momentum=0.9)
    elif optimizer == "adam":
        optimizer = optim.Adam(network.parameters(),lr=learning_rate)
    elif optimizer == "adadelta":
        optimizer = optim.Adadelta(network.parameters(),lr=learning_rate)
    elif optimizer == "adagrad":
        optimizer = optim.Adagrad(network.parameters(),lr=learning_rate)
    elif optimizer == "sparseadam":
        optimizer = optim.SparseAdam(network.parameters(),lr=learning_rate)
    elif optimizer == "rmsprop":
        optimizer = optim.RMSprop(network.parameters(),lr=learning_rate)
    return optimizer

def format_run_name(config):
    out = ""
    out += "bs:"+str(config.batch_size)
    out += " ly1:"+str(config.layer1_size)
    out += " ly2:"+str(config.layer2_size)
    out += " ly3:"+str(config.layer3_size)
    out += " lr:"+"{:.2e}".format(config.learning_rate)
    out += " op:"+str(config.optimizer)
    return out

"""
for local_batch,local_labels in train_generator:
    print("local_batch: ",local_batch)
    print("local_labels: ",local_labels)
    break
"""


