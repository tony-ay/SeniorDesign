from __future__ import print_function

import sys
sys.path.append("game/")
import random
import numpy as np
from collections import deque

from keras import initializations
from keras.initializations import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam



class DQN:
    def __init__(self,TorR):
        print("Now we build the model")
        model = Sequential()
        model.add(Convolution2D(32, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same',input_shape=(4,6,6)))
        model.add(Activation('relu'))
        model.add(Convolution2D(64, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same'))
        model.add(Activation('relu'))
        model.add(Convolution2D(64, 2, 2, subsample=(1,1),init=lambda shape, name: normal(shape, scale=0.01, name=name), border_mode='same'))
        model.add(Activation('relu'))
        model.add(Flatten())
        model.add(Dense(512, init=lambda shape, name: normal(shape, scale=0.01, name=name)))
        model.add(Activation('relu'))
        model.add(Dense(ACTIONS,init=lambda shape, name: normal(shape, scale=0.01, name=name)))
   
        adam = Adam(lr=1e-6)
        model.compile(loss='mse',optimizer=adam)
        print("We finish building the model")
        
        GAME = 'bird' # the name of the game being played for log files
        CONFIG = 'nothreshold'
        ACTIONS = 2 # number of valid actions
        GAMMA = 0.99 # decay rate of past observations
        OBSERVATION = 10000. # timesteps to observe before training
        EXPLORE = 3000000. # frames over which to anneal epsilon
        FINAL_EPSILON = 0.0001 # final value of epsilon
        INITIAL_EPSILON = 0.1 # starting value of epsilon
        REPLAY_MEMORY = 50000 # number of previous transitions to remember
        BATCH = 32 # size of minibatch
        FRAME_PER_ACTION = 1
        ARRAY_COL=6 #Number of Columns in DQN
        ARRAY_ROW=6 #Number of Rows in DQN
        INPUTS=6 #Number of inputs for DQN
        
        D = deque()
        do_nothing = np.zeros(ACTIONS)
        do_nothing[0] = 1
        x_t=np.ndarray(shape=(ARRAY_COL,ARRAY_ROW))
        for i in range(ARRAY_COL):
            for j in range(ARRAY_ROW):
                #x_t[i][j]=stuff[j%INPUTS]
                x_t[i][j]=0
                
        s_t = np.stack((x_t, x_t, x_t, x_t), axis=0)
        #In Keras, need to reshape
        s_t = s_t.reshape(1, s_t.shape[0], s_t.shape[1], s_t.shape[2])
        s_t1=s_t
        if TorR== 'R':
            OBSERVE = 999999999    #We keep observe, never train
            epsilon = FINAL_EPSILON
            print ("Now we load weight")
            model.load_weights("model.h5")
            adam = Adam(lr=1e-6)
            model.compile(loss='mse',optimizer=adam)
            print ("Weight load successfully")    
        else:                       #We go to training mode
            OBSERVE = OBSERVATION
            epsilon = INITIAL_EPSILON
        t = 0
        Q_sa = 0
        action_index = 0
        r_t = 0
def trainNetwork(self, number_of_enemy_units, number_of_freindly_units, distance_to_enemy, closest_enemy, total_enemy_Hitpoints, own_health):
    DQNinput=[number_of_enemy_units, number_of_freindly_units, distance_to_enemy, closest_enemy, total_enemy_Hitpoints, own_health]
    loss = 0
    q = model.predict(s_t) #input a stack of 4 images, get the prediction
    a_t = np.zeros([ACTIONS])
    #choose an action epsilon greedy
    if t % FRAME_PER_ACTION == 0:
        if random.random() <= epsilon:
            print("----------Random Action----------")
            action_index = random.randrange(ACTIONS)
            a_t[action_index] = 1
        else:      
            action_index = np.argmax(q)
            a_t[action_index] = 1
    else:
        a_t[0] = 1 # do nothing

    #We reduced the epsilon gradually
    if epsilon > FINAL_EPSILON and t > OBSERVE:
        epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE
    for i in range(ARRAY_COL):
        for j in range(ARRAY_ROW):
            x_t[i][j]=DQNinput[j%INPUTS]
                
    x_t = x_t.reshape(1, 1, x_t.shape[0], x_t.shape[1])
    s_t1 = np.append(x_t, s_t[:, :3, :, :], axis=1)



    
    
    #update reward r_t
    #if any squad member got kill r_t=1
    #if squad member died r_t =-1
    #else r_t =0.01
    



    
    # store the transition in D
    D.append((s_t, action_index, r_t, s_t1, terminal))
        if len(D) > REPLAY_MEMORY:
            D.popleft()
    #only train if done observing
    if t > OBSERVE:
        minibatch = random.sample(D, BATCH)

        inputs = np.zeros((BATCH, s_t.shape[1], s_t.shape[2], s_t.shape[3]))   #32, 80, 80, 4
        targets = np.zeros((inputs.shape[0], ACTIONS))

        #Now we do the experience replay
        for i in range(0, len(minibatch)):
            state_t = minibatch[i][0]
            action_t = minibatch[i][1]   #This is action index
            reward_t = minibatch[i][2]
            state_t1 = minibatch[i][3]
            terminal = minibatch[i][4]
            # if terminated, only equals reward

            inputs[i:i + 1] = state_t    #I saved down s_t

            targets[i] = model.predict(state_t)  # Hitting each buttom probability
            Q_sa = model.predict(state_t1)

            if terminal:
                targets[i, action_t] = reward_t
            else:
                targets[i, action_t] = reward_t + GAMMA * np.max(Q_sa)

        # targets2 = normalize(targets)
        loss += model.train_on_batch(inputs, targets)

    s_t = s_t1
    t = t + 1

    # save progress every 10000 iterations
    if t % 10000 == 0:
        print("Now we save model")
        model.save_weights("model.h5", overwrite=True)
        with open("model.json", "w") as outfile:
            json.dump(model.to_json(), outfile)


    # print info
    state = ""
    if t <= OBSERVE:
        state = "observe"
    elif t > OBSERVE and t <= OBSERVE + EXPLORE:
        state = "explore"
    else:
        state = "train"

    print("TIMESTEP", t, "/ STATE", state, \
        "/ EPSILON", epsilon, "/ ACTION", action_index, "/ REWARD", r_t, \
        "/ Q_MAX " , np.max(q), "/ Loss ", loss)


