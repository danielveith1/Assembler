'''
Created on May 2, 2013

@author: dan
'''
# mas version 1

import sys      # for command line args
import string
import os
import shutil

def dropTempFile(of):
    of.close()
    os.remove(of)
    
def initOperatorTable(ops):        # [opcode,num operands]
    ops['ld'] = [0x0000,1]
    ops['st'] = [0x1000,1]
    ops['add'] = [0x2000,1]
    ops['sub'] = [0x3000,1]
    ops['ldr'] = [0x4000,1]
    ops['str'] = [0x5000,1]
    ops['addr'] = [0x6000,1]
    ops['subr'] = [0x7000,1]
    ops['ldc'] = [0x8000,1]
    ops['ja'] = [0x9000,1]
    ops['jzop'] = [0xA000,1]
    ops['jn'] = [0xB000,1]
    ops['jz'] = [0xC000,1]
    ops['jnz'] = [0xD000,1]
    ops['call'] = [0xE000,1]
    ops['ret'] = [0xF000,0]
    ops['ldi'] = [0xF100,0]
    ops['sti'] = [0xF200,0]
    ops['push'] = [0xF300,0]
    ops['pop'] = [0xF400,0]
    ops['aloc'] = [0xF500,1]
    ops['dloc'] = [0xF600,1]
    ops['swap'] = [0xF700,0]
    ops['uout'] = [0xFFF5,0]
    ops['sin'] = [0xFFF6,0]
    ops['sout'] = [0xFFF7,0]
    ops['hin'] = [0xFFF8,0]
    ops['hout'] = [0xFFF9,0]
    ops['ain'] = [0xFFFA,0]
    ops['aout'] = [0xFFFB,0]
    ops['din'] = [0xFFFC,0]
    ops['dout'] = [0xFFFD,0]
    ops['bkpt'] = [0xFFFE,0]
    ops['halt'] = [0xFFFF,0]
    ops['dw'] = ['dw',1]
 
    ops['public'] = ['public',1] 
    ops['end'] = ['end',1]
    ops['extern']=['extern',1]
    
def validIdentifier(s):
    if "?" in s:
        return 0
    elif ord(s[:1]) > 64 and ord(s[:1]) < 123:
        return 1
    elif (s[:1]== "$") or (s[:1]== "@"):
        if len(s)==1:
            return 0
        else:
            return 1
    else:
        return 0 
    # checks if a token is a valid identiifer. Must begin with a letter, underscore or $ or @
    # if $ or @ it must have additional characters

def skipLabels(ll):
    x = 0
    while x < len(ll):
        #print x
        if ":" in ll[x]:
            if not ":" in ll[x+1]:
                return x+1
        x+=1
    return 0
    ## ll is a lineList
    ## returns the index of the next token on the line after skipping all labels
    
        
