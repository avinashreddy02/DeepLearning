# -*- coding: utf-8 -*-
"""DCGAN_Anime_Generation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1J7BEOdwdZtZEhy2IrUBDfD6MWsrWgx24
"""

import glob
import io
import math
import time

import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image
from keras import Sequential,Input,Model
from keras.callbacks import TensorBoard
from keras.layers import Conv2D,Dense,Flatten,BatchNormalization,LeakyReLU,ReLU,Reshape,UpSampling2D,Activation,MaxPooling2D
from keras.optimizers import Adam,SGD
from keras.preprocessing import image

#from scipy.misc import imread,imsave
from imageio import imread , imsave
from scipy.stats import entropy

#K.set_image_data_format()
np.random.seed(1337)

def build_generator():
  gen_model = Sequential()

  gen_model.add(Dense(input_dim = 100, output_dim = 2048))
  gen_model.add(ReLU())
  
  gen_model.add(Dense(256 * 8 * 8))
  gen_model.add(BatchNormalization())
  gen_model.add(ReLU())
  gen_model.add(Reshape((8, 8, 256), input_shape = (256 * 8 * 8,)))
  gen_model.add(UpSampling2D(size=(2,2)))

  gen_model.add(Conv2D(128,(5,5),padding = 'same'))
  gen_model.add(ReLU())
  gen_model.add(UpSampling2D(size = (2,2)))

  gen_model.add(Conv2D(64,(5,5),padding = 'same'))
  gen_model.add(ReLU())
  gen_model.add(UpSampling2D(size=(2,2)))

  gen_model.add(Conv2D(3,(5,5),padding = 'same'))
  gen_model.add(Activation('tanh'))

  return gen_model

def build_discriminator():

  dis_model = Sequential()

  dis_model.add(Conv2D(128,(5,5),padding = 'same',input_shape = (64,64,3)))
  dis_model.add(LeakyReLU(alpha=0.2))
  dis_model.add(MaxPooling2D(pool_size=(2,2)))

  dis_model.add(Conv2D(256,(3,3)))
  dis_model.add(LeakyReLU(alpha=0.2))
  dis_model.add(MaxPooling2D(pool_size=(2,2)))

  dis_model.add(Conv2D(512,(3,3)))
  dis_model.add(LeakyReLU(alpha=0.2))
  dis_model.add(MaxPooling2D(pool_size = (2,2)))

  dis_model.add(Flatten())
  dis_model.add(Dense(1024))
  dis_model.add(LeakyReLU(alpha=0.2))

  dis_model.add(Dense(1))
  dis_model.add(Activation('sigmoid'))

  return dis_model

def build_adversarial_model(gen_model,dis_model):
  model = Sequential()
  model.add(gen_model)
  dis_model.trainable = False
  model.add(dis_model)
  return model

def write_log(callback,name,loss,batch_no):

  summary = tf.summary()
  summary_value = summary.value.add()
  summary_value.simple_value = loss
  summary_value.tag = name
  callback.writer.add_summary(summary,batch_no)
  callback.writer.flush()

def visualize_rgb(img):
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)
  ax.imshow(img)
  ax.axis("off")
  ax.set_title("Image")
  plt.show()

def save_rgb_img(img,path):
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)
  ax.imshow(img)
  ax.axis("off")
  ax.set_title("RGB Image")
  plt.savefig(path)
  plt.close()

# data scraping from the web , install the data below packages and run the commands to download the data 

!pip install --upgrade gallery-dl
!pip install animeface
!gallery-dl https://danbooru.donmai.us/posts?tags=face

import animeface

total_num_faces = 0

