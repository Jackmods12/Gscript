#!/usr/bin/python3
import math
import os
import random
from re import S
import re
from tracemalloc import stop
import requests
import sys

import time
#fname = "test.gs"
fname = sys.argv[1]
#print(fname)

file = open(fname).read() 
file += "\n"

code = file
tokens = []
variables = {}
functions = {}

def doEVAL(x):
        mathcom = x[5:]
        complete = ""
        varON = 0
        currentVar = ""
        for i in range(0,len(mathcom)):
            if mathcom[i] == "#": 
                varON = 1
            elif mathcom[i] == "1" or mathcom[i] == "2" or mathcom[i] == "3" or mathcom[i] == "4" or mathcom[i] == "5" or mathcom[i] == "6" or mathcom[i] == "7" or mathcom[i] == "8" or mathcom[i] == "9" or mathcom[i] == "0" or mathcom[i] == ".":
                complete += mathcom[i]
            elif mathcom[i] == "+" or mathcom[i] == "-" or mathcom[i] == "*" or mathcom[i] == "/":
                varON = 0
                if currentVar != "":
                    complete += variables["$"+currentVar][4:]
                    currentVar = ""
                complete += mathcom[i]
            elif varON == 1:
                currentVar += mathcom[i]
            else:
                pass
        x = complete
        x = eval(x)
        return x


def getTYPE(x):
    if x[0:6] == "STRING":
        return x[8:][:-1],x[0:6]
    elif x[0:3] == "INT":
        return x[4:],x[0:3]
    elif x[0:4] == "EXPR":
        return str(doEVAL(x))[5:],x[0:4]
    elif x[0:4] == "BOOL":
        return x[5:],x[0:4]
    elif x[0:3] == "VAR":
        if variables[x[4:]][0:6] == "STRING":
            return variables[x[4:]][8:][:-1],variables[x[4:]][0:6]
        elif variables[x[4:]][0:3] == "INT":
            return variables[x[4:]][4:],variables[x[4:]][0:3]
        elif variables[x[4:]][0:4] == "BOOL":
            return variables[x[4:]][5:],variables[x[4:]][0:4]

def doASSAIGN_VAR(varname,varvalue):
    #print(varvalue)
    global variables
    global tokens
    if varvalue[0:6] == "STRING":
        variables[varname] = varvalue
    elif varvalue[0:3] == "INT":
        variables[varname] = varvalue
    elif varvalue[0:4] == "EXPR":
        variables[varname] = "INT:"+str(doEVAL(varvalue))

def getVARIABLE(var):
    if var[4:] in variables:
        return variables[var[4:]]
    else:
        return "Undefined Variable."

def doPRINT(x):
    if x[0:6] == "STRING":
        x = x[8:]
        x = x[:-1]
    elif x[0:3] == "INT":
        x = x[4:]
    elif x[0:4] == "EXPR":
        x = doEVAL(x)
    elif x[0:3] == "VAR":
        x = variables[x[4:]]
    x=str(x)
    print(x)