def main():
    print 'masv1 wrtten by Daniel Veith'
    programLines = []    # an array of strings so we only need to open the file once
    locationCounter = 0
    symbolTable = {}  # empty hash
    exSymbolTable = {}
    pubSymbolTable = {}
    xOperators= ('ld','st','add','sub','ldr','str','addr','subr','ldc','ja','jzop','jn','jz','jnz','call')
    yOperators= ('aloc','dloc')
    operators = {} # empty hash
    externalSymbolTable = {}   # empty hash
    initOperatorTable(operators)    # calls that function at top of program
    #print operators         # debug
    operator = ''
    operand = ''
    label = ''
    tokenNdx = 0
    cl = sys.argv    # reads in command line argument list
    cn = len(cl)     # how many tokens in the list
    if cn == 1:
        print "No file name argument"
        return 1
    elif cn > 2:
        print "Too many file name arguments"
        return 1
        
    fileName = cl[1]  # cl[0] is program name
    fileNameList = string.split(fileName,'.')
    if len(fileNameList) == 1:
        fileName = fileName+".mas"
    #print fileName
    # at this point the complete file name is available with .mas extension
    inFile = open(fileName,'r')   # open input file to be read as text
    outFile = open(fileNameList[0]+".tmp",'wb')  # open output file as binary
    outFileTempName = fileNameList[0]+".tmp"  # write to a temp file until successful and then rename
    outFileName = fileNameList[0]
    fileIsMAC = 1  # flag to determine file extension name - .mac or .mob
    
    line = "Z"
    i = 0
    # pass 1
    
    for line in inFile:
        
        #hasOperator = False
        hasOperator = False
        isEnd = False
        isExtern = False
        isPublic = False
        if line.find(";")> -1:
            line = line[:line.find(";")]
        # remove comments before empty lines
        # in case line has only comments. 
        # Then it gets removed as if it were an empty line.
        line = line.strip()    
        
        if line == "":
            continue
        programLines.append("")
        # skip over empty lines
        
        
        
        # remove whitespace prior to any ':' so convert "x    :" into "x:"
        # do it for blank spaces and tabs
        while line.find(" :")>-1:
            line = line.replace(" :", ":")
        # make sure that ":" is followed by a " " so we can tokenize on whitespace
        # so "x:dw 1" becomes "x: dw 1"
        
        lineWOW = string.replace(line,':',': ')

            
        # tokenize the line into a list
        lineList = string.split(lineWOW)  # this time on whitespace
        
    
        for x in lineList:
            if x in operators:
                hasOperator = True
            if x == "extern":
                isExtern = True
            elif x == "public":
                isPublic = True
            elif x == "end":
                isEnd = True
            elif x != "extern" and isExtern:
                exSymbolTable[x]= locationCounter
            elif x != "public" and isPublic:
                pubSymbolTable[x]= locationCounter
            elif x != "end" and isEnd:
                endVar = x
            elif ":" in x:
                
                if validIdentifier(x[:len(x)-1])==1:
                    if x[:len(x)-1] in symbolTable:
                        print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                        print lineWOW
                        print "Duplicate label"
                        sys.exit()
                    
                    symbolTable[x[:len(x)-1]]=locationCounter
                else:
                    print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                    print lineWOW
                    print "Ill-formed label in label field"
                    sys.exit()
        # grab all the labels and put them in the symbol table    
        # quit if label already in the symbol table
        # if line is empty get another line
        # on what is left of the line, get the operator
            if not (isExtern or isPublic): 
                programLines[locationCounter] = programLines[locationCounter] + " " + x 
        # if operator not in operator list then exit with error
        # nothing to do with operands in first pass
            
        # remove comments

        # handle extern public and end

        # last thing we do in this loop            
        #if hasOperator == False:
         #   print "Line " + str(locationCounter) + " is missing legal operator"
          #  sys.exit()


        programLines[locationCounter] = programLines[locationCounter].strip()
        if not (isExtern or isPublic) and hasOperator:
            locationCounter = locationCounter + 1        
        
    #  print locationCounter
    
    #print symbolTable
    #print exSymbolTable
    #print pubSymbolTable
    #print programLines
    

    # pass 2;  process contents of the array 
    
    
    locationCounter = 0
    for line in programLines:
        lineList = string.split(line)
        length = len(lineList)
        # call skipLabels here and get next token index
        tokenNdx = skipLabels(lineList )            
        if tokenNdx >= length:
            continue        # label only or blank line

        # grab opcode and operand
        
        try:
            opcode = operators[lineList[tokenNdx]][0]
        except:
            print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
            print line
            print "Invalid Operation"
            sys.exit()
        if operators[lineList[tokenNdx]][1]==1:
            try:
                operand = lineList[tokenNdx+1]
            except:
                print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                print line
                print "operand expected for this operator"
                sys.exit()
        # if no operand expected; nothing to do; continue

        # if operand missing say so with error    
        elif operators[lineList[tokenNdx]][1]==0 or opcode =='dw':
            locationCounter +=1
            continue
        if opcode == 'public' or opcode == 'extern' or opcode == 'end':
                continue
        
                
        elif type(operand) == type("asd") and not validIdentifier(operand):
            try:
                x = int(operand)
            except:
                print 'Error on line ',locationCounter, ' of ', fileName
                print line
                print "Invalid Symbol"
                
        
        else:
        
            r = locationCounter
                
            MSBR = r/256
            lsbr = r % 256
            if operand in exSymbolTable:
                #print "ex"
                #print opcode
                #print operand
                fileIsMAC = 0
                outFile.write('E')
                outFile.write(chr(lsbr))
                outFile.write(chr(MSBR))
                outFile.write(operand)
                outFile.write(chr(0))
            
            else:
                #print "regSym"
                #print opcode
                #print operand
                outFile.write('R') 
                outFile.write(chr(lsbr))
                outFile.write(chr(MSBR))
            
            try:
                if symbolTable[endVar]==locationCounter:
                    #print "end"
                    #print opcode
                    #print operand
                    outFile.write('s')
                    outFile.write(chr(lsbr))
                    outFile.write(chr(MSBR))
            except:
                print "no end variable"
            # regular operator            
            # verify operand; use validIdentifier(operand) when necessary
            # if not a valid Identifier is it an integer?
            
        # last thing we do in the second pass
        locationCounter = locationCounter + 1
    for x in pubSymbolTable:
        fileIsMAC = 0
        r = pubSymbolTable[x]
        MSBR = r/256
        lsbr = r % 256
        outFile.write('P')
        outFile.write(chr(lsbr))
        outFile.write(chr(MSBR))
        outFile.write(x)
        outFile.write(chr(0))
    #print "T"
    outFile.write('T')
        # final pass
    locationCounter = 0
    # write to file
    for line in programLines:
        
        #print 'Line: ',line
        lineList = string.split(line)
        length = len(lineList)
        tokenNdx = skipLabels(lineList )            
        if tokenNdx >= length:
            continue        # label only or blank line

        # grab opcode and operand
        
        opcode = operators[lineList[tokenNdx]][0]
        numberOperands = operators[lineList[tokenNdx]][1]
        if numberOperands == 1:
            try:
                if len(lineList)>tokenNdx + 1:
                    operand = lineList[tokenNdx+1]
                    #print operand
            except:
                print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                print line
                print "operand expected for this operator"
                sys.exit()
            
            if validIdentifier(operand)==0:
                try:
                    
                    operand = int(operand)
                except:
                    print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                    print line
                    print "Invalid Operand"
                    sys.exit()
            
       
                operand = int(operand)
                if lineList[tokenNdx] in xOperators:
                    if operand < 0 or operand>4095:
                        print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                        print line
                        print "Address or operand out of range"
                        sys.exit()
                elif lineList[tokenNdx] in yOperators:
                    if operand <0 or operand > 255:
                        print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                        print line
                        print "Address or operand out of range"
                        sys.exit()
                elif lineList[tokenNdx] == 'dw':
                    
                    if operand<(-32768) or operand > 65535:
                        print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                        print line
                        print "Address or operand out of range"
                        sys.exit()
                
                
                    
            elif validIdentifier(operand)==1:
                if not (operand in symbolTable or operand in exSymbolTable):
                    print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                    print line
                    print "Undefined label in operand field"
                    sys.exit()
            
            
        # call skipLabels here
        # get operator from linelist and then corresponding opcode
        # get operand if present
        
        # if operand in local symbol table find its value
        # if operand in external symbol table find its value
        # otherwise operand  is the value
        
            
            if operand in symbolTable and not operand in exSymbolTable:
                operandValue = int(symbolTable[operand])
            elif operand in exSymbolTable:
                operandValue = 0
            else:
                operandValue = int(operand)    
                
        if opcode == 'dw':
            machineValue = int(operandValue)
            
        elif opcode in ['public','extern','end']:
            continue
        elif opcode != 'dw' and numberOperands == 0:
            machineValue = opcode
            # the machine value is initially just the opcode
        else:
            machineValue = opcode + operandValue
            
            # add combine opcode and operand value into a single machine code
            # print opcode, operandValue
            # but before you do make sure that it is within the necessary range
            # for example, if the opcode is aloc or dloc then it must be within [0,255]
            
            #machineValue = machineValue + opVal
        
        locationCounter +=1
        if locationCounter>4096:
                print "ERROR on line " + str(locationCounter) + " of " + fileName +":"
                print line
                print "Source program too big"
                sys.exit()
        print 'OPS: ',hex(machineValue)
        MSB = machineValue/256
        lsb = machineValue % 256
        #print hex(MSB)
        #print hex(lsb)
        #print MSB
        #print lsb
        outFile.write(chr(lsb))
        outFile.write(chr(MSB))
        
        
        # now determine the most significant byte and the least significant byte 
       
       # print opcode, operand, operandValue, machineValue
        
        # output to the file, first the least significant byte followed by the msb

        # increment the location counter
        
    # Done
            
    # close the optput file
    outFile.close()
    # change its extension from .tmp to .mac or .mob
    if fileIsMAC == 0:
        outFileExt = ".mob"
    else:
        outFileExt = ".mac"
    shutil.move(outFileName+'.tmp', outFileName+outFileExt)




# call main to run the program 
main()












