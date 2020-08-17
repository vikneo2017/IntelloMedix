import io

import torch
import torch.nn as nn
from torchvision import models,transforms
from PIL import Image
import pydicom
import numpy as np


def get_model1():
	checkpoint_path='model_1.pt'
	model1 = models.densenet121(pretrained=True)
	num_ftrs = model1.classifier.in_features
	model1.classifier=nn.Sequential(nn.Linear(num_ftrs, 256), nn.ReLU(),nn.Dropout(0.4), nn.Linear(256, 2))
	model1.load_state_dict(torch.load(checkpoint_path,map_location='cpu'),strict=False)
	model1.eval()
	return model1

def get_model2():
	checkpoint_path='model_2.pt'
	model2 = models.densenet121(pretrained=True)
	num_ftrs = model2.classifier.in_features
	model2.classifier=nn.Sequential(nn.Linear(num_ftrs, 256), nn.ReLU(),nn.Dropout(0.4), nn.Linear(256, 5))
	model2.load_state_dict(torch.load(checkpoint_path,map_location='cpu'),strict=False)
	model2.eval()
	return model2

def get_tensor(image_bytes):
	my_transforms=transforms.Compose([transforms.Resize(255),
		                              transforms.CenterCrop(224),
		                              transforms.ToTensor(),
		                              transforms.Normalize(
		                              	[0.485,0.456,0.406],
		                              	[0.229,0.224,0.225])])
	image=Image.open(io.BytesIO(image_bytes)).convert('RGB')
	return my_transforms(image).unsqueeze(0)


def get_tensor2(file):
	ds = pydicom.dcmread(file)
	shape = ds.pixel_array.shape
	image_2d = ds.pixel_array.astype(float)
	image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
	image_2d_scaled = np.uint8(image_2d_scaled)
	output = image_2d_scaled.reshape((shape[1], shape[0]))
	my_transforms = transforms.Compose([transforms.Resize(255),
										transforms.CenterCrop(224),
										transforms.ToTensor(),
										transforms.Normalize(
											[0.485, 0.456, 0.406],
											[0.229, 0.224, 0.225])])
	image = Image.fromarray(output).convert('RGB')
	return my_transforms(image).unsqueeze(0)