def decode(tokens):
    global variables
    i = 0
    loopStarting = 0
    ifStarted = 0
    infunc = 0
    namefunc = ""
    curRe = ""
    funcStarting = 0

    while i < len(tokens):
        if tokens[i][0:5] == "PRINT":
            if tokens[i] + " " + tokens[i+1][0:6] == "PRINT STRING" or tokens[i] + " " + tokens[i+1][0:3] == "PRINT INT" or tokens[i] + " " + tokens[i+1][0:4] == "PRINT EXPR" or tokens[i] + " " + tokens[i+1][0:3] == "PRINT VAR":
                if tokens[i+1][0:6] == "STRING":
                    doPRINT(tokens[i+1])
                elif tokens[i+1][0:3] == "INT":
                    doPRINT(tokens[i+1])
                elif tokens[i+1][0:4] == "EXPR":
                    doPRINT(tokens[i+1])
                elif tokens[i+1][0:3] == "VAR":
                    doPRINT(getVARIABLE(tokens[i+1]))
                i+=2
        elif tokens[i][0:3] == "VAR":
            if tokens[i+1] != "EQUALS":
                variables[tokens[i][4:]] = ""
            elif tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:6] == "VAR EQUALS STRING" or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:3] == "VAR EQUALS INT" or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:4] == "VAR EQUALS EXPR" or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:3] == "VAR EQUALS VAR":
                if tokens[i+2][0:6] == "STRING":
                    doASSAIGN_VAR(tokens[i][4:] , tokens[i+2])
                elif tokens[i+2][0:3] == "INT":
                    doASSAIGN_VAR(tokens[i][4:] , tokens[i+2])
                elif tokens[i+2][0:4] == "EXPR":
                    doASSAIGN_VAR(tokens[i][4:] , tokens[i+2])
                elif tokens[i+2][0:3] == "VAR":
                    doASSAIGN_VAR(tokens[i][4:] , getVARIABLE(tokens[i+2]))
            i+=3
        elif tokens[i][0:5] == "INPUT":
            if tokens[i] + " " + tokens[i+1][0:3] == "INPUT VAR":
                doASSAIGN_VAR(tokens[i+1][4:],"STRING:\""+input()+"\"")
            i+=2
        elif tokens[i] == "IF":
            if tokens[i] + " DATA " + "OPER" + " DATA " + tokens[i+4] == "IF DATA OPER DATA THEN":
                data1 = tokens[i+1]
                data2 = tokens[i+3]
                data1 = getTYPE(data1)
                data2 = getTYPE(data2)
                if tokens[i+2] == "EQEQ": 
                    if data1[0] == data2[0]:
                        cur = 0
                        i += 5
                elif tokens[i+2] == "NOTEQ": 
                    if data1[0] != data2[0]:
                        cur = 0
                        i += 5
                elif data1[1] == "INT":
                    if tokens[i+2] == "GR":
                        if data1[0] > data2[0]:
                            cur = 0
                            i += 5
                elif data1[1] == "INT":
                    if tokens[i+2] == "LS":
                        if data1[0] < data2[0]:
                            cur = 0
                            i += 5

                else:
                    for e in range(i+2,len(tokens)):
                        if tokens[e] == "ENDIF":
                            if e+1 < len(tokens):
                                if tokens[e+1] == "ELSE":
                                    i=e+2
                                    break
                                else:
                                    i = e+1
                                    break
        elif tokens[i] == "ENDELSE":
            i+=1
        elif tokens[i] == "ENDIF":
            i+=1
        elif tokens[i] == "APPEND":
            if tokens[i] + " " + "DATA" + " " + tokens[i+2] + " " + "DATA" + " " + tokens[i+4] + " " + tokens[i+4][0:3] == "APPEND DATA NEXT DATA NEXT VAR":
                data1 = ""
                data2 = ""
                if tokens[i+1][0:3] == "VAR":
                    if variables[tokens[i+1][4:]][0:6] == "STRING":
                        data1 = variables[tokens[i+1][4:]][8:][:-1]
                    else:
                        print("Wrong Data Type")
                elif tokens[i+1][0:6] == "STRING":
                    data1 = tokens[i+1][8:][:-1]



                if tokens[i+3][0:3] == "VAR":
                    if variables[tokens[i+3][4:]][0:6] == "STRING":
                        data2 = variables[tokens[i+3][4:]][8:][:-1]
                    else:
                        print("Wrong Data Type")
                elif tokens[i+3][0:6] == "STRING":
                    data2 = tokens[i+3][8:][:-1]

                x = data1 + data2
                variables[tokens[i+5][4:]] = x
                i += 6
        elif tokens[i] == "CLEAR":
            os.system("clear")
            i+=1
        elif tokens[i] == "LOOP":
            loopStarting = i
            i += 1
        elif tokens[i] == "ENDLOOP":
            i=loopStarting
        elif tokens[i] == "ELSE":
            for e in range(i,len(tokens)):
                if tokens[e] == "ENDELSE":
                    i = e+1
        elif tokens[i] == "BREAK":
            for e in range(i,len(tokens)):
                if tokens[e] == "ENDLOOP":
                    i = e+1
        elif tokens[i] == "WAIT":
            data1 = ""
            if tokens[i+1][0:3] == "INT":
                data1 = tokens[i+1][4:]
            elif tokens[i+1][0:3] == "VAR":
                data1 = variables[tokens[i+1][4:]][4:]
            time.sleep(int(data1))
            i+=2
        elif tokens[i] == "RANDOM":
            if tokens[i] + " " + "DATA" + " " + tokens[i+2] + " " + "DATA" + " " + tokens[i+4] + " " + tokens[i+5][0:3] == "RANDOM DATA NEXT DATA NEXT VAR":
                data1 = ""
                data2 = ""
                if tokens[i+1][0:3] == "INT":
                    data1 = tokens[i+1][4:]
                elif tokens[i+1][0:3] == "VAR":
                    if variables[tokens[i+1][4:]][0:3] == "INT":
                        data1 = variables[tokens[i+1][4:]][4:]
                

                if tokens[i+3][0:3] == "INT":
                    data2 = tokens[i+3][4:]
                elif tokens[i+3][0:3] == "VAR":
                    if variables[tokens[i+3][4:]][0:3] == "INT":
                        data2 = variables[tokens[i+3][4:]][4:]
                variables[tokens[i+5][4:]] = "INT:"+str(random.randrange(int(data1),int(data2)))
            
            i+=6
        elif tokens[i] == "STRING":
            if tokens[i] + " " + "DATA" + " " + tokens[i+2] + " " + tokens[i+3][0:3] == "STRING DATA NEXT VAR":
                data1 = ""
                if tokens[i+1][0:3] == "INT":
                    data1 = tokens[i+1][4:]
                elif tokens[i+1][0:3] == "VAR":
                    if variables[tokens[i+1][4:]][0:3] == "INT":
                        data1 = variables[tokens[i+1][4:]][4:]
                
                variables[tokens[i+3][4:]] = "STRING:\""+data1+"\""
            i+=4
        elif tokens[i] == "INT":
            if tokens[i] + " " + "DATA" + " " + tokens[i+2] + " " + tokens[i+3][0:3] == "INT DATA NEXT VAR":
                true = 0
                for e in range(0,len(tokens[i+1][8:][:-1])):
                    tok = tokens[i+1][8:][:-1][e]
                    if tok == "1" or tok == "2" or tok == "3" or tok == "4" or tok == "5" or tok == "6" or tok == "7" or tok == "8" or tok == "9" or tok == "0":
                        true = 1
                    else:
                        true = 0
                        break
                if true == 1:
                    data1 = ""
                    if tokens[i+1][0:6] == "STRING":
                        data1 = tokens[i+1][8:][:-1]
                    elif tokens[i+1][0:3] == "VAR":
                        if variables[tokens[i+1][4:]][0:6] == "STRING":
                            data1 = variables[tokens[i+1][7:]][8:][:-1]
                     
                    variables[tokens[i+3][4:]] = "INT:"+data1
            i+=4
        elif tokens[i][0:4] == "FUNC":
            if tokens[i+1] == "SET":
                args = []
                if tokens[i+2] == "ARG0":
                    for e in range(i+3,len(tokens)):
                        if tokens[e] == "ARG1":
                            for n in range(e+1,len(tokens)):
                                if tokens[n] == "ENDFUNC":
                                    functions[tokens[i][5:]] = {"args":args,"start":e+1,"end":n+1}
                                    i=n+1
                                    break
                            break
                        else:
                            args.append(tokens[e][4:])
            elif tokens[i+1] == "RUN":
                if tokens[i+2] == "ARG0":
                    pos = 0
                    for e in range(i+3,len(tokens)):
                        if tokens[e] != "ARG1":
                            variables[functions[tokens[i][5:]]["args"][pos]] = getTYPE(tokens[e])[0]
                            pos+=1
                        elif tokens[e] == "ARG1":
                            if e+1 < len(tokens):
                                if tokens[e+1][0:3] == "VAR":
                                    curRe = tokens[e+1][4:]
                                funcStarting = e+1
                                break
                            else:
                                funcStarting = e
                infunc = 1
                namefunc = tokens[i][5:]
                i=functions[tokens[i][5:]]["start"]

        elif tokens[i] == "HTTPGET":
            data,dtype = getTYPE(tokens[i+1])
            if dtype == "STRING":
                if tokens[i+2][0:3] == "VAR":
                    ret = requests.get(data).content.decode("utf-8")
                    variables[tokens[i+2][4:]] = ret
                    i+=3
        elif tokens[i] == "HTTPPOST":
            #print("POS")
            data,dtype = getTYPE(tokens[i+1])
            data2,dtype2 = getTYPE(tokens[i+2])
            if dtype == "STRING":
                if dtype2 == "STRING":
                    if tokens[i+3][0:3] == "VAR":
                        r = requests.post(data,data=data2)
                        variables[tokens[i+3][4:]] = r.text
                        i+=4
        elif tokens[i] == "FILEREAD":
            data,dtype = getTYPE(tokens[i+1])

            if dtype == "STRING":
                if tokens[i+2][0:3] == "VAR":
                    f = open(data,"r")
                    variables[tokens[i+2][4:]] = f.read()
                    f.close()
            i+=3

        elif tokens[i] == "FILEWRITE":
            data,dtype = getTYPE(tokens[i+2])
            data2,dtype2 = getTYPE(tokens[i+1])
            data3,dtype3 = getTYPE(tokens[i+3])

            if dtype2 == "STRING":
                if data2 == "append":
                    if dtype == "STRING":
                        if dtype3 == "STRING":
                            f = open(data,"a")
                            f.write(data3)
                            f.close()
            i+=4

            #if dtype == "STRING":
                #print(dtype)
                #if tokens[i+2][0:3] == "VAR":
                    #f = open(data,"r")
                    #variables[tokens[i+2][4:]] = f.read()
                    #f.close()

        elif tokens[i] == "RETURN":
            if infunc == 1:
                variables[curRe] = tokens[i+1]
            i+=2
        elif tokens[i] == "ENDFUNC":
            if infunc == 1:
                i=funcStarting
                infunc = 0
                namefunc =""
                funcStarting = 0
                curRe = ""
        else:
            break

