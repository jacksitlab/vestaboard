from enum import Enum
from typing import List
import math

class HorizontalAlign(Enum):
    LEFT=1
    CENTER=2
    RIGHT=3
class VerticalAlign(Enum):
    TOP=1
    CENTER=2
    BOTTOM=3


class TextAlignment:


    def __init__(self, width, height, splitOperators=[' '], widthFactor=0.8) -> None:
        self.width = width
        self.height = height
        self.splitOperators = splitOperators
        self.widthFactor=widthFactor
      
    
    def align(self, inputstr:str, halign:HorizontalAlign = HorizontalAlign.CENTER, valign:VerticalAlign = VerticalAlign.CENTER)-> List[str]:
        

        if len(inputstr)>self.width*self.height:
            raise ValueError('input string seems to be tooo long for the matrix')
        
        words = inputstr.split(' ')
        max_chars_per_line = math.floor(self.widthFactor*self.width)
        result:List[inputstr]=[]
        curLine=''
        tmpLine=''
        while True:
            # try to add all words first
            while len(words)>0:
                word = words.pop(0)
                tmpLine = f'{tmpLine} {word}'
                if len(tmpLine)>max_chars_per_line:
                    result.append(curLine)
                    tmpLine=f'{word}'
                curLine = tmpLine
            
            if len(curLine)>0:
                result.append(curLine)
            
            if len(result)<=self.height:
                break
            
            # retry with higher scale factor/more chars per line
            words = inputstr.split(' ')
            result=[]
            max_chars_per_line +=1
            curLine=''
            tmpLine=''
            if max_chars_per_line>self.width:
                raise ValueError('input string is to be tooo long for the matrix')


        # vertical align
        if valign==VerticalAlign.TOP:
            while len(result)<self.height:
                result.append(' '*self.width)
        elif valign == VerticalAlign.BOTTOM:
            while len(result)<self.height:
                result.insert(0,' '*self.width)
        
        else:
            toggle=False
            while len(result)<self.height:
                if toggle:
                    result.insert(0,' '*self.width)
                else:
                    result.append(' '*self.width)
                
                toggle=not toggle
        
        # horizontal align
        idx=0
        if halign == HorizontalAlign.LEFT:
            fmt = '{:<'+str(self.width)+'}'
        elif halign == HorizontalAlign.RIGHT:
            for line in result:
                fmt = '{:>'+str(self.width)+'}'
        else:
            for line in result:
                fmt = '{:^'+str(self.width)+'}'
     
        for line in result:
            result[idx] = fmt.format(line.strip())
            idx+=1
        return result