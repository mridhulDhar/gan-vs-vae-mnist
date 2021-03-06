import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import nnConfig

def create_encoder(self, nn_input, act, drop):
        x = nn_input
        for l in self.layer_sizes:
            x = Dense(l, activation=act)(x)
            if drop:
                x = Dropout(drop)(x)
        z_mean = Dense(self.latent_dim)(x)
        z_log_var = Dense(self.latent_dim)(x)
        return z_mean, z_log_var

def create_decoder(self, act, drop):
        z = Lambda(self.sampling, output_shape=(self.latent_dim,))([self.z_mean, self.z_var])
        rev_layers = self.layer_sizes[::-1]
        ae_output = z
        inpt = Input(shape=(self.latent_dim,), name="decoder_input")
        dec_tensor = inpt
        if len(rev_layers) > 1:
            for lay in rev_layers:
                dec = Dense(lay, activation=act)
                ae_output = dec(ae_output)
                dec_tensor = dec(dec_tensor)
                if drop:
                    ae_output = Dropout(drop)(ae_output)
                    dec_tensor = Dropout(drop)(dec_tensor)
        output_layer = Dense(self.input_size, activation=act, name="output")
        ae_output = output_layer(ae_output)
        dec_tensor = output_layer(dec_tensor)
        decoder = Model(inpt, dec_tensor)
        return ae_output, decoder

def relu(self, x, leak=0.2, name="myrelu"):
    with tf.variable_scope(name):
        f1 = 0.5 * (1 + leak)
        f2 = 0.5 * (1 - leak)
        return f1 * x + f2 * abs(x)

def weight_variable(self, shape, name='weights'):
  return tf.get_variable(name, shape, initializer=tf.contrib.layers.xavier_initializer())

def bias_variable(self, shape, name='biases'):
  return tf.get_variable(name, shape, initializer=tf.constant_initializer(0.0))

def conv2d(self, x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(self, x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

def train_batch(self, x, y):
  self.session.run(self.train_step, feed_dict={self.x: x, self.y_: x})

def evaluate(self, x, y):
  return self.session.run(self.accuracy, feed_dict={self.x: x, self.y_: x});

def save(self, path):
  if not os.path.exists(path):
    os.makedirs(path)
  saver = tf.train.Saver(max_to_keep=1)
  saver.save(self.session, path + '/model')

def load(self, path):
  saver = tf.train.Saver()
  saver.restore(self.session, tf.train.latest_checkpoint(path))

def embed(self, images, batchsize=100):
  num_batches = images.shape[0] // batchsize
  all_embeds = None
  for i in range(num_batches):
    batch = images[(i*batchsize):((i+1)*batchsize)]
    batch_embed = self.session.run(self.embed_layer, feed_dict={self.x: batch})
    if all_embeds is None:
      all_embeds = batch_embed
    else:
      all_embeds = np.concatenate((all_embeds, batch_embed))
  return all_embeds

def output_reconstructed_images(self, output_path, x):
  result = self.session.run(self.y, feed_dict={self.x: x})
  orig_image = np.reshape(x, (x.shape[0]*28, 28)) * 255.0
  result_image = np.reshape(result, (x.shape[0]*28, 28)) * 255.0
  combo_image = np.concatenate((orig_image, result_image), axis=1)
  png.save_png(output_path, combo_image)

def vae():
  parser = argparse.ArgumentParser()
  parser.add_argument("--embed-model", help="path to the model to use for embedding")
  global args
  
  args = parser.parse_args()    
  
  print(args)

  batchsize = 100
  
  trainer = Trainer()

  mnist = Dataset.load_mnist()
  autoencoder = MNISTConvVariationalAutoencoder(True, 20, batchsize)
  print("Loading model from %s" % args.embed_model)
  autoencoder.load(args.embed_model)

  print("Generating embedding...")
  smallMnist = mnist.slice(2000, 1000, mnist.test.count)
  embeddedMnist = Dataset(autoencoder.embed(smallMnist.train.x, batchsize), mnist.train.y,
                          autoencoder.embed(smallMnist.validation.x, batchsize), mnist.validation.y,
                          autoencoder.embed(smallMnist.test.x, batchsize), mnist.test.y)
  embeddedMnist.train.x = np.concatenate((smallMnist.train.x, embeddedMnist.train.x), axis=1)
  embeddedMnist.validation.x = np.concatenate((smallMnist.validation.x, embeddedMnist.validation.x), axis=1)
  embeddedMnist.test.x = np.concatenate((smallMnist.test.x, embeddedMnist.test.x), axis=1)

# Ends Here---------------------------------------------------------------------------------------------------------------------------

class Sampling(layers.Layer):
    

    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

latent_dim = 2

encoder_inputs = keras.Input(shape=(28, 28, 1))
x = layers.Conv2D(32, 3, activation=nnConfig.activationRelu, strides=2, padding=nnConfig.padding)(encoder_inputs)
x = layers.Conv2D(64, 3, activation=nnConfig.activationRelu, strides=2, padding=nnConfig.padding)(x)
x = layers.Flatten()(x)
x = layers.Dense(16, activation=nnConfig.activationRelu)(x)
z_mean = layers.Dense(latent_dim, name="z_mean")(x)
z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)
z = Sampling()([z_mean, z_log_var])
encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name="encoder")
encoder.summary()

latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(7 * 7 * 64, activation="relu")(latent_inputs)
x = layers.Reshape((7, 7, 64))(x)
x = layers.Conv2DTranspose(64, 3, activation="relu", strides=2, padding="same")(x)
x = layers.Conv2DTranspose(32, 3, activation="relu", strides=2, padding="same")(x)
decoder_outputs = layers.Conv2DTranspose(1, 3, activation="sigmoid", padding="same")(x)
decoder = keras.Model(latent_inputs, decoder_outputs, name="decoder")
decoder.summary()

class VAE(keras.Model):
    def __init__(self, encoder, decoder, **kwargs):
        super(VAE, self).__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder

    def train_step(self, data):
        if isinstance(data, tuple):
            data = data[0]
        with tf.GradientTape() as tape:
            z_mean, z_log_var, z = encoder(data)
            reconstruction = decoder(z)
            reconstruction_loss = tf.reduce_mean(
                keras.losses.binary_crossentropy(data, reconstruction)
            )
            reconstruction_loss *= 28 * 28
            kl_loss = 1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
            kl_loss = tf.reduce_mean(kl_loss)
            kl_loss *= -0.5
            total_loss = reconstruction_loss + kl_loss
        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        return {
            "loss": total_loss,
            "reconstruction_loss": reconstruction_loss,
            "kl_loss": kl_loss,
        }

(x_train, _), (x_test, _) = keras.datasets.mnist.load_data()
mnist_digits = np.concatenate([x_train, x_test], axis=0)
mnist_digits = np.expand_dims(mnist_digits, -1).astype("float32") / 255

vae = VAE(encoder, decoder)
vae.compile(optimizer=keras.optimizers.Adam())
vae.fit(mnist_digits, epochs=45, batch_size=250)

import matplotlib.pyplot as plt


def plot_latent(encoder, decoder):
    n = 30
    digit_size = 28
    scale = 2.0
    figsize = 15
    figure = np.zeros((digit_size * n, digit_size * n))
    grid_x = np.linspace(-scale, scale, n)
    grid_y = np.linspace(-scale, scale, n)[::-1]

    for i, yi in enumerate(grid_y):
        for j, xi in enumerate(grid_x):
            z_sample = np.array([[xi, yi]])
            x_decoded = decoder.predict(z_sample)
            digit = x_decoded[0].reshape(digit_size, digit_size)
            figure[
                i * digit_size : (i + 1) * digit_size,
                j * digit_size : (j + 1) * digit_size,
            ] = digit

    plt.figure(figsize=(figsize, figsize))
    start_range = digit_size // 2
    end_range = n * digit_size + start_range + 1
    pixel_range = np.arange(start_range, end_range, digit_size)
    sample_range_x = np.round(grid_x, 1)
    sample_range_y = np.round(grid_y, 1)
    plt.xticks(pixel_range, sample_range_x)
    plt.yticks(pixel_range, sample_range_y)
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.imshow(figure, cmap="Greys_r")
    plt.show()


plot_latent(encoder, decoder)