def lexer(code=code):
  
    TT_PRINT = "PRINT"
    TT_STRG = "STRING:\""
    TT_INT = "INT:"
    TT_S_WRAP = "SWRP"
    TT_E_WRAP = "EWRP"
    TT_END = "END"
    TT_EXPR = "EXPR:"
    TT_VAR = "VAR:"

    #TT_ADD = "ADD"

    global tokens
    keyword = ""
    string = ""
    varStart = 0
    funcStart = 0
    func = ""
    var = ""
    expr = ""
    isexpr_var = 0
    isdouble = 0
    isexpr = 0
    quote = 0 
    curpos = 0
    for char in code:
        keyword += char
        #print(var)
        if keyword == " " and quote == 0:
            if quote == 0:
                if expr != "" and isexpr == 1:
                    tokens.append(TT_EXPR+expr)
                    expr = ""
                    isexpr = 0
                elif expr != "" and isexpr == 0:
                    tokens.append(TT_INT+expr)
                    expr = ""
                    isexpr = 0 
                if var != "":
                    tokens.append("VAR:"+var)
                    var = ""
                    varStart = 0
                if func != "":
                    tokens.append("FUNC:"+func)
                    func = ""
                    funcStart = 0
                keyword = ""
            else:
                keyword = " "
        elif keyword == "\n" or keyword == "<EOF>" and quote == 0:
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
                isexpr_var = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            elif quote == 0 and varStart == 1:
                tokens.append("VAR:"+var)
                varStart = 0
                var = ""
            keyword = ""
        elif keyword == ")" and quote == 0:
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            if var != "":
                    tokens.append("VAR:"+var)
                    var = ""
                    varStart = 0
            tokens.append("ARG1")
            keyword = ""
        elif keyword == "(" and quote == 0:
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            tokens.append("ARG0")
            keyword = ""
        elif keyword == "true" and quote == 0:
            tokens.append("BOOL:TRUE")
            keyword = ""
        elif keyword == "false" and quote == 0:
            tokens.append("BOOL:FALSE")
            keyword = ""
        elif keyword == "httpPOST" and quote == 0:
            tokens.append("HTTPPOST")
            keyword = ""
        elif keyword == "httpGET" and quote == 0:
            tokens.append("HTTPGET")
            keyword = ""
        elif keyword == "return" and quote == 0:
            tokens.append("RETURN")
            keyword = ""
        elif keyword == "set" and quote == 0:
            tokens.append("SET")
            keyword = ""
        elif keyword == "run" and quote == 0:
            tokens.append("RUN")
            keyword = ""
        elif keyword == "endfunc" and quote == 0:
            tokens.append("ENDFUNC")
            keyword = ""
        elif keyword == "else" and quote == 0:
            tokens.append("ELSE")
            keyword = ""
        elif keyword == "endelse" and quote == 0:
            tokens.append("ENDELSE")
            keyword = ""
        elif keyword == "int" and quote == 0:
            tokens.append("INT")
            keyword = ""
        elif keyword == "string" and quote == 0:
            tokens.append("STRING")
            keyword = ""
        elif keyword == "random" and quote == 0:
            tokens.append("RANDOM")
            keyword = ""
        elif keyword == "wait" and quote == 0:
            tokens.append("WAIT")
            keyword = ""
        elif keyword == "filewrite" and quote == 0:
            tokens.append("FILEWRITE")
            keyword = ""
        elif keyword == "fileread" and quote == 0:
            tokens.append("FILEREAD")
            keyword = ""
        elif keyword == "++" and quote == 0:
            tokens.append("PLPL")
            keyword = ""
        elif keyword == "break" and quote == 0:
            tokens.append("BREAK")
            keyword = ""
        elif keyword == "loop" and quote == 0:
            tokens.append("LOOP")
            keyword = ""
        elif keyword == "endloop" and quote == 0:
            tokens.append("ENDLOOP")
            keyword = ""
        elif keyword == "clear" and quote == 0:
            tokens.append("CLEAR")
            keyword = ""
        elif keyword == "append" and quote == 0:
            tokens.append("APPEND")
            keyword = ""
        elif keyword == "if" and quote == 0 :
            tokens.append("IF")
            keyword = ""
        elif keyword == "then" and quote == 0 :

            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0

            tokens.append("THEN")
            keyword = ""
        elif keyword == "endif" and quote == 0 :
            tokens.append("ENDIF")
            keyword = ""
        elif keyword == "input" and quote == 0:
            tokens.append("INPUT")
            keyword = ""
        elif keyword == "," and quote == 0:
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            tokens.append("NEXT")
            keyword = ""
        elif keyword == "=" and quote == 0:
            
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            
            if var != "":
                tokens.append("VAR:"+var)
                var = ""
                varStart = 0
            if tokens[-1] == "EQUALS":
                tokens[-1] = "EQEQ"
            else:
                tokens.append("EQUALS")
            keyword = ""
        elif keyword == "!" and quote == 0:
            
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0
            
            if var != "":
                tokens.append("VAR:"+var)
                var = ""
                varStart = 0
            if tokens[-1] == "EQUALS":
                tokens[-1] = "NOTEQ"
            else:
                tokens.append("EQUALS")
            keyword = ""
        elif keyword == "<" and quote == 0:
            
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0

            tokens.append("LS")
            keyword = ""

        elif keyword == ">" and quote == 0:
            
            if expr != "" and isexpr == 1:
                tokens.append(TT_EXPR+expr)
                expr = ""
                isexpr = 0
            elif expr != "" and isexpr == 0:
                tokens.append(TT_INT+expr)
                expr = ""
                isexpr = 0

            tokens.append("GR")
            keyword = ""

        elif keyword == "func " and quote == 0:
            funcStart = 1
            func += keyword
            keyword = ""
        elif keyword == "$" and quote == 0:
            varStart = 1
            var += keyword
            keyword = ""
        elif funcStart == 1:
            func += keyword
            keyword = ""
        elif varStart == 1:
            var += keyword
            keyword = ""
        elif keyword == "print":
            
            tokens.append(TT_PRINT)
            keyword = ""
        elif keyword == '"':
            if quote == 0:
                quote = 1
                keyword = ""
            elif quote == 1:
                tokens.append(TT_STRG+string+"\"")
                quote = 0
                keyword = ""
                string = ""
        elif quote == 1:
            string += keyword
            keyword = ""

        elif keyword == "1" or keyword == "2" or keyword == "3" or keyword == "4" or keyword == "5" or keyword == "6" or keyword == "7" or keyword == "8" or keyword == "9" or keyword == "0" or keyword == "#" or keyword == ".":
            if keyword == "#" and quote == 0:
                isexpr_var = 1
            expr += keyword
            keyword = ""
        elif keyword == "+" or keyword == "-" or keyword == "*" or keyword == "/":
            isexpr = 1
            expr += keyword
            keyword = ""
        elif isexpr_var == 1:
            expr += keyword
            keyword = ""
        elif keyword == "\t" and quote == 0:
            keyword = ""
    
        #print(tokens)
    #print(expr)    
    #print(var)

    curpos += 1
    #print(tokens)
    
    decode(tokens)
    #print(tokens)
lexer()
