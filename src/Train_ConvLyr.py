

# -*- coding: utf-8 -*-


"""
/* -----------------------------------------------------------------------------
  Copyright: (C) Daniel Lu, RasVector Technology.

  Email : dan59314@gmail.com
  Web :     http://www.rasvector.url.tw/
  YouTube : http://www.youtube.com/dan59314/playlist

  This software may be freely copied, modified, and redistributed
  provided that this copyright notice is preserved on all copies.
  The intellectual property rights of the algorithms used reside
  with the Daniel Lu, RasVector Technology.

  You may not distribute this software, in whole or in part, as
  part of any commercial product without the express consent of
  the author.

  There is no warranty or other guarantee of fitness of this
  software for any purpose. It is provided solely "as is".

  ---------------------------------------------------------------------------------
  版權宣告  (C) Daniel Lu, RasVector Technology.

  Email : dan59314@gmail.com
  Web :     http://www.rasvector.url.tw/
  YouTube : http://www.youtube.com/dan59314/playlist

  使用或修改軟體，請註明引用出處資訊如上。未經過作者明示同意，禁止使用在商業用途。
*/


Created on Wed Feb  7 22:11:59 2018

@author: dan59314
"""


#%%
# Standard library----------------------------------------------
import sys
sys.path.append('../data')
sys.path.append('../RvLib')
import os
import time
from datetime import datetime


# Third-party libraries------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cmn


# prvaite libraries---------------------------------------------
import mnist_loader
import RvNeuralNetworks as rn
from RvNeuralNetworks import *
import RvAskInput as ri
import RvMiscFunctions as rf
import RvNeuNetworkMethods as nm
from RvNeuNetworkMethods import EnumDropOutMethod as drpOut
import PlotFunctions as pltFn




#%%  


def Add_ConvLayer(lyrObjs, lyrsNeus,  inputNeusNum, cnvLyrSId):
    nChannel=1
    inputW = np.sqrt(inputNeusNum)
    inputH = inputW
    inputShape =[inputW,inputH,nChannel]     
    
    # the less the filterW,H is, the more the Neurons num and the higher accuracy------
    filterW       = 5
    filterH       = 5
    filterNum     = 10
    filterShape = np.asarray([filterW,filterH, nChannel, filterNum])     
    # the less the filterStride is, the more the oveloap will be, the higher the accuracy -----------
    filterStride = 1
    cnvLyr = rn.RvConvolutionLayer(
        inputShape, # eg. [pxlW, pxlH, Channel]
        filterShape, # eg. [pxlW, pxlH, Channel, FilterNum], 
        filterStride)        
    lyrObjs.append(cnvLyr)
    cnvLyrSId += 1
    lyrsNeus.insert(cnvLyrSId, cnvLyr.Get_NeuronsNum())
    return lyrsNeus, cnvLyrSId, cnvLyr


        
        

def Main():    
    #Load MNIST ****************************************************************
    
    #mnist.pkl.gz(50000） Accuracy 0.96 
    #mnist_expanded.pkl.gz(250000） Accuracy 0.97 
    fn = "..\\data\\mnist.pkl.gz"  #".datamnist_expanded.pkl.gz"
    lstTrain, lstV, lstT =  mnist_loader.load_data_wrapper(fn)
    lstTrain = list(lstTrain)
    lstV = list(lstV)
    lstT = list(lstT)
    
    
    # *********************************************************************
    path = "..\\TmpLogs\\"
    if not os.path.isdir(path):
        os.mkdir(path)           
    
    fnNetworkData = "{}{}_CNN".format(path,rn.RvNeuralNetwork.__name__)   
    fnSaved = ""
    
    
    #Hyper pameters -------------------------------------------    
    loop = 10  # loop effect，10, 30 all above 0.95
    stepNum = 10  # stepNum effect,　10->0.9,  100->0.5
    learnRate = 0.1  # learnRate and lmbda will affect each other
    lmbda = 5.0     #add lmbda(Regularization) to solve overfitting 
    
    
    sTrain = "y"
    # Training ***********************************************************
    # Ask DoTraining-
    LoadAndTrain = ri.Ask_YesNo("Load exist model and continue training?", "n")    
    
    if LoadAndTrain:    
        fns, shortFns =  rfi.Get_FilesInFolder(".\\NetData\\", [".cnn"])
        aId = ri.Ask_SelectItem("Select CNN Network file", shortFns, 0)    
        fn1= fns[aId]
        net = rn.RvNeuralNetwork(fn1) 
        sTrain = "n"
        initialWeiBias = False
        
    else:            
        """
        [784,50,10], 
            loop=10, 0.9695
            loop=100, 0.9725
        """
         # 建立 RvNeuralNetWork----------------------------------------------
        inputNeusNum = len(lstTrain[0][0])
        lyr1NeuNum = 50
        lyr2NeuNum = len(lstTrain[0][1])
        
        lyrsNeus = [inputNeusNum, lyr1NeuNum]
        lyrsNeus = ri.Ask_Add_Array_Int("Input new layer Neurons num.", lyrsNeus, lyr1NeuNum)
        lyrsNeus.append(lyr2NeuNum)
        
        #net = rn.RvNeuralNetwork( \
        #   rn.RvNeuralNetwork.LayersNeurons_To_RvNeuralLayers(lyrsNeus))
        #net = rn.RvNeuralNetwork.Class_Create_LayersNeurons(lyrsNeus)
        #net = rn.RvNeuralNetwork(lyrsNeus)  # ([784,50,10])
        
        cnvLyrSId = 0
        lyrObjs=[]
        
        
        # Add RvConvolutionLayer--------------------------------   
        EnableCovolutionLayer = ri.Ask_YesNo("Add ConvolutionLayer?", "y")
        if EnableCovolutionLayer:             
          lyrsNeus, cnvLyrSId, cnvLyr = Add_ConvLayer(lyrObjs, lyrsNeus, inputNeusNum, cnvLyrSId)
          
          
        # Create Layer Object array -------------------------------
        for iLyr in range(cnvLyrSId, len(lyrsNeus)-1):
            lyrObjs.append( rn.RvNeuralLayer([lyrsNeus[iLyr], lyrsNeus[iLyr+1]]) )
        
