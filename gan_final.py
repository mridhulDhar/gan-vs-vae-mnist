import nnConfig

import os
os.environ["KERAS_BACKEND"] = "tensorflow"
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from keras.layers import Input
from keras.models import Model, Sequential
from keras.layers.core import Reshape, Dense, Dropout, Flatten
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Convolution2D, UpSampling2D
from keras.layers.normalization import BatchNormalization
from keras.datasets import mnist
from keras.optimizers import Adam
from keras import backend as K
from keras import initializers

from keras.optimizers import SGD
from keras.optimizers import RMSprop
from keras.optimizers import Adadelta
from keras.optimizers import Adamax
from keras.optimizers import Nadam

# Initial Version Code starts ------------------------------------------------------------------------------------------------


adamLR = nnConfig.adamLR
beta  = nnConfig.beta

def adam_optimizer():
    return Adam(lr=adamLR, beta_1=beta)
def sgd_optimizer():
    return SGD(lr=adamLR, beta_1=beta)
def rmsprop_optimizer():
    return RMSprop(lr=adamLR, beta_1=beta)
def adadelta_optimizer():
    return Adadelta(lr=adamLR, beta_1=beta)
def adamax_optimizer():
    return Adamax(lr=adamLR, beta_1=beta)

def nadam_optimizer():
    return Nadam(lr=adamLR, beta_1=beta)



def create_generator_1():
    generator=Sequential()
    generator.add(Dense(units=256,input_dim=nnConfig.dimensionality))
    generator.add(LeakyReLU(0.2))

    generator.add(Dense(units=512))
    generator.add(LeakyReLU(0.2))

    generator.add(Dense(units=784, activation=nnConfig.activation))

    generator.compile(loss=nnConfig.loss, optimizer=adam_optimizer())
    return generator


def create_generator_2():
    generator=Sequential()
    generator.add(Dense(units=256,input_dim=100))
    generator.add(LeakyReLU(0.2))

    generator.add(Dense(units=512))
    generator.add(LeakyReLU(0.2))

    generator.add(Dense(units=1024))
    generator.add(LeakyReLU(0.2))

    generator.add(Dense(units=784, activation=nnConfig.activationTanh))

    generator.compile(loss='binary_crossentropy', optimizer=nadam_optimizer())
    return generator
g=create_generator_2()
g.summary()

def create_discriminator_1():
    discriminator=Sequential()
    discriminator.add(Dense(units=1024,input_dim=784))
    discriminator.add(LeakyReLU(0.2))



    discriminator.add(Dense(units=512))
    discriminator.add(LeakyReLU(0.2))


    discriminator.add(Dense(units=256))
    discriminator.add(LeakyReLU(0.2))

    discriminator.add(Dense(units=1, activation='sigmoid'))

    discriminator.compile(loss='binary_crossentropy', optimizer=adam_optimizer())
    return discriminator

def create_discriminator_2():
    discriminator=Sequential()
    discriminator.add(Dense(units=1024,input_dim=784))
    discriminator.add(LeakyReLU(0.2))
    discriminator.add(Dropout(0.3))


    discriminator.add(Dense(units=512))
    discriminator.add(LeakyReLU(0.2))
    discriminator.add(Dropout(0.3))

    discriminator.add(Dense(units=256))
    discriminator.add(LeakyReLU(0.2))

    discriminator.add(Dense(units=1, activation='sigmoid'))

    discriminator.compile(loss='binary_crossentropy', optimizer=nadam_optimizer())
    return discriminator
d =create_discriminator_1()
d.summary()

def create_gan_1(discriminator, generator):
    discriminator.trainable=False
    gan_input = Input(shape=(100,))
    x = generator(gan_input)
    gan_output= discriminator(x)
    gan= Model(inputs=gan_input, outputs=gan_output)
    gan.compile(loss='binary_crossentropy', optimizer='sgd')
    return gan

def create_gan_2(discriminator, generator):
    discriminator.trainable=False
    gan_input = Input(shape=(100,))
    x = generator(gan_input)
    gan_output= discriminator(x)
    gan= Model(inputs=gan_input, outputs=gan_output)
    gan.compile(loss='binary_crossentropy', optimizer='adam')
    return gan
gan = create_gan_1(d,g)
gan.summary()

