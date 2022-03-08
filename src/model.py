# -*- coding: utf-8 -*-
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, num_features, layer1_size, layer2_size,layer3_size):
    #def __init__(self, layer1_size=64, layer2_size=84):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(num_features, layer1_size)
        self.fc2 = nn.Linear(layer1_size, layer2_size)
        self.fc3 = nn.Linear(layer2_size, layer3_size)
        self.fc4 = nn.Linear(layer3_size, 2)
        self.dropout = nn.Dropout(p=0.3)

    def forward(self, x):
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.dropout(F.relu(self.fc2(x)))
        x = self.dropout(F.relu(self.fc3(x)))
        x = self.fc4(x)
        return x # check if you have to specify x.to(device)