for index,filename in enumerate(glob.glob('your data path')):
  print(filename)

  try:
    im = Image.open(filename)
    faces = animeface.detect(im)
  except Exception as e:
    print("Exception:{}".format(e))

    continue
    if len(faces) == 0:
      print("no faces found")
      continue

      fp = faces[0].face.pos
      coordinates = (fp.x,fp.y,fp.x+fp.width,fp.y+fp.height)
      cropped_image = im.crop(coordinates)
      cropped_image = cropped_image.resize((64,64),Image.ANTIALIAS)

  cropped_image.save("{}".format(filename))

  print("cropped image saved")

  total_num_faces += 1
  print("total numer of faces detected till now :",total_num_faces)

def train():

  start_time = time.time()
  dataset_dir = "your data path"
  batch_size = 128
  z_shape = 100
  epochs = 5
  dis_learning_rate = 0.1
  gen_learning_rate = 0.1
  #dis_momentum = 0.5
  #gen_momentum = 0.5
  #dis_nesterov = True
  #gen_nesterov = True

  dis_optimizer = Adam(learning_rate=  dis_learning_rate)
  gen_optimizer = Adam(learning_rate= gen_learning_rate)

  dis_model = build_discriminator()
  dis_model.compile(loss = 'binary_crossentropy', optimizer = dis_optimizer)

  gen_model = build_generator()
  gen_model.compile(loss = 'binary_crossentropy',optimizer = gen_optimizer)

  adversarial_model = build_adversarial_model(gen_model,dis_model)
  adversarial_model.compile(loss = 'binary_crossentropy',optimizer = gen_optimizer)

  tensorboard = TensorBoard(log_dir = "logs/{}".format(time.time()),write_images=True,write_grads=True,write_graph=True)
  tensorboard.set_model(gen_model)
  tensorboard.set_model(dis_model)

  for epoch in range(epochs):
    print("-------------------------")
    print("epoch:{}".format(epoch))

    dis_losses = []
    gen_losses = []

    all_images = []

    for index,filename in enumerate(glob.glob("your data path")):
      all_images.append(imread(filename, flatten = False, mode = 'RGB'))

    X = np.array(all_images)
    X = (X-127.5) / 127.5
    X = X.astype(np.float32)

    #X = load_images()
    num_batches = int(X.shape[0]) / batch_size

    print("Number of batches:{}".format(num_batches))

    for index in range(num_batches):

      print("Batch:{}".format(index))

      z_noise = np.random.normal(0,1,size = (batch_size,z_shape))

      gen_images = gen_model.predict_on_batch(z_noise)

      visualize_rgb(gen_images[0])

      dis_model.trainable = True
      image_batch = X[index * batch_size : (index+1) * batch_size]

      y_real = np.ones((batch_size, )) * 0.9
      y_fake = np.zeros((batch_size, )) * 0.1

      dis_loss_real = dis_model.train_on_batch(image_batch,y_real)
      dis_loss_fake = dis_model.train_on_batch(generated_images,y_fake)

      d_loss = (dis_loss_real + dis_loss_fake)/2
      print("d_loss:",d_loss)

      dis_model.trainable = False

      z_noise = np.random.normal(0,1,size = (batch_size, z_shape))

      g_loss = adversarial_model.train_on_batch(z_noise,y_real)

      print("g_loss:",g_loss)

      dis_losses.append(d_loss)
      gen_losses.append(g_loss)

      if epoch % 5 == 0:
        z_noise = np.random.normal(0,1,size = (batch_size,z_shape))
        gen_images1 = gen_model.predict_on_batch(z_noise)

        for img in gen_images1[:2]:
          save_rgb_img(img,"results/one_{}.png".format(epoch))

      print("epoch:{},dis_loss:{}".formt(epoch,np.mean(dis_losses)))
      print("epoch:{},gen_loss:{}".format(epoch,np.mean(gen_losses)))

      write_log(tensorboard,'discriminator_loss',np.mean(dis_losses),epoch)
      write_log(tensorboard,'generator_loss',np.mean(gen_losses),epoch)
    
    gen_model.save("generator_model.h5")
    dis_model.save("discriminator_model.h5")

if __name__ == '__main__':
  train()