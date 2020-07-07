from graph import Grapher
import torch
import scipy.sparse
import torch_geometric.data
import networkx as nx
import numpy as np


def load_data():
    pass



def define_class(df):
    path

def from_networkx(G):
    """Converts a :obj:`networkx.Graph` or :obj:`networkx.DiGraph` to a
    :class:`torch_geometric.data.Data` instance.

    Args:
        G (networkx.Graph or networkx.DiGraph): A networkx graph.
    """

    G = nx.convert_node_labels_to_integers(G)
    edge_index = torch.tensor(list(G.edges)).t().contiguous()

    data = {}

    for i, (_, feat_dict) in enumerate(G.nodes(data=True)):
        for key, value in feat_dict.items():
            data[key] = [value] if i == 0 else data[key] + [value]

    for i, (_, _, feat_dict) in enumerate(G.edges(data=True)):
        for key, value in feat_dict.items():
            data[key] = [value] if i == 0 else data[key] + [value]

    for key, item in data.items():
        try:
            data[key] = torch.tensor(item)
        except ValueError:
            pass 

    data['edge_index'] = edge_index.view(2, -1)
    data = torch_geometric.data.Data.from_dict(data)
    data.num_nodes = G.number_of_nodes()

    return data

if __name__ == "__main__":
    # file = '550'
    # for i in range(10,50):
    #     file = '0' + str(i)
    #     connect = Grapher(file)
    #     result, df = connect.graph_formation(export_graph=True)
    #     connect.relative_distance(export_document_graph = True)
    # print(result)
    # print(df)
    #file = '525'
    file = '012'
    connect = Grapher(file)
    G,result, df = connect.graph_formation()#export_graph=True)
    #df = df.fillna(0)

    df = connect.relative_distance()#export_document_graph = True)

    data = from_networkx(G)


    feature_cols = ['xmin', 'ymin', 'xmax', 'ymax','rd_b','line_number', 'rd_r', 'rd_t', 'rd_l']
    features = torch.tensor(df[feature_cols].values.astype(np.float32))



    df['labels'] = df['labels'].fillna('undefined')
    df.loc[df['labels'] == 'company', 'num_labels'] = 1
    df.loc[df['labels'] == 'address', 'num_labels'] = 2
    df.loc[df['labels'] == 'invoice', 'num_labels'] = 3
    df.loc[df['labels'] == 'date', 'num_labels'] = 4
    df.loc[df['labels'] == 'total', 'num_labels'] = 5
    df.loc[df['labels'] == 'undefined', 'num_labels'] = 6


    labels = torch.tensor(df['num_labels'].values.astype(np.int))
    print(labels)
    print(labels.shape[0])
    
    data.y = labels


    #weights
    data.edge_attr = None 

    idx_train = range(30)
    idx_val = range(30, 40)
    idx_test = range(41, 47)

    idx_train = torch.LongTensor(idx_train)
    idx_val = torch.LongTensor(idx_val)
    idx_test = torch.LongTensor(idx_test)

    def sample_mask(idx, l):
        """Create mask."""
        mask = np.zeros(l)
    
        mask[idx] = 1
        return np.array(mask, dtype=np.bool)

    data.train_mask = sample_mask(idx_train, labels.shape[0])
    data.val_mask = sample_mask(idx_val, labels.shape[0])
    data.test_mask = sample_mask(idx_test, labels.shape[0])

    #train_mask 
    #data.train_idx = torch.tensor([...], dtype=torch.long)
    #data.test_mask = 
    #data.train_idx = 
    #data.val_mask 
    #data.test_mask = 
   


    print(features.shape)

    data.x = features
    print(data)

    print(type(data))
    print(data.__dict__)

     
    
    r"""
    use class batch for it


    """








import os.path as osp
import argparse
import numpy as np 

import torch
import torch.nn.functional as F

import torch_geometric.transforms as T
from torch_geometric.nn import GCNConv, ChebConv  # noqa

parser = argparse.ArgumentParser()

# Training settings
parser = argparse.ArgumentParser()
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='Disables CUDA training.')
parser.add_argument('--fastmode', action='store_true', default=False,
                    help='Validate during training pass.')
parser.add_argument('--seed', type=int, default=42, help='Random seed.')
parser.add_argument('--epochs', type=int, default=200,
                    help='Number of epochs to train.')
parser.add_argument('--lr', type=float, default=0.01,
                    help='Initial learning rate.')
parser.add_argument('--weight_decay', type=float, default=5e-4,
                    help='Weight decay (L2 loss on parameters).')
parser.add_argument('--hidden', type=int, default=16,
                    help='Number of hidden units.')
parser.add_argument('--dropout', type=float, default=0.5,
                    help='Dropout rate (1 - keep probability).')\

#early stopping criteria
parser.add_argument('--early_stopping', type=int, default = 50,
                    help = 'Stopping criteria for validation')



parser.add_argument('--use_gdc', action='store_true',
                    help='Use GDC preprocessing.')
args = parser.parse_args()





if args.use_gdc:
    gdc = T.GDC(self_loop_weight=1, normalization_in='sym',
                normalization_out='col',
                diffusion_kwargs=dict(method='ppr', alpha=0.05),
                sparsification_kwargs=dict(method='topk', k=128,
                                           dim=0), exact=True)
    data = gdc(data)



#cached = True is for transductive learning
class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = GCNConv(9, 32, cached=True,\
                             normalize=not args.use_gdc)
        self.conv2 = GCNConv(32, 7, cached=True,\
                             normalize=not args.use_gdc)

        
        # self.conv1 = ChebConv(data.num_features, 16, K=2)
        # self.conv2 = ChebConv(16, data.num_features, K=2)

        self.reg_params = self.conv1.parameters()
        self.non_reg_params = self.conv2.parameters()

    def forward(self):
        x, edge_index, edge_weight = data.x, data.edge_index, data.edge_attr
        x = F.relu(self.conv1(x, edge_index, edge_weight))
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index, edge_weight)
        return F.log_softmax(x, dim=1)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, data = Net().to(device), data.to(device)
optimizer = torch.optim.Adam([
    dict(params=model.reg_params, weight_decay=5e-4),
    dict(params=model.non_reg_params, weight_decay=0)
], lr=0.01)


def train():
    model.train()
    optimizer.zero_grad()
    loss = F.nll_loss(model()[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()
    return loss


@torch.no_grad()
def test():
    model.eval()
    
    #F.nll_loss(model()[data.val_mask], data.y[data.val_mask])
    logits, accs = model(), []
    for _, mask in data('train_mask', 'val_mask', 'test_mask'):
        pred = logits[mask].max(1)[1]
        acc = pred.eq(data.y[mask]).sum().item() / mask.sum().item()
        accs.append(acc)
    return accs



#stopping criteria 
counter = 0


for epoch in range(1, args.epochs):
    

    loss = train()
    train_acc, val_acc, test_acc = test()

    with torch.no_grad():
        loss_val = F.nll_loss(model()[data.val_mask], data.y[data.val_mask])


 
    
    log = 'Epoch: {:03d}, train_loss:{:.4f}, val_loss:{:.4f}, Train: {:.4f}, Val: {:.4f}, Test: {:.4f}'
    print(log.format(epoch,loss,loss_val, train_acc, val_acc, test_acc))


    #for first epoch
    if epoch == 1:
        largest_val_loss = loss_val

    #early stopping if the loss val does not improve/decrease for a number of epochs
    if loss_val >= largest_val_loss:
        counter += 1 
        best_val_loss = loss_val
        if counter >= args.early_stopping:
            print(f'EarlyStopping counter: validation loss did not increase for {args.early_stopping}!!')
            break