# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 17:27:54 2020

@author: Brian Minnick
"""
#master parameters
#part 1

#part 2
enableDoubleActivations = True
enableTripleActivations = True
enableQuadrupleActivations = False

#part 3
maximumSpeed = 1800 #maximum observed speed in RPM. This can include gear reduction
minimumSpeed = None
minimumVoltage = None #TODO: determine minimum opperational voltage
useDebugSpeedList = False
maximumItt = 100

#part 4
motorRotationsPerMM = 10 #currently, the program assumes this value is the same for all axes.
maximumSurfaceSpeed = 3 #the surface speed of the hotend in mm/s

#part 5
extruderXmmPerEmm = 21.55 #mm of X axis movement per mm of E axis movement on belt printer
slotBufferLength = 2 #in mm. this value accounts for the arm not making contact at the very start of the slot
stripFeedRate = 1 #in mm/s. the rate at which the data strip is fed through the mechanism

#part 6
xDrawOffset = 10 #offset within Tkinter window to draw paths
yDrawOffset = 600
drawScale = 2 #scaling factor all points are multiplied by to display. Does not effect model
learningRate = 0.001
drawRed = True
drawGreen = True
drawBlack = True

#part 7

#part 8

#=================================Part 1=======================================

#First, the GCode file is opened and looped through to detect important lines
rawGCodeFile = open("input.gcode", "r")
absXPoints = [0] #the desired X Coordinate of the hotend 
absYPoints = [0]
absZPoints = [0]
extruderActive = []

for line in rawGCodeFile:
    if((line[:2] == "G1")or(line[:2] == "G0")):
        temporarySplitLine = line.split(" ")
        xHit = False#used to ensure each G1 or G0 line is give a full XYZ point even if a word doesn't exist
        yHit = False
        zHit = False
        eHit = False
        for word in temporarySplitLine: #A word is each space seperated element in a GCode line
            if (word[:1] == ";"):
                break
            elif (word[:1] == "X"):
                absXPoints.append(word[1:])
                xHit = True
            elif (word[:1] == "Y"):
                absYPoints.append(word[1:])
                yHit = True
            elif (word[:1] == "Z"):
                absZPoints.append(word[1:])
                zHit = True
            elif (word[:1] == "E"):
                if (word[:2] == "E-"):
                    extruderActive.append(-1)
                else:
                    extruderActive.append(1)
                eHit = True
        if not xHit:
            absXPoints.append(absXPoints[len(absXPoints)-1])
        if not yHit:
            absYPoints.append(absYPoints[len(absYPoints)-1])
        if not zHit:
            absZPoints.append(absZPoints[len(absZPoints)-1])
        if not eHit:
            extruderActive.append(0)
print("End Part 1")

#=================================Part 2=======================================

#Now, the output voltage of all possible combinations of voltage dividers will be calculated. REQUIRES TUNING
import numpy
from itertools import combinations
from collections import OrderedDict

inputVoltage = 25 #Vi

R1list = []
R2list = []

#             Z1            Z2 
# +Vi -----|==|-----o-----|==|--- +0
#                    |Vout

ohmRatios = numpy.array([[0.001,11],#REQUIRES TUNING
                         [0.5,10.5],
                         [1,10], #fist value is the resistance of Z1
                         [3,8], #second value is the resistance of Z2
                         [7,4],
                         [8,3],
                         [9,2],])

#keys are the resulting voltage, values are the combination of activated chanels that result in that voltage
voltages = {'0': [0,0,0,0,0,0,0]}

#single activation voltages
for positions in combinations(range(7), 1):
        p = [0] * 7
        R1list = []
        R2list = []
        for i in positions:
            p[i] = 1
            R1list.append(ohmRatios[i,0])
            R2list.append(ohmRatios[i,1])
        R1 = (1/((1/R1list[0])))
        R2 = (1/((1/R2list[0])))
        voltage = (R2/(R1+R2))*inputVoltage
        voltages[voltage] = p

#     R1 ___________  ___________ R2
#        v          v v         v
#              r1         r3     
#        o----|==|---o---|==|----o
# +Vi ---|     r2    |    r4     |--- +0v
#        o----|==|---o---|==|----o
#                    |Vout

if enableDoubleActivations:
    for positions in combinations(range(7), 2):
        p = [0] * 7
        R1list = []
        R2list = []
        for i in positions:
            p[i] = 1
            R1list.append(ohmRatios[i,0])
            R2list.append(ohmRatios[i,1])
        R1 = (1/((1/R1list[0])+(1/R1list[1])))
        R2 = (1/((1/R2list[0])+(1/R2list[1])))
        voltage = (R2/(R1+R2))*inputVoltage
        voltages[voltage] = p

#     R1 ___________  ___________ R2
#        v          v v         v
#              r1         r4     
#        o----|==|---o---|==|----o
# +Vi ---|     r2    |    r5     |--- +0v
#        o----|==|---o---|==|----o
#        |     r3    |    r6     |
#        o----|==|---o---|==|----o
#                    |Vout

#triple activation voltages              
if enableTripleActivations:
    for positions in combinations(range(7), 3):
        p = [0] * 7
        R1list = []
        R2list = []
        for i in positions:
            p[i] = 1
            R1list.append(ohmRatios[i,0])
            R2list.append(ohmRatios[i,1])
        R1 = (1/((1/R1list[0])+(1/R1list[1])+(1/R1list[2])))
        R2 = (1/((1/R2list[0])+(1/R2list[1])+(1/R2list[2])))
        voltage = (R2/(R1+R2))*inputVoltage
        voltages[voltage] = p
        
#quadruple activation voltages
if enableQuadrupleActivations:
    for positions in combinations(range(7), 4):
        print("hit")
        p = [0] * 7
        R1list = []
        R2list = []
        for i in positions:
            p[i] = 1
            R1list.append(ohmRatios[i,0])
            R2list.append(ohmRatios[i,1])
        R1 = (1/((1/R1list[0])+(1/R1list[1])+(1/R1list[2])+(1/R1list[3])))
        R2 = (1/((1/R2list[0])+(1/R2list[1])+(1/R2list[2])+(1/R2list[3])))
        voltage = (R2/(R1+R2))*inputVoltage
        voltages[voltage] = p
voltagesSorted = OrderedDict(sorted(voltages.items(), key=lambda x:x[1], reverse=True))

print("End Part 2")
#=================================Part 3=======================================
#We must determine the rotation speed of the motor at a given voltage
speeds = {0.0: [0,0,0,0,0,0,0]}
maximumSpeed = 1800 #maximum observed speed in RPM. This can include gear reduction
minimumSpeed = None
minimumVoltage = None #TODO: determine minimum opperational voltage

if not useDebugSpeedList:
    for key in voltages:
        vRatio = float(key)/inputVoltage
        rotationSpeed = ((vRatio*maximumSpeed)*(1/motorRotationsPerMM))/60 #mm/s
        speeds[rotationSpeed] = voltages[key]
    speedsSorted = OrderedDict(sorted(speeds.items(), key=lambda x:x[1], reverse=True))
else:
    for x in range(maximumItt):
        rotationSpeed = maximumSurfaceSpeed*((x+1)/maximumItt)
        speeds[rotationSpeed] = [1]
    speedsSorted = OrderedDict(sorted(speeds.items(), key=lambda x:x[1], reverse=True))
print("End Part 3")

#=================================Part 4=======================================
#Now using the rotation speeds and the points from the GCode file, the duration of each movement can be calculated.
#along with that, the voltage on each motor is calculated and the corresponding channels are selected
import math
import bisect 

movementDurations = list()
closestSpeeds = list(list())
closestActivatedChanels = list(list())
requestedSpeeds = list(list())

for index in range(len(absXPoints)):
    if index == 0:
        pass
    else:
        try:
            previousXPos = float(absXPoints[index-1])
            previousYPos = float(absYPoints[index-1])
            previousZPos = float(absZPoints[index-1])
            currentXPos = float(absXPoints[index])
            currentYPos = float(absYPoints[index])
            currentZPos = float(absZPoints[index])
            deltaX = currentXPos - previousXPos
            deltaY = currentYPos - previousYPos
            deltaZ = currentZPos - previousZPos
            deltaC = math.sqrt((pow(deltaX, 2)+(pow(deltaY, 2))+(pow(deltaZ, 2))))
            movementDuration = deltaC/maximumSurfaceSpeed
            movementDurations.append(movementDuration) #movement duration in seconds
        except:
            break
        try:
            XReqSpeed = (deltaX/movementDuration)*0.999 #this multiple is needed or else the binary search can return a value not in the speed list
            YReqSpeed = (deltaY/movementDuration)*0.999
            ZReqSpeed = (deltaZ/movementDuration)*0.999
            
            minimumDifference = 1000
            closestSpeedX = -1000
            for key in speeds: #TODO: This is horribly inefficient, someone fix me! Binary search?
                difference = abs(abs(XReqSpeed) - float(key))
                if difference < minimumDifference:
                    minimumDifference = difference
                    closestSpeedX = key
            
            
            minimumDifference = 1000
            closestSpeedY = -1000
            for key in speeds: #TODO: This is horribly inefficient, someone fix me! Binary search?
                difference = abs(abs(YReqSpeed) - float(key))
                if difference < minimumDifference:
                    minimumDifference = difference
                    closestSpeedY = key
            
            minimumDifference = 1000
            closestSpeedZ = -1000
            for key in speeds: #TODO: This is horribly inefficient, someone fix me! Binary search?
                difference = abs(abs(ZReqSpeed) - float(key))
                if difference < minimumDifference:
                    minimumDifference = difference
                    closestSpeedZ = key
            
            if closestSpeedX == -1000:
                closestSpeedX = 0
            if closestSpeedY == -1000:
                closestSpeedY = 0
            if closestSpeedZ == -1000:
                closestSpeedZ = 0
            
            # closestSpeedX = min(speeds.keys(), key = lambda key: abs(key-XReqSpeed))
            # closestSpeedY = min(speeds.keys(), key = lambda key: abs(key-YReqSpeed))
            # closestSpeedZ = min(speeds.keys(), key = lambda key: abs(key-ZReqSpeed))
            
            # closestSpeedIndexX = bisect.bisect_left(list(speedsSorted.keys()), abs(XReqSpeed))
            # closestSpeedIndexY = bisect.bisect_left(list(speedsSorted.keys()), abs(YReqSpeed))
            # closestSpeedIndexZ = bisect.bisect_left(list(speedsSorted.keys()), abs(ZReqSpeed))
            # speedsList = list(speedsSorted.keys())
            # closestSpeedX = speedsList[closestSpeedIndexX]
            # closestSpeedY = speedsList[closestSpeedIndexY]
            # closestSpeedZ = speedsList[closestSpeedIndexZ]
                
            requestedSpeeds.append([XReqSpeed, YReqSpeed, ZReqSpeed])
            closestSpeeds.append([closestSpeedX, closestSpeedY, closestSpeedZ])
            closestActivatedChanels.append([speeds[closestSpeedX], speeds[closestSpeedY], speeds[closestSpeedZ]])
        except:
            print("Extrusion only move detected at line %i, removing this line for now" % index)
            absXPoints.pop(index)
            absYPoints.pop(index)
            absZPoints.pop(index)
            extruderActive.pop(index)
            
print("End Part 4")

#=================================Part 5=======================================
#now, the data strip is compilled into one big, happy list.
currentXPosition = 10
currentYPosition = 10
currentEPosition = 0
fullDataStripSegment = []
completeDataStrip = list(list())

for index, chanelSet in enumerate(closestActivatedChanels):
    fullDataStripSegment = []
    for chanel in chanelSet[0]:
        fullDataStripSegment.append(chanel)
    for chanel in chanelSet[1]:
        fullDataStripSegment.append(chanel)
    for chanel in chanelSet[2]:
        fullDataStripSegment.append(chanel)
    for x in range(3):
        if(requestedSpeeds[index][x] < 0):
            fullDataStripSegment.append(1)
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(1)
            fullDataStripSegment.append(0)
        elif(requestedSpeeds[index][x] > 0):
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(1)
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(1)
        elif(requestedSpeeds[index][x] == 0):
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(0)
            fullDataStripSegment.append(0)
    if(extruderActive[index] < 0):
        fullDataStripSegment.append(1)
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(1)
        fullDataStripSegment.append(0)
    if(extruderActive[index] > 0):
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(1)
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(1)
    elif(extruderActive[index] == 0):
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(0)
        fullDataStripSegment.append(0)
    completeDataStrip.append(fullDataStripSegment)
print("End Part 5")

#=================================Part 6=======================================
#the propagated data strip coordinates are compared to the ground truth file
#the ground truth and propagated coordinates are displayed.
#a custom gradient descent algorithm is applied to minimize error in the data strip
import tkinter as tk

propagatedCoordinates = [0,0,0]
currentPos = [0,0,0]
oldPropagatedCoordinates = [0,0,0]
oldAbsoluteCoordinates = [0,0,0]
oldAfterGradientDescentPropagatedCoordinates = [0,0,0]
afterGradientDescentPropagatedCoordinates = [0,0,0]
summedErrorAGD = [0,0,0]
summedErrorBGD = [0,0,0]
agdCoordinateList = list(list())
bgdCoordinateList = list(list())
updatedMovementDurations = list()
window = tk.Tk()
canvas = tk.Canvas(window,width=800,height=800)

def getCurrentAbsolutePosition (index):
    coordinate = list()
    coordinate.append(float(absXPoints[index]))
    coordinate.append(float(absYPoints[index]))
    coordinate.append(float(absZPoints[index]))
    return coordinate
def subtractLists (l1, l2):
    l1 = [float(item) for item in l1]
    l2 = [float(item) for item in l2]
    output = list()
    for i in range(len(l1)):
        output.append(l1[i]-l2[i])
    return output
def addLists (l1, l2):
    output = list()
    for i in range(len(l1)):
        output.append(l1[i]+l2[i])
    return output
def divideList (l1, div):
    output = list()
    for i in range(len(l1)):
        output.append(l1[i]/div)
    return output
def squareList (l1):
    output = list()
    for i in range(len(l1)):
        output.append(pow(l1[i],2))
    return output
def rootList (l1):
    output = list()
    for i in l1:
        output.append(l1[i])
def calculateError(currentPos, propagatedCoordinates):
    delta = subtractLists(currentPos, propagatedCoordinates)
    squaredError = squareList(delta)
    return squaredError


for index, closestSpeedList in enumerate(closestSpeeds):
    #calculate the toolhead position from the datastrip
    oldPropagatedCoordinates = propagatedCoordinates
    oldAfterGradientDescentPropagatedCoordinates = afterGradientDescentPropagatedCoordinates
    offsetComponents = list()
    for x in range(3):
        if requestedSpeeds[index][x] < 0:
            offsetComponents.append((-1)*(float(closestSpeedList[x])*movementDurations[index]))
        else:
            offsetComponents.append(float(closestSpeedList[x])*movementDurations[index])
    propagatedCoordinates = addLists(propagatedCoordinates, offsetComponents)
    currentPos = getCurrentAbsolutePosition(index) #the ground truth coordinate
    try:
        nextPos = getCurrentAbsolutePosition(index+1)
        if drawRed:
            canvas.create_line((xDrawOffset+oldPropagatedCoordinates[0])*drawScale, (yDrawOffset+(-1*oldPropagatedCoordinates[1]))*drawScale, (xDrawOffset+propagatedCoordinates[0])*drawScale, (yDrawOffset+(-1*propagatedCoordinates[1]))*drawScale, fill = 'red')
        if drawBlack:
            canvas.create_line((xDrawOffset+oldAbsoluteCoordinates[0])*drawScale, (yDrawOffset+(-1*oldAbsoluteCoordinates[1]))*drawScale, (xDrawOffset+currentPos[0])*drawScale, (yDrawOffset+(-1*currentPos[1]))*drawScale)
        
        #calculate error
        beforeGradientDescentError = calculateError(nextPos, propagatedCoordinates)
        summedErrorBGD = addLists(summedErrorBGD, beforeGradientDescentError)
        
        # correct for this error and regenerate movement duration list using gradient descent
        
        # the gradient function is the following:
        # dJ/dt= [-2Sx][Xc-Xl-Sxt]+[-2Sy][Yc-Yl-Syt] / 2 sqrt([Xc-Xl-Sxt]^2 + [Yc-Yl-Syt]^2)
        
        gradient = 10
        newMovementDuration = movementDurations[index]
        counter = 0 #ensure that the correction loop is finite. Normally, the gradient reaches the cutoff threshold before the counter reaches 100
        while abs(gradient) > 0.1 and counter < 100:
            # gradient = 2*((-1*nextPos[1]*requestedSpeeds[index][1])-(nextPos[0]*requestedSpeeds[index][0])+(oldPropagatedCoordinates[1]*requestedSpeeds[index][1])+(oldPropagatedCoordinates[0]*requestedSpeeds[index][0])+(pow(requestedSpeeds[index][1],2)*newMovementDuration)+(pow(requestedSpeeds[index][0],2)*newMovementDuration))
            
            numerator = (((-2*requestedSpeeds[index][0])*(nextPos[0] - (oldAfterGradientDescentPropagatedCoordinates[0] + (requestedSpeeds[index][0]*newMovementDuration))))-((2*requestedSpeeds[index][1])*(nextPos[1] - (oldAfterGradientDescentPropagatedCoordinates[1] + (requestedSpeeds[index][1]*newMovementDuration))))) 
            gradient = numerator
            newMovementDuration -= learningRate*gradient
            counter +=1
        
        #replace movement duration within list with the optimized value
        updatedMovementDurations.append(newMovementDuration)
        
        #recalculate movement with the new movement duration
        offsetComponents = list()
        for x in range(3):
            if requestedSpeeds[index][x] < 0:
                offsetComponents.append((-1)*(float(closestSpeedList[x])*updatedMovementDurations[index]))
            else:
                offsetComponents.append(float(closestSpeedList[x])*updatedMovementDurations[index])
        
        #draw optimized movment to screen in green
        afterGradientDescentPropagatedCoordinates = addLists(afterGradientDescentPropagatedCoordinates, offsetComponents)
        if drawGreen:
            canvas.create_line((xDrawOffset+oldAfterGradientDescentPropagatedCoordinates[0])*drawScale, (yDrawOffset+(-1*oldAfterGradientDescentPropagatedCoordinates[1]))*drawScale, (xDrawOffset+afterGradientDescentPropagatedCoordinates[0])*drawScale, (yDrawOffset+(-1*afterGradientDescentPropagatedCoordinates[1]))*drawScale, fill = 'green')
        
        #calculate error after gradient descent applied
        afterGradientDescentError = calculateError(nextPos, afterGradientDescentPropagatedCoordinates)
        summedErrorAGD = addLists(summedErrorAGD, afterGradientDescentError)
        oldAbsoluteCoordinates = currentPos
        
        agdCoordinateList.append(afterGradientDescentPropagatedCoordinates)
        bgdCoordinateList.append(propagatedCoordinates)

    except:
        print("\n\nThis should not be happening, what did you do?\n\n")
        break
    
cumulativeErrorBGD = subtractLists(getCurrentAbsolutePosition(len(closestSpeeds)), propagatedCoordinates)
MSErrorBGD = divideList(summedErrorBGD, len(closestSpeeds)+1)       
cumulativeErrorAGD = subtractLists(getCurrentAbsolutePosition(len(closestSpeeds)), afterGradientDescentPropagatedCoordinates)
MSErrorAGD = divideList(summedErrorAGD, len(closestSpeeds)+1)
print("----Before Gradient Descent (RED) Propagated Points")
print("    Mean Squared Error (X): %f" % pow(MSErrorBGD[0],0.5))
print("    Mean Squared Error (Y): %f" % pow(MSErrorBGD[1],0.5))
# print("    Mean Squared Error (Z): %f" % pow(MSErrorBGD[2],0.5))
print("    Cumulative Error (X): %fmm" % cumulativeErrorBGD[0])
print("    Cumulative Error (Y): %fmm" % cumulativeErrorBGD[1])
# print("    Cumulative Error (Z): %fmm" % cumulativeErrorBGD[2])
print("\n----After Gradient Descent (GREEN) Propagated Points")
print("    Mean Squared Error (X): %f" % pow(MSErrorAGD[0],0.5))
print("    Mean Squared Error (Y): %f" % pow(MSErrorAGD[1],0.5))
# print("    Mean Squared Error (Z): %f" % pow(MSErrorAGD[2],0.5))
print("    Cumulative Error (X): %fmm" % cumulativeErrorAGD[0])
print("    Cumulative Error (Y): %fmm" % cumulativeErrorAGD[1])
# print("    Cumulative Error (Z): %fmm" % cumulativeErrorAGD[2])

print("End Part 6")

#=================================Part 7=======================================
    #write gcode to file
outputFile = open("output.gcode", "a+") #TODO: update GCode header to match belt printer
outputFile.seek(0)
outputFile.truncate()
outputFile.write(";GCode file generated by SlicerPy 2020 written by Brian Minnick\n")
outputFile.write("T0\n")                      #select tool 0
outputFile.write("M104 S200\n")               #set temp
outputFile.write("M109 S200\n")               #wait for temp
outputFile.write("M82\n")                     #absolute mode
outputFile.write("G28\n")                     #home
outputFile.write("M375 P\"heightmap.csv\"\n") #load heightmap
outputFile.write("G92 E0\n")                  #set extruder position to 0
outputFile.write("G1 F3600 E-6.5\n")          #retract filament
outputFile.write("G0 F1714.3 X10 Y10 Z0.3\n") #move to starting location
outputFile.write("M204 S1100\n")              #set maximum acceleration
outputFile.write("G1 F3600 E0\n")             #undo retract filament

for index, row in enumerate(completeDataStrip):
    extrudeAmountX = 185.5/extruderXmmPerEmm
    currentEPosition += extrudeAmountX
    outputFile.write(str("G1 X195.5 E%f\n" % (currentEPosition)))
    totalSlotHeight = (slotBufferLength)+(stripFeedRate*movementDurations[index])
    extrudeAmountY = totalSlotHeight/extruderXmmPerEmm
    currentXPosition = 195.5
    for chanelIndex, chanel in enumerate(reversed(row)):
        if chanel == 0:
            currentXPosition -=1.9
            outputFile.write("G0 X%f\n" % (currentXPosition))
            currentYPosition += totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=0.4
            outputFile.write("G0 X%f\n" % (currentXPosition))
            currentYPosition -= totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=0.4
            outputFile.write("G0 X%f\n" % (currentXPosition))
            currentYPosition += totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=0.4
            outputFile.write("G0 X%f\n" % (currentXPosition))
            currentYPosition -= totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=1.9
            outputFile.write("G0 X%f ;end of chanel value 0\n" % (currentXPosition))
        if chanel == 1:
            currentXPosition -=0.2
            outputFile.write("G0 X%f ;end of chanel value 0\n" % (currentXPosition))
            currentYPosition += totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=4.6
            outputFile.write("G0 X%f\n" % (currentXPosition))
            currentYPosition -= totalSlotHeight
            currentEPosition += extrudeAmountY
            outputFile.write("G1 Y%f E%f\n" % (currentYPosition, currentEPosition))
            currentXPosition -=0.2
            outputFile.write("G0 X%f ;end of chanel value 0\n" % (currentXPosition))
    currentYPosition += totalSlotHeight
    currentXPosition = 10
    outputFile.write("G0 Y%f X%f ;end of row\n" % (currentYPosition, currentXPosition))
outputFile.close()
print("End Part 7")

#=================================Part 8=======================================
#define the window tools

def xPlus100():
    global xDrawOffset
    xDrawOffset += 100
    reDraw()
    
def xPlus10():
    global xDrawOffset
    xDrawOffset += 10
    reDraw()
    
def reDraw():
    global canvas
    for index in range(len(bgdCoordinateList)):
        if index == 0:
            pass
        else:
            canvas.create_line((xDrawOffset+agdCoordinateList[index-1][0])*drawScale, (yDrawOffset+(-1*agdCoordinateList[index-1][1]))*drawScale, (xDrawOffset+agdCoordinateList[index][0])*drawScale, (yDrawOffset+(-1*agdCoordinateList[index][1]))*drawScale, fill = 'green')
            canvas.create_line((xDrawOffset+bgdCoordinateList[index-1][0])*drawScale, (yDrawOffset+(-1*bgdCoordinateList[index-1][1]))*drawScale, (xDrawOffset+bgdCoordinateList[index][0])*drawScale, (yDrawOffset+(-1*bgdCoordinateList[index][1]))*drawScale, fill = 'red')
            #canvas.create_line((xDrawOffset+agdCoordinateList[index-1][0])*drawScale, (yDrawOffset+(-1*agdCoordinateList[index-1][1]))*drawScale, (xDrawOffset+agdCoordinateList[index][0])*drawScale, (yDrawOffset+(-1*agdCoordinateList[index][1]))*drawScale)
            window.mainloop()
canvas.pack() 


xIncPlus100 = tk.Button(window, command=xPlus100, text="X +100")
xIncPlus100.pack(side=tk.LEFT)
xIncPlus10 = tk.Button(window, command=xPlus10, text="X +10")
xIncPlus10.pack(side=tk.LEFT)

window.mainloop()