import os
import sys
import pandas as pd
import copy
from openpyxl import styles

APP_NAME = "FAPSoftware"
    
def resource_path(relative):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

def sort_list(lst):

    '''
    Sort list by the length of Japanese of every element through merge.
    '''
    
    length = len(lst)
    if length in [0,1]:
        return lst
    m = sort_list(lst[0: length//2])
    n = sort_list(lst[length//2: length])
    new_list = []
    i = j = 0
    while i < len(m) and j < len(n):
        if len(simplify(m[i][0])) >= len(simplify(n[j][0])):
            new_list.append(m[i])
            i+=1
        else:
            new_list.append(n[j])
            j+=1
    new_list = new_list + m[i:] + n[j:]
    return new_list

def simplify(term):
    temp = ''
    for i in term:
        if i not in r'\/':
            temp = temp+i
    return temp

class Dictionary:
    def __init__(self, dic_path=resource_path(os.path.join("data", "Dictionary.xlsx"))):
        self.dic_address = dic_path
        self.dic = pd.read_excel(self.dic_address)
        self.shape = self.dic.shape

    def outputdf(self):
        return copy.deepcopy(self.dic)
    
    def outputList(self):
        l=[]
        for i in range(self.dic.shape[0]):
            l.append(Term(list(self.dic.loc[i])))
        return l
    
    def isExists(self, l):
        for i in range(self.dic.shape[0]):
            if list(self.dic.loc[i])==l:
                return True
        return False
    
    def outputClassifiedList(self):
        df = self.outputdf()
        df.sort_values("Japanese")
        lst = [[], [], []]
        for i in range(df.index.stop):
            temp = list(df.loc[i])
            for i in range(4):
                temp[i] = JpString(temp[i])
            temp[4] = int(temp[4])
            lst[temp[4]].append(temp[:4])
        return [sort_list(lst[1])+sort_list(lst[0]), sort_list(lst[2])]
    
    def __getitem__(self, key):
        return Term(list(self.dic.loc[key]))
    
    def dfappend(self, l):
        new_l = self.outputList()
        new_l.append(l)
        return pd.DataFrame(new_l, columns=self.dic.columns)
    
    def isIndf(self, l):
        outputList = self.outputList()
        new_l = [JpString(i) for i in l]
        for i in range(len(outputList)):
            if outputList[i] == new_l:
                return True
        return False
    
    def savedf(self, df):
        with pd.ExcelWriter(self.dic_address, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
            workbook = writer.book
            worksheet = workbook["Sheet1"]
            for c in "ABCDE":
                for cell in worksheet[c]:
                    cell.font = styles.Font(name="Corporate Logo Bold", sz=14)
            workbook.save(self.dic_address)

    def delete(self, index):
        df = self.outputdf()
        tempList = self.outputList()
        tempList = tempList[:index]+tempList[index+1:]
        new_df = pd.DataFrame(tempList, columns=df.columns)
        self.savedf(new_df)
        
    
class JpString(str):
    def __new__(cls, value):
        return super().__new__(cls, value)

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(result, str):
            return JpString(result)
        return result
        

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        if callable(attr) and name not in dir(str):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if isinstance(result, str):
                    return JpString(result)
                return result
            return wrapper
        return attr
    
    def __add__(self, other):
        return JpString(super().__add__(other))
    
    def __mul__(self, other):
        return JpString(super().__mul__(other))
    
    def string_division(self):
        tempString = "/"+self
        tempSubstring = JpString("")
        tempValue = 0
        tempMap = []
        for i in range(len(tempString)):
            if tempString[i]=="/":
                if i != 0:
                    tempMap.append((tempSubstring, tempValue))
                    tempValue=0
                    tempSubstring=JpString("")
            elif tempString[i]=="\\":
                tempMap.append((tempSubstring, tempValue))
                tempValue=1
                tempSubstring=JpString("")
            else:
                tempSubstring+=tempString[i]
        tempMap.append((tempSubstring, tempValue))
        return tempMap
    
    def isHiragana(self):
        return len(self)==1 and 12353<=ord(self)<=12436
    
    def isKatakana(self):
        return len(self)==1 and 12449<=ord(self)<=12538
    
    def isKana(self):
        return self.isHiragana() or self.isKatakana()
    
    def isSameKana(self, other):
        if not isinstance(other, JpString):
            return False
        if not self.isKana() or not other.isKana():
            return False
        c1 = copy.deepcopy(self)
        c2 = copy.deepcopy(other)
        if c1.isHiragana():
            c1 = JpString(chr(ord(c1)+96))
        if c2.isHiragana():
            c2 = JpString(chr(ord(c2)+96))
        return c1==c2
    
    def isSameString(self, other):
        if not isinstance(other, JpString):
            return False
        if len(self)!=len(other):
            return False
        s1 = JpString(self.upper())
        s2 = JpString(other.upper())
        for i in range(len(s1)):
            if not s1[i].isSameKana(s2[i]) and s1[i]!=s2[i]:
                return False
        return True
    
    def isAllKana(self):
        flag = False
        for i in self:
            if JpString(i).isKana():
                flag = True
            if flag and not JpString(i).isKana():
                return -1
        return 0 if flag else 1
    

class Term(list):
    def __init__(self, *args):
        l = [JpString(i) for i in args[0]]
        super().__init__(l)
        self.Japanese_division = self[0].string_division()
        self.Kana_division = self[1].string_division()
        self.Division_division = self[2].string_division()

    def isLegal(self):
        return self.isMatch() and self.isDivisionMatch() and self.isTypeMatch()

    def isMatch(self):
        if (len(self.Japanese_division)!=len(self.Kana_division)
            or len(self.Kana_division)!=len(self.Division_division)):
            return False
        for i in range(len(self.Kana_division)):
            if (self.Japanese_division[i][1]!=self.Kana_division[i][1]
                or self.Kana_division[i][1]!=self.Division_division[i][1]):
                return False
        return True
    
    def isDivisionMatch(self):
        for i in range(len(self.Kana_division)):
            if self.Division_division[i][0]=="0":
                if (self.Japanese_division[i][0].isAllKana()!=1
                    or self.Kana_division[i][0].isAllKana()!=0):
                    return False
            elif self.Division_division[i][0]=="-1":
                if (self.Kana_division[i][0].isAllKana()!=0
                    or not self.Japanese_division[i][0].isSameString(self.Kana_division[i][0])):
                    return False
            else:
                return False
        return True
    
    def isTypeMatch(self):
        match self[3]:
            case "五段":
                if (self.Division_division[-1][1]==1 and
                    self.Japanese_division[-1][0] in "うくすつぬむるぐぶ"):
                    return True
            case "上下":
                if (self.Division_division[-1][1]==1 and
                    self.Japanese_division[-1][0]=="る"):
                    return True
            case "形容":
                if (self.Division_division[-1][1]==1 and
                    self.Japanese_division[-1][0]=="い"):
                    return True
            case "サ行":
                if (self.Division_division[-1][1]==1 and
                    self.Japanese_division[-1][0]=="する"):
                    return True
            case ("タ行"|"名詞"):
                if self.Division_division[-1][1]==0:
                    return True
        return False
    
    def AutoDivision_Japanese(self, Japanese):
        templist = []
        tempJpString = ""
        flag = Japanese[0].isKana()
        for i in range(len(Japanese)):
            if flag==Japanese[i].isKana():
                tempJpString += Japanese[i]
            else:
                if flag:
                    templist.append([tempJpString, "-1"])
                else:
                    templist.append([tempJpString, "0"])
                tempJpString = Japanese[i]
                flag = not flag
        if flag:
            templist.append([tempJpString, "-1"])
        else:
            templist.append([tempJpString, "0"])
        return templist
    
    def AutoDivision_Kana(self, Japanese, Kana):
        templist = []
        tempCount = 0
        tempStart = 0
        flag = Japanese[0][1]=="-1"
        tempIndex = 0 if flag else len(Japanese[tempCount][0])
        if tempIndex >= len(Kana):
            templist.append([Kana[tempStart:], "0"])
        while tempIndex<len(Kana) and tempCount<len(Japanese):
            if flag:
                if Kana[tempIndex: tempIndex+len(Japanese[tempCount][0])]==Japanese[tempCount][0]:
                    templist.append([Japanese[tempCount][0], "-1"])
                    tempIndex += len(Japanese[tempCount][0])
                    tempStart = tempIndex
                    tempAddition = len(Japanese[tempCount][0])
                    tempIndex += tempAddition if tempIndex+tempAddition<len(Kana) else 0
                    tempCount += 1
                    flag = not flag
                else:
                    raise ValueError("Invalid Kana input")
            else:
                if tempCount==len(Japanese)-1:
                    templist.append([Kana[tempStart:], "0"])
                    break
                elif Kana[tempIndex: tempIndex+len(Japanese[tempCount+1][0])]==Japanese[tempCount+1][0]:
                    templist.append([Kana[tempStart: tempIndex], "0"])
                    flag = not flag
                    tempCount += 1
                else:
                    tempIndex += 1
        return templist
    
    def AutoDivision_Type(self, Japanese, Kana, Type):
        newlist = []
        match Type:
            case "五段":
                if (Japanese[-1][0][-1] not in "うくすつぬむるぐぶ" or
                    Kana[-1][0][-1] not in "うくすつぬむるぐぶ" or Japanese[-1][0][-1]!=Kana[-1][0][-1]):
                    raise ValueError("Invalid Kana input")
                newlist.append(Japanese[:-1]+[[Japanese[-1][0][:-1], "-1"]]+[[Japanese[-1][0][-1], "-2"]])
                newlist.append(Kana[:-1]+[[Kana[-1][0][:-1], "-1"]]+[[Kana[-1][0][-1], "-2"]])
            case ("上下"|"形容") as x:
                dic = {"上下":"る", "形容":"い"}
                if (Japanese[-1][0][-1]!=dic[x] or Kana[-1][0][-1]!=dic[x]):
                    raise ValueError("Invalid Kana input")
                newlist.append(Japanese[:-1]+[[Japanese[-1][0][:-1], "-1"]]+[[Japanese[-1][0][-1], "-2"]])
                newlist.append(Kana[:-1]+[[Kana[-1][0][:-1], "-1"]]+[[Kana[-1][0][-1], "-2"]])
            case "サ行":
                if (Japanese[-1][0][-2:]!="する" or Kana[-1][0][-2:]!="する"):
                    raise ValueError("Invalid Kana input")
                newlist.append(Japanese[:-1]+[[Japanese[-1][0][:-2], "-1"]]+[[Japanese[-1][0][-2:], "-2"]])
                newlist.append(Kana[:-1]+[[Kana[-1][0][:-2], "-1"]]+[[Kana[-1][0][-2:], "-2"]])
            case _:
                newlist = [Japanese, Kana]
        templist = [newlist[0][0][0], newlist[1][0][0], newlist[0][0][1]]
        for i in range(1, len(newlist[0])):
            if newlist[0][i][0]!="":
                if newlist[0][i][1] in ("0", "-1"):
                    templist[0] += "/"+newlist[0][i][0]
                    templist[1] += "/"+newlist[1][i][0]
                    templist[2] += "/"+newlist[0][i][1]
                elif newlist[0][i][1]=="-2":
                    templist[0] += "\\"+newlist[0][i][0]
                    templist[1] += "\\"+newlist[1][i][0]
                    templist[2] += "\\-1"
        return templist
    
    def AutoDivision(self):
        tempTerm = copy.deepcopy(self)
        templist = [[], []]
        templist[0] = self.AutoDivision_Japanese(tempTerm[0])
        templist[1] = self.AutoDivision_Kana(templist[0], tempTerm[1])
        templist = self.AutoDivision_Type(*templist, tempTerm[3])
        return Term([*templist, *tempTerm[3:]])
    
class InText():
    def __init__(self, in_text_path=resource_path(os.path.join("data", "in.txt"))):
        self.file_address = in_text_path

    def read_text(self):
        file = open(self.file_address, mode='r', encoding="utf-8")
        text = file.read()
        file.close()
        return text
    
    def write_text(self, text):
        file = open(self.file_address, mode='w', encoding="utf-8")
        file.write(text)
        file.close()

class OutText():
    def __init__(self, out_text_path=resource_path(os.path.join("data", "out.txt"))):
        self.file_address = out_text_path
        
    def read_text(self):
        file = open(self.file_address, mode='r', encoding="utf-8")
        text = file.read()
        file.close()
        return text
    
    def write_text(self, text):
        file = open(self.file_address, mode='w', encoding="utf-8")
        file.write(text)
        file.close()

class Addition:
    def __init__(self):
        self.MOE = 0
        pass

    def operation(self, intext=InText(), outtext = OutText()):
        outtext.write_text(self.process(intext.read_text()))
        pass

    def process(self, text):
        new_text = text
        i = 0
        dic = Dictionary().outputClassifiedList()
        while i < len(new_text):
            dic_index = 0
            if new_text[i:i+2] == "${":
                new_text = new_text[:i]+new_text[i+2:]
                while new_text[i:i+2]!="}$" and i<len(new_text):
                    i+=1
                new_text = new_text[:i]+new_text[i+2:]
                continue
            if new_text[i] == "$":
                new_text = new_text[:i]+new_text[i+1:]
                i+=1
                continue
            if new_text[i] == "@":
                new_text = new_text[:i]+new_text[i+1:]
                dic_index = 1
            dic_sub = dic[dic_index]
            for j in range(len(dic_sub)):
                new_text, i = self.check(new_text, i, dic_sub[j])
            i+=1
        return new_text

    def printform(self, term):
        new_term = list(term)[:3]
        for i in range(3):
            if '\\' in new_term[i]:
                new_term[i] = new_term[i].split('\\')
                new_term[i] = new_term[i][0]
            new_term[i] = new_term[i].split('/')
        temp = ''
        for i in range(len(new_term[2])):
            if new_term[2][i] == '0':
                if(self.MOE == 0):
                    temp+=new_term[0][i]+'('+new_term[1][i]+')'
                else:
                    temp+="{}photrans|{}|{}{}".format("{{", new_term[0][i], new_term[1][i], "}}")
            else:
                temp+=new_term[0][i]
        return temp
    
    def meishi(self, new_line, j, term):
        temp = simplify(term[0])
        if new_line[j:j+len(temp)] == temp:
            new_line = new_line[:j] + self.printform(term) + new_line[j+len(temp):]
            j+=len(self.printform(term))-1
        return new_line, j
    
    def godann(self, new_line, j, term):
        temp = simplify(term[0])
        gobi = {'う':'わいうえおっ',
                'く':'かきくけこい',
                'す':'さしすせそ',
                'つ':'たちつてとっ',
                'ぬ':'なにぬねのん',
                'む':'まみむめもん',
                'る':'らりるれろっ',
                'ぐ':'がぎぐげごい',
                'ぶ':'ばびぶべぼん'}
        if (new_line[j:j+len(temp)-1] == temp[:-1] and
            j+len(temp)-1<len(new_line) and
            new_line[j+len(temp)-1] in gobi[temp[-1]]):
            new_line = new_line[:j] + self.printform(term) + new_line[j+len(temp)-1:]
            j+=len(self.printform(term))
        return new_line, j
    
    def kamishimo(self, new_line, j, term):
        temp = simplify(term[0])
        if new_line[j:j+len(temp)-1] == temp[:-1]:
            new_line = new_line[:j] + self.printform(term) + new_line[j+len(temp)-1:]
            j+= len(self.printform(term))-1
        return new_line, j
    
    def tagyou(self, new_line, j, term):
        gokann = ['来/る','来/ま','来/なさ','来/な','来/た','来/て',
                '来/られ','来/させ','来/い','来/よ']
        yomikata = ['く/る','き/ま','き/なさ','こ/な','き/た',
                    'き/て','こ/られ','こ/させ','こ/い','こ/よ']
        for i in range(len(gokann)):
            temp = simplify(gokann[i])
            if new_line[j:j+len(temp)] == temp:
                new_line = new_line[:j] + self.printform([gokann[i],yomikata[i],'0/-1','タ行']) + new_line[j+len(temp):]
                j+=len(self.printform([gokann[i],yomikata[i],'0/-1','タ行']))-1
                break
        return new_line, j
    
    def sagyou(self, new_line, j, term):
        gokann = ['する', 'し', 'せず', 'せよ', 'させ', 'され']
        for i in range(len(gokann)):
            temp = simplify(term[0])[:-2]
            if (new_line[j:j+len(temp)] == temp and
                new_line[j+len(temp):j+len(temp)+len(gokann[i])] == gokann[i]):
                new_line = new_line[:j] + self.printform(term) + new_line[j+len(temp):]
                j+=len(self.printform(term))
                break
        return new_line, j
    
    def keiyou(self, new_line, j, term):
        temp = simplify(term[0])
        gobi = ['い','かった','く','ければ','がる','がり','がら',
                'がれ','がろ','がっ','げ','さ','すぎ','過ぎ', "そう"]
        for i in range(len(gobi)):
            if (new_line[j:j+len(temp)-1] == temp[:-1] and
                new_line[j+len(temp)-1:j+len(temp)-1+len(gobi[i])] == gobi[i]):
                new_line = new_line[:j] + self.printform(term) + new_line[j+len(temp)-1:]
                j+=len(self.printform(term))-1
                break
        return new_line, j
    
    def check(self, new_line, j , term):
        match term[3]:
            case JpString('五段'):
                new_line, j = self.godann(new_line, j, term)
            case JpString('上下'):
                new_line, j = self.kamishimo(new_line, j, term)
            case JpString('タ行'):
                new_line, j = self.tagyou(new_line, j, term)
            case JpString('形容'):
                new_line, j = self.keiyou(new_line, j, term)
            case JpString('サ行'):
                new_line, j = self.sagyou(new_line, j, term)
            case JpString('名詞'):
                new_line, j = self.meishi(new_line, j, term)
        return new_line, j


def main():
    addition = Addition()
    addition.operation()
    return

if __name__ == "__main__":
    main()