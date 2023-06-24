import base64
import json
from enum import Enum
from alignment import VerticalAlign, HorizontalAlign, TextAlignment
import urllib3
from typing import List

def invertMap(inp:dict)->dict:
    outp=dict()
    for key, values in inp.items():
        for value in values:
            outp[value]=key
    return outp

class VestaboardResult:
    def __init__(self, response) -> None:
        self.succeeded = response.status == 200
        if response.data is not None:
            try:
                self.data = json.loads(response.data.decode())
            except:
                self.data = response.data.decode()
        else:
            self.data = None

    def __str__(self) -> str:
        return f'VestaboardResult[succeeded={self.succeeded}, data={self.data}]'



class Vestaboard:
    NUM_ROWS=6
    NUM_COLS=22

    CHARACTERS_MAP={
        0:[' '],
        1:['A'],
        2:['B'],
        3:['C'],
        4:['D'],
        5:['E'],
        6:['F'],
        7:['G'],
        8:['H'],
        9:['I'],
        10:['J'],
        11:['K'],
        12:['L'],
        13:['M'],
        14:['N'],
        15:['O'],
        16:['P'],
        17:['Q'],
        18:['R'],
        19:['S'],
        20:['T'],
        21:['U'],
        22:['V'],
        23:['W'],
        24:['X'],
        25:['Y'],
        26:['Z'],
        27:['1'],
        28:['2'],
        36:['0'],
        37:['!'],
        38:['@'],
        39:['#'],
        40:['$'],
        41:['('],
        42:[')'],
        44:['-'],
        46:['+'],
        47:['&'],
        48:['='],
        49:[';'],
        50:[':'],
        52:['\''],
        53:['"'],
        54:['%'],
        55:[','],
        56:['.'],
        59:['/'],
        60:['?'],
        62:['°'],
        63:['PoppyRed', 'Red', '#FF0000'],
        64:['Orange'],
        65:['Yellow'],
        66:['Green','#00FF00'],
        67:['ParisBlue', 'Blue', '#0000FF'],
        68:['Violet'],
        69:['White'],
        70:['Black'],
        71:['Filled']
    }
    
    CHARACTERS_MAP_INVERTED = invertMap(CHARACTERS_MAP)
    SPECIAL_CODES=[63,64,65,66,67,68,69,70,71]
    LANGUAGE_REPLACEMENTS={
        'de':{
            'ö':'oe',
            'Ö':'Oe',
            'ü':'ue',
            'Ü':'Ue',
            'ä':'ae',
            'Ä':'Ae',
            'ß':'ss'
        }
    }
    @staticmethod 
    def translate(inputstr:str, halign:HorizontalAlign=HorizontalAlign.CENTER, 
                  valign:VerticalAlign=VerticalAlign.CENTER,
                  fillRest:int=0)->List[List[int]]:
        # check for special inputs
        arr:List[List[int]]=[]
        for i in range(Vestaboard.NUM_ROWS):
            arr.append([fillRest]*Vestaboard.NUM_COLS)#
        
        helper = TextAlignment(Vestaboard.NUM_COLS, Vestaboard.NUM_ROWS)
        lines = helper.align(inputstr,halign = halign, valign=valign)        
        for ln in range(Vestaboard.NUM_ROWS):
            line  = lines[ln]
            line = line.upper()
            for cn in range(Vestaboard.NUM_COLS):
                if(line[cn]!=' '):
                    arr[ln][cn]=Vestaboard.CHARACTERS_MAP_INVERTED[line[cn]]
                
        return arr
    
    @staticmethod
    def validate(inp:str|List[List[int]])->bool:
        if type(inp) is str:
            for c in inp.upper():
                if c not in Vestaboard.CHARACTERS_MAP_INVERTED.keys():
                    print(f'unsupported character \'{c}\' found')
                    return False
        elif type(inp) is list:
            if len(inp)!=Vestaboard.NUM_ROWS:
                return False
            for row in inp:
                if type(row) is not list:
                    return False
                if len(row)!=Vestaboard.NUM_COLS:
                    return False
                for value in row:
                    if value not in Vestaboard.CHARACTERS_MAP.keys():
                        return False
        return True
    
    def __init__(self, host, localApiKey, autocorrectLang=False) -> None:
        self.baseUrl = f'http://{host}:7000'
        self.defaultJsonHeaders = dict()
        self.defaultJsonHeaders['Content-Type']='application/json'
        self.defaultJsonHeaders['Accept']='application/json'
        self.defaultJsonHeaders['X-Vestaboard-Local-Api-Key']=localApiKey
        self.autocorrectLang = autocorrectLang
    def correctLang(self,lang:str,inputstr:str) -> str:
        result=''
        if lang not in Vestaboard.LANGUAGE_REPLACEMENTS:
            print(f'unsupported language {lang}. supported languages={Vestaboard.LANGUAGE_REPLACEMENTS.keys()}')
            return None
        langCorrections = Vestaboard.LANGUAGE_REPLACEMENTS[lang]
        for c in inputstr:
            if c.upper() not in Vestaboard.CHARACTERS_MAP_INVERTED.keys():
                if c in langCorrections:
                    result+=langCorrections[c]
                else:
                    print(f'unable to find replacement for invalid char \'{c}\' in lang {lang}')
                    return None
            else:
                result+=c
        return result

    def requestRest(self, uri, method, headers=None, data=None) -> VestaboardResult:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        if headers is None:
            headers = self.defaultJsonHeaders
        r = None
        if data == None:
            r = http.request(method, self.baseUrl+uri, headers=headers)
        else:
            if type(data) in [dict, list]:
                data = json.dumps(data)
            encoded_data = data.encode('utf-8')
            r = http.request(method, self.baseUrl+uri,
                             body=encoded_data, headers=headers)
        print(r.data.decode())
        return VestaboardResult(r)
  
    def read(self) -> VestaboardResult:
        return self.requestRest('/local-api/message','GET')
    
    def raw(self, data:List[List[int]])-> None|VestaboardResult:
        if not Vestaboard.validate(data):
           return None
        print(data)
        return self.requestRest('/local-api/message','POST',data=data)

    def write(self, inputstr:str, halign:HorizontalAlign=HorizontalAlign.CENTER, valign:VerticalAlign=VerticalAlign.CENTER):
        if(self.autocorrectLang):
            inputstr = self.correctLang('de',inputstr)
        if inputstr is None:
            return None
        if not Vestaboard.validate(inputstr):
           return None
        outp = Vestaboard.translate(inputstr, halign, valign)
        for line in outp:
            print(line)
        return self.raw(outp)


