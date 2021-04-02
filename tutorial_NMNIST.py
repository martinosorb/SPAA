from videofig import videofig
from dataloader_NMNIST import NMNISTDataLoader
from main_NMNIST import train_ann_mnist, get_prob_net
import torch
from experiment_utils import *

# - Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# - Create data loader
nmnist_dataloader = NMNISTDataLoader()

# - Train ANN MNIST model
ann = train_ann_mnist()

# - Turn into spiking prob net
prob_net = get_prob_net()

data_loader_test_spikes = nmnist_dataloader.get_data_loader(dset="test", mode="snn", shuffle=True, num_workers=4, batch_size=1, dt=3000)

for idx, (data, target) in enumerate(data_loader_test_spikes):
    P0 = data
    if target == 0:
        break

P0 = P0[0].to(device)
P0 = torch.clamp(P0, 0.0, 1.0)
model_pred = get_prediction(prob_net, P0)

# - Attack parameters
N_pgd = 50
N_MC = 10
eps = 1.5
eps_iter = 0.3
rand_minmax = 0.01
norm = 2

P_adv = prob_attack_pgd(
    prob_net=prob_net,
    P0=P0,
    eps=eps,
    eps_iter=eps_iter,
    N_pgd=N_pgd,
    N_MC=N_MC,
    norm=norm,
    rand_minmax=rand_minmax,
    verbose=True
)

# - Evaluate the network X times
print("Original prediction",int(get_prediction(prob_net, P0)))
N_eval = 300
correct = []
for i in range(N_eval):
    model_pred_tmp = get_prediction(prob_net, P_adv, "prob")
    if model_pred_tmp == target:
        correct.append(1.0)
print("Evaluation accuracy",float(sum(correct)/N_eval))

plot_attacked_prob(
    P_adv,
    target,
    prob_net,
    N_rows=4,
    N_cols=4,
    block=False,
    figname=1
)

plot_attacked_prob(
    P0,
    target,
    prob_net,
    N_rows=2,
    N_cols=2,
    figname=2
)