#        lyrObjs.append( rn.RvNeuralLayer([784, 100]) )        
#        lyrObjs.append(rn.RvConvolutionLayer(
#                [10,10,1], # eg. [pxlW, pxlH, Channel]
#                [5,5,1,1], # eg. [pxlW, pxlH, Channel, FilterNum], 
#                1) )
#        lyrObjs.append( rn.RvNeuralLayer([lyrObjs[-1].Get_NeuronsNum(),10]) )
            
        net = rn.RvNeuralNetwork(lyrObjs)
        initialWeiBias = True
        
        
    # Training ***********************************************************
    DoTrain = ri.Ask_YesNo("Do Training?", sTrain)    
    if DoTrain:        
        fnNetworkData = "{}_{}Lyr".format(fnNetworkData, len(net.NeuralLayers))
        
        # Ask nmtivation  ------------------_----------
        enumActivation = ri.Ask_Enum("Select Activation method.", 
             nm.EnumActivation,  nm.EnumActivation.afReLU )
        for lyr in net.NeuralLayers:
            lyr.ClassActivation, lyr.ClassCost = \
            nm.Get_ClassActivation(enumActivation)
        
        net.NetEnableDropOut = ri.Ask_YesNo("Execute DropOut?", "n")
        if net.NetEnableDropOut:
            enumDropOut = ri.Ask_Enum("Select DropOut Method.", 
            nm.EnumDropOutMethod,  drpOut.eoSmallActivation )
            rn.gDropOutRatio = ri.Ask_Input_Float("Input DropOut ratio.", rn.gDropOutRatio)
            net.Set_DropOutMethod(enumDropOut, rn.gDropOutRatio)
        
        
        # Caculate proper hyper pameters ---
        DoEvaluate_ProperParams = ri.Ask_YesNo("Auto-caculating proper hyper pameters?", "n")
        if DoEvaluate_ProperParams:
            loop,stepNum,learnRate,lmbda = rf.Evaluate_BestParam_lmbda(
                    net, net.Train, lstTrain[:1000], lstV[:500], loop,stepNum,learnRate,lmbda)
            loop,stepNum,learnRate,lmbda = rf.Evaluate_BestParam_learnRate(
                    net, net.Train, lstTrain[:1000], lstV[:500], loop,stepNum,learnRate,lmbda)
        else:      
            loop,stepNum,learnRate,lmbda = rf.Ask_Input_SGD(loop,stepNum,learnRate,lmbda)
        
        print( "Hyper pameters: Loop({}), stepNum({}), learnRatio({}), lmbda({})\n".format(loop,stepNum,learnRate,lmbda)  )
    
    
        # Start Training-
        initialWeights = True
        keepTraining = True
        while (keepTraining):
            start = time.time()   
            net.Train(lstTrain, loop, stepNum, learnRate, lstV, lmbda, initialWeights )
            initialWeights = False
        
            dT = time.time()-start
            
            fnSaved = rf.Save_NetworkDataFile(net, fnNetworkData, 
                loop,stepNum,learnRate,lmbda, dT, ".cnn")
            
            keepTraining = ri.Ask_YesNo("Keep Training?", "y")
    
   
    print("Filter Share Weights = {}\n".format(rn.gFilterShareWeights) )

    
    # Ask DoPredict----------------------------------------------------
    DoPredict=True
    if DoPredict:          
        if (os.path.isfile(fnSaved)): 
            fn1 = fnSaved
        else:
            fn1= ".\\NetData\\{}_CNN.cnn".format(rn.RvNeuralNetwork.__name__)
        rn.Debug_Plot = True #ri.Ask_YesNo("Plot Digits?", "n") 
    #    Predict_Digits(net, lstT)
        rf.Predict_Digits_FromNetworkFile(fn1, lstT, rn.Debug_Plot)    
    
    
    
    
    
#%% Test Section *********************************************************************
    
#Test RvNeuralLayer --------------------------------------
#rvLyr = RvNeuralLayer([30,10])
#rvLyr1 = RvNeuralLayer(10, 20)

#測試 RvNeuralNetwork() overload Constructor ---------------    
#lyrsNeus = [784,50,10]
#rvNeuLyrs = RvNeuralNetwork.LayersNeurons_To_RvNeuralLayers(lyrsNeus)
#net = RvNeuralNetwork(rvNeuLyrs)    
#net = RvNeuralNetwork.Class_Create_LayersNeurons(lyrsNeus)    
#net = RvNeuralNetwork(lyrsNeus)    
    
    
    
#print(ac.EnumActivation.afReLU)  #EnumActivation.afReLU
#print(ac.EnumActivation.afReLU.name)   #afReLU
#print(ac.EnumActivation.afReLU.value)  #2
#print(type(ac.EnumActivation.afReLU))  #<enum 'EnumActivation'>
#print(type(ac.EnumActivation.afReLU.name)) #<class 'str'>
#print(type(ac.EnumActivation.afReLU.value))    #<class 'int'>




#%% Main Section ***************************************************************    
Main()
    
    
    