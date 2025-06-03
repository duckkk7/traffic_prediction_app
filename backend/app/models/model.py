import torch
import torch.nn.functional as F
from torch import nn
from torch_geometric.nn import GATConv


class TrafficGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()

        self.gat1 = GATConv(in_channels, hidden_channels, heads=2, concat=True)
        self.bn1 = nn.BatchNorm1d(hidden_channels * 2)
        self.dropout1 = nn.Dropout(p=0.3)

        self.gat2 = GATConv(hidden_channels * 2, hidden_channels)
        self.bn2 = nn.BatchNorm1d(hidden_channels)
        self.dropout2 = nn.Dropout(p=0.3)

        self.lin = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index):
        x = self.gat1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.dropout1(x)

        x = self.gat2(x, edge_index)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.dropout2(x)

        return self.lin(x).squeeze(-1)