def training(epochs=1, batch_size=128):

    
    (X_train, y_train, X_test, y_test) = load_data()
    batch_count = X_train.shape[0] / batch_size

    generator= create_generator_1()
    discriminator= create_discriminator_1()
    gan = create_gan_1(discriminator, generator)

    for e in range(1,epochs+1 ):
        print("Epoch %d" %e)
        for _ in tqdm(range(batch_size)):
            noise= np.random.normal(0,1, [batch_size, 100])
            generated_images = generator.predict(noise)
            image_batch =X_train[np.random.randint(low=0,high=X_train.shape[0],size=batch_size)]
            X= np.concatenate([image_batch, generated_images])
            y_dis=np.zeros(2*batch_size)
            y_dis[:batch_size]=0.9


            discriminator.trainable=True
            discriminator.train_on_batch(X, y_dis)


            noise= np.random.normal(0,1, [batch_size, 100])
            y_gen = np.ones(batch_size)

            discriminator.trainable=False
            gan.train_on_batch(noise, y_gen)

        if e == 1 or e % 10 == 0:

            plot_generated_images(e, generator)

# ENDS HERE---------------------------------------------------------------------------------------------------------------------

# Final Version Of Code STarts Here--------------------------------------------------------------------------------------------

np.random.seed(1000)
randomDim = 100

(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_train = (X_train.astype(np.float32) - 127.5)/127.5
X_train = X_train.reshape(60000, 784)

adam = Adam(lr=0.0002, beta_1=0.5)

generator = Sequential()
generator.add(Dense(256, input_dim=randomDim, kernel_initializer=initializers.RandomNormal(stddev=0.02)))
generator.add(LeakyReLU(0.2))
generator.add(Dense(512))
generator.add(LeakyReLU(0.2))
generator.add(Dense(1024))
generator.add(LeakyReLU(0.2))
generator.add(Dense(784, activation='tanh'))
generator.compile(loss='binary_crossentropy', optimizer=adam)

discriminator = Sequential()
discriminator.add(Dense(1024, input_dim=784, kernel_initializer=initializers.RandomNormal(stddev=0.02)))
discriminator.add(LeakyReLU(0.2))
discriminator.add(Dropout(0.3))
discriminator.add(Dense(512))
discriminator.add(LeakyReLU(0.2))
discriminator.add(Dropout(0.3))
discriminator.add(Dense(256))
discriminator.add(LeakyReLU(0.2))
discriminator.add(Dropout(0.3))
discriminator.add(Dense(1, activation='sigmoid'))
discriminator.compile(loss='binary_crossentropy', optimizer=adam)

discriminator.trainable = False
ganInput = Input(shape=(randomDim,))
x = generator(ganInput)
ganOutput = discriminator(x)
gan = Model(inputs=ganInput, outputs=ganOutput)
gan.compile(loss='binary_crossentropy', optimizer=adam)

dLosses = []
gLosses = []


def plotLoss(epoch):
    plt.figure(figsize=(10, 8))
    plt.plot(dLosses, label='Discriminitive loss')
    plt.plot(gLosses, label='Generative loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

def plotGeneratedImages(epoch, examples=100, dim=(10, 10), figsize=(10, 10)):
    noise = np.random.normal(0, 1, size=[examples, randomDim])
    generatedImages = generator.predict(noise)
    generatedImages = generatedImages.reshape(examples, 28, 28)

    plt.figure(figsize=figsize)
    for i in range(generatedImages.shape[0]):
        plt.subplot(dim[0], dim[1], i+1)
        plt.imshow(generatedImages[i], interpolation='nearest', cmap='gray_r')
        plt.axis('off')
    plt.tight_layout()

def train(epochs=1, batchSize=128):
    batchCount =int(X_train.shape[0] / batchSize)
    print('Epochs:', epochs)
    print('Batch size:', batchSize)
    print('Batches per epoch:', batchCount)

    for e in range(1, epochs+1):
        print('-'*15, 'Epoch %d' % e, '-'*15)
        for _ in tqdm(range(batchCount)):
            noise = np.random.normal(0, 1, size=[batchSize, randomDim])
            imageBatch = X_train[np.random.randint(0, X_train.shape[0], size=batchSize)]


            generatedImages = generator.predict(noise)

            X = np.concatenate([imageBatch, generatedImages])
            yDis = np.zeros(2*batchSize)
            yDis[:batchSize] = 0.9

            discriminator.trainable = True
            dloss = discriminator.train_on_batch(X, yDis)
            noise = np.random.normal(0, 1, size=[batchSize, randomDim])
            yGen = np.ones(batchSize)
            discriminator.trainable = False
            gloss = gan.train_on_batch(noise, yGen)


        dLosses.append(dloss)
        gLosses.append(gloss)

        if e == 1 or e % 20 == 0:
            plotGeneratedImages(e)


    plotLoss(e)

if __name__ == '__main__':
    train(nnConfig.epochs, nnConfig.batches)
