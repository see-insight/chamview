#this works when the chameleon is walking from right to left, could be changed
#to work left to right as well

import os
import math
fileName = raw_input('File Name:')

fo = open(fileName,'r')

cm = 0
sv = 0

RFDic = {}
LFDic = {}
LBDic = {}
RBDic = {}
LeftDic = {}
RightDic = {}
for line in fo:
    linLst = line.split(':')
    #calibration steps
    if 'Cm' in line:
        if cm == 0:
            cmx1 = float(linLst[1])+3.0
            cmy1 = float(linLst[2])+3.0
            cm = cm + 1
        elif cm == 1:
            cmx2 = float(linLst[1])+3.0
            cmy2 = float(linLst[2])+3.0
    if 'GS' in line:
        gx1 = float(linLst[1])+3.0
        gy1 = float(linLst[2])+3.0
    if 'GE' in line:
        gx2 = float(linLst[1])+3.0
        gy2 = float(linLst[2])+3.0
    if 'S/V' in line:
        if sv == 0:
            svx1 = float(linLst[1])+3.0
            svy1 = float(linLst[2])+3.0
            sv = sv + 1
        elif sv == 1:
            svx2 = float(linLst[1])+3.0
            svy2 = float(linLst[2])+3.0
## makes dictionaries of x,y coords for feet, keys are frame numbers
    if 'RF' in line:
        RFDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
        RightDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
    if 'LF' in line:
        LFDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
        LeftDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
    if 'RB' in line:
        RBDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
        RightDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
    if 'LB' in line:
        LBDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
        LeftDic[linLst[0]] = (int(linLst[1])+3,int(linLst[2])+3)
        
fo.close()


#distance formula for cm, gap length, and snout/vent length
cent = math.sqrt(((cmx2-cmx1)*(cmx2-cmx1))+((cmy2-cmy1)*(cmy2-cmy1)))
gap = math.sqrt(((gx2-gx1)*(gx2-gx1))+((gy2-gy1)*(gy2-gy1)))
snVe = math.sqrt(((svx2-svx1)*(svx2-svx1))+((svy2-svy1)*(svy2-svy1)))
gapCm = gap/cent
gapCm = round(gapCm,2)
snVeCm = snVe/cent
snVeCm = round(snVeCm,2)


#sorting, puts steps in order in a new list (tuples)
RFList = []
for key in sorted(RFDic.iterkeys(),reverse=True):
    RFList.insert(0,(key,RFDic[key]))
LFList = []
for key in sorted(LFDic.iterkeys(),reverse=True):
    LFList.insert(0,(key,LFDic[key]))
RBList = []
for key in sorted(RBDic.iterkeys(),reverse=True):
    RBList.insert(0,(key,RBDic[key]))
LBList = []
for key in sorted(LBDic.iterkeys(),reverse=True):
    LBList.insert(0,(key,LBDic[key]))
RightList = []
for key in sorted(RightDic.iterkeys(),reverse=True):
    RightList.insert(0,(key,RightDic[key]))
LeftList = []
for key in sorted(LeftDic.iterkeys(),reverse=True):
    LeftList.insert(0,(key,LeftDic[key]))
           
##print RFList
##print LFList
##print RBList
##print LBList
##print gx2

##print "Left"
##print LeftList
##print "Right"
##print RightList
##print

#find zero step
SumList = [RFList,LFList]
zeroDiff = 2000
zeroFrame = 0
for lis in SumList:
    for item in lis:
        xcor = item[1][0]
        if (xcor <= gx2) and (int(item[0][:-1]) > zeroFrame): #ensures zero step is first one that crosses the gap
            temp = gx2 - xcor
            if abs(temp) < abs(zeroDiff):
                zeroDiff = temp
                zeroStep = xcor
                zeroFrame = int(item[0][:-1]) #saves frame of zero step as integer

##print
##print "Zero Frame: ", zeroFrame

#finds step length             
x = 1
n = len(RightList)
stepDic = {}
if n == len(LeftList): #lists must be same length for now, can change later
    while (x < n):
        step1= abs(LeftList[x][1][0]-RightList[x-1][1][0])#fix to distance formula with y
        step2 = abs(RightList[x][1][0]-LeftList[x-1][1][0])
        step = (step1+step2)/2.0 #avg of back step and front step
        step = step/snVe #step relative to snout/vent length
        step = round(step,2)
        if (RightList[x][1][0] == zeroStep) or (LeftList[x][1][0] == zeroStep):
##            print "Right List: ", RightList[x][1][0]
##            print "Left List: ", LeftList[x][1][0]
            zeroStep = step
##            print "Zero Step: ", zeroStep
        stepDic[x] = step
        x += 1
else:
    print "Error, step lists not same length"
    
##print
##print stepDic
##print "Zero: ", zeroStep
##print
    
#renumbers dictionary keys based on the zero step
fixedStepDic = {}
for key in stepDic: #finds key of zero step
    if stepDic[key] == zeroStep:
        zeroKey = key
        
fixedStepDic[0] = stepDic[zeroKey]

for key in stepDic:
    if key != zeroKey:
        newKey = zeroKey-key
        fixedStepDic[newKey] = stepDic[key]



#prints results in terminal and file, can fix to CSL for excel graph later
fo2 = open(fileName[:-4]+"DATA.txt",'w')
print 
print "Step Length Relative to Snout/Vent:"
fo2.write("Step Length Relative to Snout/Vent:"+"\n")
fStepList = []
for key in sorted(fixedStepDic.iterkeys(),reverse=False):
    fStepList.insert(0,(key,fixedStepDic[key]))
for item in fStepList:
    print item
    fo2.write(str(item)+"\n")
print
print 'One centimeter is equal to:', cent, 'pixels'
fo2.write("\n"+'One centimeter is equal to:'+str(cent)+'pixels'+"\n")
print 'Gap is:', gapCm, 'cm'
fo2.write('Gap is:'+str(gapCm)+'cm'+'\n')
print 'Snout/Vent length is:', snVeCm, 'cm'
fo2.write('Snout/Vent length is:'+str(snVeCm)+'cm'+'\n')
print 
print "Results written to ", (fileName[:-4]+"DATA.txt")
print

fo2.close()
        


