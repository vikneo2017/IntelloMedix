import torch.nn as nn
from commons import get_model1, get_model2, get_tensor, get_tensor2
import pydicom
import numpy as np

classes_name1 = {'0': 'No', '1': 'Yes'}
model1=get_model1()
def get_result1(image_bytes):
    tensor=get_tensor(image_bytes)
    outputs=model1(tensor)
    _,prediction=outputs.max(1)
    category=prediction.item()
    resultat1 = classes_name1[str(category)]

    return resultat1

classes_name2 = {'1': 'Class BI-RADS: 1', '2': 'Class BI-RADS: 2', '3':'Class BI-RADS: 3', '4': 'Class BI-RADS: 4', '5':'Class BI-RADS: 5'}
model2=get_model2()
def get_result2(image_bytes):
    tensor=get_tensor(image_bytes)
    outputs=model2(tensor)
    _,prediction=outputs.max(1)
    category=prediction.item()
    # resultat2 = classes_name2[str(category)]

    return category

def get_probability(image_bytes):
    tensor=get_tensor(image_bytes)
    outputs=model1(tensor)
    probability = max(nn.functional.softmax(outputs).tolist()[0])

    return str(probability)

classes_name1_dcm = {'0': 'No', '1': 'Yes'}
model1=get_model1()
def get_result1_dcm(file):
    tensor=get_tensor2(file)
    outputs=model1(tensor)
    _,prediction=outputs.max(1)
    category=prediction.item()
    resultat1 = classes_name1_dcm[str(category)]

    return resultat1

classes_name2_dcm = {'1': 'Class BI-RADS: 1', '2': 'Class BI-RADS: 2', '3':'Class BI-RADS: 3', '4': 'Class BI-RADS: 4', '5':'Class BI-RADS: 5'}
model2=get_model2()
def get_result2_dcm(file):
    tensor=get_tensor2(file)
    outputs=model2(tensor)
    _,prediction=outputs.max(1)
    category=prediction.item()
    # resultat2 = classes_name2_ct[str(category)]

    return category

def get_probability_dcm(file):
    tensor=get_tensor2(file)
    outputs=model1(tensor)
    probability = max(nn.functional.softmax(outputs).tolist()[0])

    return str(probability)

def save_dcmtodb(filepath):
    ds = pydicom.dcmread(filepath)
    shape = ds.pixel_array.shape
    image_2d = ds.pixel_array.astype(float)
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    image_2d_scaled = np.uint8(image_2d_scaled)
    output = image_2d_scaled.reshape((shape[1], shape[0]))

    return output