#from sklearn import preprocessing
from logistic_sgd import LogisticRegression
from Constructor import *

class CNN_struct(object):

    def __getstate__(self):
        weights = [p.get_value() for p in self.params]
        #return (self.layer0.W, self.layer0.b, self.layer1.W, self.layer1.b, self.layer2.W,  
        #                       self.layer2.b, self.layer3.W, self.layer3.b)
        return weights

    def __setstate__(self, weights):
     #   (self.layer0.W, self.layer0.b, self.layer1.W, self.layer1.b, self.layer2.W, self.layer2.b, self.layer3.W, self.layer3.b) = state
        i = iter(weights)
        for p in self.params:
            p.set_value(i.next())


    def __init__(self, rng, input, nkerns, batch_size, image_size, image_dimension):
        # Reshape matrix of rasterized images of shape (batch_size, size[0] * size[1])
        # to a 4D tensor, compatible with our LeNetConvPoolLayer
        self.layer0_input = input.reshape((batch_size, image_dimension, image_size[0], image_size[1]))

        # Construct the first convolutional pooling layer:
        # filtering reduces the image size to (100-3+1 , 100-3+1) = (98, 98)
        # 4D output tensor is thus of shape (batch_size, nkerns[0], 98, 98)
        self.layer0 = LeNetConvPoolLayer(
            rng,
            input=self.layer0_input,
            image_shape=(batch_size, image_dimension, image_size[0], image_size[1]),
            filter_shape=(nkerns[0], image_dimension, 3, 3),
            poolsize=(2, 2),
            pool_flag = False
        )


        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (98-3+1, 98-3+1) = (96, 96)
        # 4D output tensor is thus of shape (batch_size, nkerns[1], 96, 96)
        self.layer1 = LeNetConvPoolLayer(
            rng,
            input= self.layer0.output,
            image_shape=(batch_size, nkerns[0], 98, 98),
            filter_shape=(nkerns[1], nkerns[0], 3, 3),
            poolsize=(2, 2),
            pool_flag = False
        )

        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (96-5+1, 96-5+1) = (92, 92)
        # maxpooling reduces this further to (94/2, 94/2) = (46, 46)
        # 4D output tensor is thus of shape (batch_size, nkerns[2], 46, 46)
        self.layer2 = LeNetConvPoolLayer(
            rng,
            input = self.layer1.output,
            image_shape=(batch_size, nkerns[1], 96, 96),
            filter_shape=(nkerns[2], nkerns[1], 5, 5),
            poolsize=(2,2),
            pool_flag = True
        )

        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (46-7+1, 46-7+1) = (40, 40)
        # 4D output tensor is thus of shape (batch_size, nkerns[3], 40, 40)
        self.layer3 = LeNetConvPoolLayer(
            rng,
            input=self.layer2.output,
            image_shape=(batch_size, nkerns[2], 46, 46),
            filter_shape=(nkerns[3], nkerns[2], 7, 7),
            poolsize=(2, 2),
            pool_flag=False
        )

        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (40-7+1, 40-7+1) = (34, 34)
        # 4D output tensor is thus of shape (batch_size, nkerns[4], 34, 34)
        self.layer4 = LeNetConvPoolLayer(
            rng,
            input=self.layer3.output,
            image_shape=(batch_size, nkerns[3], 40, 40),
            filter_shape=(nkerns[4], nkerns[3], 7, 7),
            poolsize=(2, 2),
            pool_flag=False
        )

        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (34-11+1, 34-11+1) = (24, 24)
        # maxpooling reduces this further to (24/2, 24/2) = (12, 12)
        # 4D output tensor is thus of shape (batch_size, nkerns[5], 12, 12)
        self.layer5 = LeNetConvPoolLayer(
            rng,
            input=self.layer4.output,
            image_shape=(batch_size, nkerns[4], 34, 34),
            filter_shape=(nkerns[5], nkerns[4], 11, 11),
            poolsize=(2, 2),
            pool_flag=True
        )



        # the HiddenLayer being fully-connected, it operates on 2D matrices of
        # shape (batch_size, num_pixels) (i.e matrix of rasterized images).
        # This will generate a matrix of shape (batch_size, nkerns[5] * 12 * 12),
        # or (66, 20 * 12 * 12) = (66, 2880) with the default values.
        self.layer6_input = self.layer5.output.flatten(2)

        # construct a fully-connected sigmoidal layer
        self.layer6 = HiddenLayer(
            rng,
            input=self.layer6_input,
            n_in= nkerns[5] * 12 * 12,
            n_out=1500,
            activation= T.nnet.relu
        )

        self.layer7 = HiddenLayer(
            rng,
            input=self.layer6.output,
            n_in=1500,
            n_out=500,
            activation=T.nnet.relu
        )

        # classify the values of the fully-connected sigmoidal layer
        # self.layer4 = LogisticRegression(input=self.layer3.output, n_in=300, n_out=10)

        self.layer8 = LogisticRegression(input = self.layer7.output, n_in=500, n_out=2)

        # create a list of all model parameters to be fit by gradient descent
        self.params = self.layer8.params + self.layer7.params + self.layer6.params + \
                      self.layer5.params + self.layer4.params + self.layer3.params + self.layer2.params + self.layer1.params + self.layer0.params

    def get_output(self):
        return self.layer8.get_y_pred()

    def get_flatted_params(self):
        return self.layer8.output
