import re


class Line:
    def __init__(self, line):
        
        linSep = line.split(":")
        
        self.Frame = linSep[0][:-1]#frame number
        self.X = str(int(linSep[1])+3) #x coord
        self.Y = str(int(linSep[2])+3) #y coord
        #strips numbers out, retuns a list, could be faster.
        tagList = re.split("[0-9]",linSep[-1][:-1])
        self.Tag = ''
        for item in tagList:#combines list into one string
            self.Tag = self.Tag+item
                

            
fileName = raw_input('File Name:')

fo = open(fileName, 'r')#name of file being opened
f2 = open(fileName[:-3]+'CONV.txt','w')#new file of converted coordinates
for line in fo:
    Lstring = Line(line)
    f2.write(Lstring.Tag+', '+Lstring.X+', '+Lstring.Y+', '+Lstring.Frame+'\n')

print "Created file ", (fileName[:-3]+'CONV.txt'), " with converted point list."
print "Format is [Tag], [X], [Y], [Frame]"
fo.close()
f2.close()

