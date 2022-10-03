import json
import ulab as np
import gc

gc.enable()
gc.threshold(30000)

__version__ = '1.0.2'

class Model():
    def __init__(self, path):
        f = open(path)
        data = f.read()
        self.model_dict = json.loads(data)
        del data
        for i in range(len(self.model_dict['layers'])):
            if self.model_dict['layers'][i]['class_name'] == 'Dense':
                self.model_dict['layers'][i]['weights'][0]=np.array(self.model_dict['layers'][i]['weights'][0])
                if type(self.model_dict['layers'][i]['weights'][1])==list:
                    self.model_dict['layers'][i]['weights'][1]=np.array(self.model_dict['layers'][i]['weights'][1])
            elif self.model_dict['layers'][i]['class_name'] == 'Conv1D':
                self.model_dict['layers'][i]['weights'][0]=np.array(self.model_dict['layers'][i]['weights'][0])
                if type(self.model_dict['layers'][i]['weights'][1])==list:
                    self.model_dict['layers'][i]['weights'][1]=np.array(self.model_dict['layers'][i]['weights'][1])
    
    def predict(self, x):
        for layer in self.model_dict['layers']:
            if layer['class_name'] == 'Dense':
                x = np.dot(x,layer['weights'][0])
                x = x + layer['weights'][1]
                x = activation(x,f=layer['activation'])
            elif layer['class_name'] == 'Reshape':
                x = reshape(x,tuple(layer['target_shape']))
            elif layer['class_name'] == 'Conv1D':
                x = conv1D(x,layer['weights'][0],
                               layer['weights'][1],
                               kernel_size=layer['kernel_size'],
                               strides=layer['strides'],
                               padding=layer['padding'])
                x = activation(x,f=layer['activation'])
            elif layer['class_name'] == 'MaxPooling1D':
                x = maxPooling1D(x,pool_size=layer['pool_size'],strides=layer['strides'])
            elif layer['class_name'] == 'AveragePooling1D':
                x = averagePooling1D(x,pool_size=layer['pool_size'],strides=layer['strides'])
            elif layer['class_name'] == 'GlobalMaxPooling1D':
                x = globalMaxPooling1D(x)
            elif layer['class_name'] == 'GlobalAveragePooling1D':
                x = globalAveragPooling1D(x)
            elif layer['class_name'] == 'Flatten':
                x = flatten(x)
        return x
    
    def predict_classes(self, x):
        activation = self.model_dict['layers'][-1].get('activation')
        output = self.predict(x)
        if activation=='softmax':      
            output = np.argmax(output,axis=1)
        elif activation=='sigmoid':
            output = np.array(output>=0.5,dtype=np.uint16)
        return output

def activation(x,f='relu'):
    if type(x)==list:
        for i in range(len(x)):
            np.activation(x[i],f=f)
    else:
        np.activation(x,f=f)
    return x

def conv1D(x,w,b,kernel_size=3,strides=1,padding='valid'):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(np.conv1D(x[i],w,b,kernel_size=kernel_size,strides=strides,padding=padding))
        return output
    else:
        raise ValueError('First input should be list')
    
def maxPooling1D(x,pool_size=2,strides=0):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(np.maxPooling1D(x[i],pool_size=pool_size,strides=strides))
        return output
    else:
        raise ValueError('First input should be list')
    
def averagePooling1D(x,pool_size=2,strides=0):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(np.averagePooling1D(x[i],pool_size=pool_size,strides=strides))
        return output
    else:
        raise ValueError('First input should be list')
    
def globalMaxPooling1D(x):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(np.globalMaxPooling1D(x[i]))
        output = np.array(output)
        return output
    else:
        raise ValueError('Input should be list')
    
def globalAveragePooling1D(x):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(np.globalAveragePooling1D(x[i]))
        output = np.array(output)
        return output
    else:
        raise ValueError('Input should be list')
    
def flatten(x):
    if type(x)==list:
        output = []
        for i in range(len(x)):
            output.append(x[i].flatten())
        output = np.array(output)
        return output
    else:
        raise ValueError('First input should be list')
    
def reshape(x,shape):
    if type(x)==type(np.array([])):
        if x.shape()[0]==1:
            output = [np.array(x).reshape(shape)]
        else:
            output = []
            for i in x:
                output.append(i.reshape(shape))
        return output
    else:
        raise ValueError('Input should be ndarray')