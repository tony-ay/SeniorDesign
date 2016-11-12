from __future__ import print_function

import sys
sys.path.append("game/")
import random
import numpy as np
from collections import deque

import json
from keras import initializations
from keras.initializations import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam



class DQN:
    def __init__(self,TorR):


        
        GAME = 'bird' # the name of the game being played for log files
        CONFIG = 'nothreshold'
        self.ACTIONS = 3 # number of valid actions
        self.GAMMA = 0.99 # decay rate of past observations
        self.OBSERVATION = 100. # timesteps to observe before training
        self.EXPLORE = 3000000. # frames over which to anneal epsilon
        self.FINAL_EPSILON = 0.0001 # final value of epsilon
        self.INITIAL_EPSILON = 0.1 # starting value of epsilon
        self.REPLAY_MEMORY = 50000 # number of previous transitions to remember
        self.BATCH = 32 # size of minibatch
        self.FRAME_PER_ACTION = 1
        self.ARRAY_COL=6 #Number of Columns in DQN
        self.ARRAY_ROW=6 #Number of Rows in DQN
        self.INPUTS=6 #Number of inputs for DQN


        
        print("Now we build the model")
        self.model = Sequential()
        self.model.add(Convolution2D(32, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same',input_shape=(4,6,6)))
        self.model.add(Activation('relu'))
        self.model.add(Convolution2D(64, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same'))
        self.model.add(Activation('relu'))
        self.model.add(Convolution2D(64, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same'))
        self.model.add(Activation('relu'))
        self.model.add(Flatten())
        self.model.add(Dense(512, init=lambda shape, name: normal(shape, scale=0.01, name=name)))
        self.model.add(Activation('relu'))
        self.model.add(Dense(self.ACTIONS,init=lambda shape, name: normal(shape, scale=0.01, name=name)))
   
        self.adam = Adam(lr=1e-6)
        self.model.compile(loss='mse',optimizer=self.adam)
        print("We finish building the model")
        
        
        
        self.D = deque()
        self.do_nothing = np.zeros(self.ACTIONS)
        self.do_nothing[0] = 1
        self.x_t=np.ndarray(shape=(self.ARRAY_COL,self.ARRAY_ROW))
        for i in range(self.ARRAY_ROW):
            for j in range(self.ARRAY_COL):
                #x_t[i][j]=stuff[j%INPUTS]
                self.x_t[i][j]=0
                
        self.s_t = np.stack((self.x_t, self.x_t, self.x_t, self.x_t), axis=0)
        #In Keras, need to reshape
        self.s_t = self.s_t.reshape(1, self.s_t.shape[0], self.s_t.shape[1], self.s_t.shape[2])
        self.s_t1=self.s_t
        if TorR== 'R':
            self.OBSERVE = 999999999    #We keep observe, never train
            self.epsilon = self.FINAL_EPSILON
            print ("Now we load weight")
            self.model.load_weights("model.h5")
            self.adam = Adam(lr=1e-6)
            self.model.compile(loss='mse',optimizer=self.adam)
            print ("Weight load successfully")    
        else:                       #We go to training mode
            self.OBSERVE = self.OBSERVATION
            self.epsilon = self.INITIAL_EPSILON
        self.t = 0
        self.Q_sa = 0
        self.action_index = 0
        self.r_t = 0
        
    def trainNetwork(self, reward, number_of_enemy_units, number_of_friendly_units, distance_to_enemy, total_enemy_Hitpoints, total_friendly_Hitpoints, own_health):
        DQNinput=[number_of_enemy_units, number_of_friendly_units, distance_to_enemy, total_enemy_Hitpoints, total_friendly_Hitpoints, own_health]
        loss = 0
        q = self.model.predict(self.s_t) #input a stack of 4 images, get the prediction
        a_t = np.zeros([self.ACTIONS])
        #choose an action epsilon greedy
        if self.t % self.FRAME_PER_ACTION == 0:
            if random.random() <= self.epsilon:
                print("----------Random Action----------")
                action_index = random.randrange(self.ACTIONS)
                a_t[action_index] = 1
                #print(action_index)
               
            else:
                #print("----------Action----------")
                action_index = np.argmax(q)
                a_t[action_index] = 1
                #print(action_index)
        else:
            a_t[0] = 1 # do nothing

        #We reduced the epsilon gradually
        if self.epsilon > self.FINAL_EPSILON and self.t > self.OBSERVE:
            self.epsilon -= (self.INITIAL_EPSILON - self.FINAL_EPSILON) / self.EXPLORE
        self.x_t=np.ndarray(shape=(6,6))
        for i in range(self.ARRAY_ROW):
            for j in range(self.ARRAY_COL):
                self.x_t[i][j]=DQNinput[j%self.INPUTS]
                
        self.x_t = self.x_t.reshape(1, 1, self.x_t.shape[0], self.x_t.shape[1])
        self.s_t1 = np.append(self.x_t, self.s_t[:, :3, :, :], axis=1)



    
    
        #update reward r_t
        self.r_t=reward
    



    
        # store the transition in D
        self.D.append((self.s_t, action_index, self.r_t, self.s_t1))
        if len(self.D) > self.REPLAY_MEMORY:
            self.D.popleft()
        #only train if done observing
        if self.t > self.OBSERVE:
            minibatch = random.sample(self.D, self.BATCH)

            inputs = np.zeros((self.BATCH, self.s_t.shape[1], self.s_t.shape[2], self.s_t.shape[3]))   #32, 80, 80, 4
            targets = np.zeros((inputs.shape[0], self.ACTIONS))

            #Now we do the experience replay
            for i in range(0, len(minibatch)):
                state_t = minibatch[i][0]
                action_t = minibatch[i][1]   #This is action index
                reward_t = minibatch[i][2]
                state_t1 = minibatch[i][3]
                #terminal = minibatch[i][4]
                # if terminated, only equals reward

                inputs[i:i + 1] = state_t    #I saved down s_t

                targets[i] = self.model.predict(state_t)  # Hitting each buttom probability
                Q_sa = self.model.predict(state_t1)

                if reward_t<=0.1:
                    targets[i, action_t] = reward_t
                else:
                    targets[i, action_t] = reward_t + self.GAMMA * np.max(self.Q_sa)

            # targets2 = normalize(targets)
            loss += self.model.train_on_batch(inputs, targets)

        self.s_t = self.s_t1
        self.t = self.t + 1
    
        # save progress every 10000 iterations
        if self.t % 100000 == 0:
            print("Now we save model")
            self.model.save_weights("model.h5", overwrite=True)
            with open("model.json", "w") as outfile:
                json.dump(self.model.to_json(), outfile)


        # print info
        state = ""
        if self.t <= self.OBSERVE:
            state = "observe"
        elif self.t > self.OBSERVE and self.t <= self.OBSERVE + self.EXPLORE:
            state = "explore"
        else:
            state = "train"
        
        print("TIMESTEP", self.t, "/ STATE", state, \
            "/ EPSILON", self.epsilon, "/ ACTION", action_index, "/ REWARD", self.r_t, \
            "/ Q_MAX " , np.max(q), "/ Loss ", loss)
        
        return a_t

