import torch

from models.MMR import MMR_pipeline_
from utils import get_dataloaders, load_backbones

def Predict(img=img):
    model = torch.load("MMR_instance.pth")
    model.eval()

