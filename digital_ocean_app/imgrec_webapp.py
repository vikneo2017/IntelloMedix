import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# from keras.models import load_model
from keras.backend import set_session
from skimage.transform import resize
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import matplotlib.pyplot as plt
import torchvision
from torchvision import datasets, models
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import time
import os
import copy
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
import torch.onnx
import torchvision
print("Loading model")

global sess
sess = tf.Session()
set_session(sess)
global model
model = torch.load('model v0.1(CT)')
global graph
graph = tf.get_default_graph()


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('dataset/test/noclass', filename))
        return redirect(url_for('prediction', filename=filename))
    return render_template('index.html')




@app.route('/prediction/<filename>')
def prediction(filename):
    #Step 1
	data_transforms_work = {'train': transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224),transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])]), 'test': transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]),}
	def get_dataset_work(data_dir, data_transforms_work):
    # Создаю train и test датасеты
		image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),data_transforms_work[x]) for x in ['train', 'test']}
		dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=1, shuffle=True, num_workers=4) for x in ['train', 'test']}
		dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'test']}
    #Получаем классы из имен папок train датасета
		classes = image_datasets['train'].classes
		return dataloaders["train"], dataloaders['test'], classes, dataset_sizes
	
	data_work ='dataset/'
	trainloader_work, workloader, classes_work, dataset_sizes_work=get_dataset_work(data_work, data_transforms_work)
	
	# Предсказываем класс
	with torch.no_grad():
		set_session(sess)
		for data in workloader:
			images, labels = data
			images, labels = images.cuda(), labels.cuda()
			outputs = modelBR(images)
			_, predicted = torch.max(outputs.data, 1)
			for printdata in list(zip(predicted,labels,outputs)):
				printclass =[classes_work[int(printdata[0])],classes_work[int(printdata[1])]]
				predictions = {"Предсказанный класс по классификации BI-RADS - {0}'.format(printclass[0])}
    
	#Step 2
    return render_template('predict.html', predictions=predictions)


app.run(host='0.0.0.0', port=80)