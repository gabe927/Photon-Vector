import xml.etree.ElementTree as ET

tree = ET.parse('data.xml')
root = tree.getroot()

class lightInst():
    def __init__(self) -> None:
        self.UID = ""
        self.LWID = ""
        self.deviceType = ""
        self.symbolName = ""
        self.instType = ""
        self.unitNumber = None
        self.load = 0
        self.mult = None
        self.circuit = None

class mult():
    def __init__(self) -> None:
        self.name = ""
        self.circuits = {
            1 : None,
            2 : None,
            3 : None,
            4 : None,
            5 : None,
            6 : None
        }
        self.unnumberedLIs = []

class circuit():
    def __init__(self) -> None:
        self.number = -1
        self.parent = None
        self.lightInsts = []
    
    def getLoad(self):
        totalLoad = 0
        for i in self.lightInsts:
            totalLoad += i.load
        return totalLoad

insts = {}
mults = {}
instData = root[1]
for i in reversed(instData):
    if i.tag[:3] == "UID":
        li = lightInst()
        for j in i:
            if j.tag == "UID":
                li.UID = j.text
            elif j.tag == "Circuit_Name" and j.text != None:
                cn = None
                if j.text not in mults:
                    cn = mult()
                    cn.name = j.text
                    mults.update({j.text:cn})
                else:
                    cn = mults[j.text]
                li.mult = cn
            elif j.tag == "Circuit_Number" and j.text != None:
                cirNumb = int(j.text)
                if li.mult == None:
                    continue
                c = li.mult.circuits[cirNumb]
                if c == None:
                    c = circuit()
                    c.number = cirNumb
                    c.parent = li.mult
                li.circuit = c
                c.lightInsts.append(li)

        insts.update({li.UID:li})
        instData.remove(i)

print(insts)
print("****____****____****____****")
print(mults)
# Key sort
mults = dict(sorted(mults.items()))
# Value sort
# mults = dict(sorted(mults(), key=lambda item: item[1]))
print(mults)
print("****____****____****____****")
for i in instData:
    print(i.tag)