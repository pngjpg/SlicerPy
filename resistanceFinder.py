# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 10:55:44 2020

@author: Brian Minnick
"""
import numpy as np
from itertools import combinations
from collections import OrderedDict
import math
import random

motorRotationsPerMM = 10 #currently, the program assumes this value is the same for all axes.
maximumSurfaceSpeed = 3 #the surface speed of the hotend in mm/s

enableDoubleActivations = True
enableTripleActivations = True
enableQuadrupleActivations = False

inputVoltage = 30 #vi
motorResistance = 7.8
cutSwitchResistance = 8 #The cut switch adds a resistor in parallel with the motor to cur the current in half, This is to even out the distribution of speeds
#potResistances = [50.0,35.0,20.0,8.0,2.0,0.1]
potResistances = [52.54, 36.92, 37.65, 21.58, 4.56, 7.63]

n = 100 # the total population size

def generateStartingPopulation (n, potResistances):
    output = list()
    for index in range(n):
        mutatedResistances = mutate(potResistances)
        output.append(mutatedResistances)
    return output
    
def mutate(potResistances):
    output = list()
    for element in potResistances:
        r = random.randrange(-100,100)/100
        element += r
        output.append(element)
    returned = checkResistances(output)
    return returned

def checkResistances(potResistances):
    output = list()
    for element in potResistances:
        if element < 0.1:
            output.append(0.1)
        else:
            output.append(round(element,2))
    return output

def mutateList(population):
    output = list()
    for element in population:
        returned = mutate(element)
        returned = checkResistances(returned)
        output.append(returned)
    return output

def computeSpeeds(potResistances, indexPlot, plotHist):
    #      Controller         Motor 
    # +Vi -----|==|-----o-----|==|--- +0
    #                   |Vmot
    
    #keys are the resulting voltage, values are the combination of activated channels that result in that voltage
    #voltages = {'0': [0,0,0,0,0,0,0]}
    currents = {'0': [0,0,0,0,0,0,0]}
    
    #single activation voltages
    for positions in combinations(range(6), 1):
        p = [0] * 7
        Rlist = []
        for i in positions:
            p[i] = 1
            Rlist.append(potResistances[i])
        R1 = (1/((1/Rlist[0]))) #the resistance of all activated channels are added using the parallel resistance equation
        current = inputVoltage/(R1+motorResistance)
        currents[current] = p 
        # voltage = inputVoltage-(inputVoltage*(R1/(R1+motorResistance)))
        # voltages[voltage] = p         
    
    for positions in combinations(range(6), 1):
        p = [0] * 7
        Rlist = []
        for i in positions:
            p[i] = 1
            Rlist.append(potResistances[i])
        p[6] = 1
        R1 = (1/((1/Rlist[0]))) #the resistance of all activated channels are added using the parallel resistance equation
        R2 = (1/((1/motorResistance)+(1/cutSwitchResistance))) #the resistance of the motor and cutswitch in parallel is calculated
        current = inputVoltage/(R1+R2)
        currents[current*(motorResistance/(motorResistance+cutSwitchResistance))] = p #The current is cut in half (roughly) by the bypass resistor
        # voltage = inputVoltage-(inputVoltage*(R1/(R1+R2))) #the voltage drop across the first resistors is calculated.
        # voltages[voltage*(motorResistance/(motorResistance+cutSwitchResistance))] = p #Since the current is cut in half due to the cut switch in parallel, the "apparent" voltage to achieve the same current without the cut switch is half.
    
    #Controller__________  
    #        v          v 
    #              r1       Motor     
    #        o----|==|---o---|==|---- +0v
    # +Vi ---|     r2    |
    #        o----|==|---o
    #                    |Vmot
    
    if enableDoubleActivations:
        for positions in combinations(range(6), 2):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            R1 = (1/((1/Rlist[0])+(1/Rlist[1])))
            current = inputVoltage/(R1+motorResistance)
            currents[current] = p 
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+motorResistance)))
            # voltages[voltage] = p
            
        for positions in combinations(range(6), 2):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            p[6] = 1
            R1 = (1/((1/Rlist[0])+(1/Rlist[1]))) #the resistance of all activated channels are added using the parallel resistance equation
            R2 = (1/((1/motorResistance)+(1/cutSwitchResistance))) #the resistance of the motor and cutswitch in parallel is calculated
            current = inputVoltage/(R1+R2)
            currents[current*(motorResistance/(motorResistance+cutSwitchResistance))] = p #The current is cut in half (roughly) by the bypass resistor
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+R2))) #the voltage drop across the first resistors is calculated.
            # voltages[voltage*(motorResistance/(motorResistance+cutSwitchResistance))] = p #Since the current is cut in half due to the cut switch in parallel, the "apparent" voltage to achieve the same current without the cut switch is half.
    
    #Controller__________  
    #        v          v 
    #              r1       Motor     
    #        o----|==|---o---|==|---- +0v
    # +Vi ---|     r2    | 
    #        o----|==|---o
    #        |     r3    |
    #        o----|==|---o
    #                    |Vmot
    
    #triple activation voltages              
    if enableTripleActivations:
        for positions in combinations(range(6), 3):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            R1 = (1/((1/Rlist[0])+(1/Rlist[1])+(1/Rlist[2])))
            current = inputVoltage/(R1+motorResistance)
            currents[current] = p 
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+motorResistance)))
            # voltages[voltage] = p
            
        for positions in combinations(range(6), 3):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            p[6] = 1
            R1 = (1/((1/Rlist[0])+(1/Rlist[1])+(1/Rlist[2]))) #the resistance of all activated channels are added using the parallel resistance equation
            R2 = (1/((1/motorResistance)+(1/cutSwitchResistance))) #the resistance of the motor and cutswitch in parallel is calculated
            current = inputVoltage/(R1+R2)
            currents[current*(motorResistance/(motorResistance+cutSwitchResistance))] = p #The current is cut in half (roughly) by the bypass resistor
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+R2))) #the voltage drop across the first resistors is calculated.
            # voltages[voltage*(motorResistance/(motorResistance+cutSwitchResistance))] = p #Since the current is cut in half due to the cut switch in parallel, the "apparent" voltage to achieve the same current without the cut switch is half.
            
    #quadruple activation voltages
    if enableQuadrupleActivations:
        for positions in combinations(range(6), 4):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            R1 = (1/((1/Rlist[0])+(1/Rlist[1])+(1/Rlist[2])+(1/Rlist[3])))
            current = inputVoltage/(R1+motorResistance)
            currents[current] = p 
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+motorResistance)))
            # voltages[voltage] = p
            
        for positions in combinations(range(6), 4):
            p = [0] * 7
            Rlist = []
            for i in positions:
                p[i] = 1
                Rlist.append(potResistances[i])
            p[6] = 1
            R1 = (1/((1/Rlist[0])+(1/Rlist[1])+(1/Rlist[2])+(1/Rlist[3]))) #the resistance of all activated channels are added using the parallel resistance equation
            R2 = (1/((1/motorResistance)+(1/cutSwitchResistance))) #the resistance of the motor and cutswitch in parallel is calculated
            current = inputVoltage/(R1+R2)
            currents[current*(motorResistance/(motorResistance+cutSwitchResistance))] = p #The current is cut in half (roughly) by the bypass resistor
            # voltage = inputVoltage-(inputVoltage*(R1/(R1+R2))) #the voltage drop across the first resistors is calculated.
            # voltages[voltage*(motorResistance/(motorResistance+cutSwitchResistance))] = p #Since the current is cut in half due to the cut switch in parallel, the "apparent" voltage to achieve the same current without the cut switch is half.
    
    # now, the currents calculated above are normalized into motor speed values.
    
    speeds = list()
    maximumSpeed = 1800 #maximum observed speed in RPM. This can include gear reduction
    minimumSpeed = None
    minimumMotorCurrent = min(currents, key=float) #TODO: determine minimum opperational voltage
    maximumMotorCurrent = max(currents, key=float)
    
    for key in currents:
        IRatio = float(key)/maximumMotorCurrent
        rotationSpeed = ((IRatio*maximumSpeed)*(1/motorRotationsPerMM))/60 #mm/s
        speeds.append(rotationSpeed)
    
    #ganerate the histogram
    import matplotlib.pylab as plt
    if indexPlot ==20 and plotHist:
        x = list()
        for key in speeds: x.append(key)
        plt.axes(ylim =(0, 45))
        plt.hist(x, bins=10)
        plt.title("Histogram of Currents (%i total)" % len(speeds))
        plt.xlabel("Motor Current (mm/s)")
        plt.ylabel("Frequency")
        plt.show()
        print(potResistances)
    
    # calculate the distribution of speeds
    hist,bin_edges = np.histogram(speeds, 10)
    cumulativeSquaredError = 0
    for value in hist:
        cumulativeSquaredError += pow((8.3-value), 2)
    meanSquaredError = cumulativeSquaredError/len(speeds)
    
    return hist, cumulativeSquaredError, meanSquaredError
    
#distribution, CSE, MSE = computeSpeeds(potResistances)
    
def computeGeneration(population, indexA):
    distributionList = list()
    cumulativeSquaredErrorList = list()
    meanSquaredErrorDict = dict()
    
    for index, element in enumerate(population):
        if indexA % 100 == 50:
            if index == 20:
                d,c,m = computeSpeeds(element, index, True)
            else:
                d,c,m = computeSpeeds(element, index, False)
        else:
            d,c,m = computeSpeeds(element, index, False)
        distributionList.append(d)
        cumulativeSquaredErrorList.append(c)
        m=logValue(m, meanSquaredErrorDict)
        meanSquaredErrorDict[m] = element
    
    return meanSquaredErrorDict

def logValue(m, meanSquaredErrorDict):
    try:
        temp = meanSquaredErrorDict[m]
        return logValue(m+0.0000001, meanSquaredErrorDict)
    except:
        return m

def killOff(meanSquaredErrorDict):
    output = dict()
    outputList = list()
    for x in range(int(len(meanSquaredErrorDict)/2)):
        #print(x)
        minimum = min(meanSquaredErrorDict)
        output[minimum] = meanSquaredErrorDict[minimum]
        meanSquaredErrorDict.pop(minimum)
    outputList = list(output.values())
    return outputList

def repopulate(population):
    output = list()
    for element in population:
        newElement = mutate(element)
        output.append(element)
        output.append(newElement)
    return output

population = generateStartingPopulation(n, potResistances)
for x in range(10000):
    meanSquaredErrorDict = computeGeneration(population, x)
    mseWatch = list(meanSquaredErrorDict.keys())
    population = killOff(meanSquaredErrorDict)
    population = repopulate(population)
    if x % 100 == 0:
        print(x)
    # meanSquaredErrorList.sort()
#print(speeds)

# speeds, x, y = computeSpeeds(population[0])

# #ganerate the histogram
# import matplotlib.pylab as plt
# x = list()
# for key in speeds: x.append(key)
# plt.hist(x, bins=10)
# plt.title("Histogram of Currents (%i total)" % len(speeds))
# plt.xlabel("Motor Current (mm/s)")
# plt.ylabel("Frequency")
# plt.show()
