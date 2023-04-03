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
        self.circuitName = None
        self.circuitNumber = None

class circuitName():
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

class circuitNumber():
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
cirNames = {}
instData = root[1]
for i in reversed(instData):
    if i.tag[:3] == "UID":
        li = lightInst()
        for j in i:
            if j.tag == "UID":
                li.UID = j.text
            elif j.tag == "Circuit_Name" and j.text != None:
                cn = None
                if j.text not in cirNames:
                    cn = circuitName()
                    cn.name = j.text
                    cirNames.update({j.text:cn})
                else:
                    cn = cirNames[j.text]
                li.circuitName = cn
            elif j.tag == "Circuit_Number" and j.text != None:
                cirNumb = int(j.text)
                if li.circuitName == None:
                    continue
                circuit = li.circuitName.circuits[cirNumb]
                if circuit == None:
                    circuit = circuitNumber()
                    circuit.number = cirNumb
                    circuit.parent = li.circuitName
                li.circuitNumber = circuit
                circuit.lightInsts.append(li)

        insts.update({li.UID:li})
        instData.remove(i)

print(insts)
print("****____****____****____****")
print(cirNames)
# Key sort
cirNames = dict(sorted(cirNames.items()))
# Value sort
# cirNames = dict(sorted(cirNames(), key=lambda item: item[1]))
print(cirNames)
print("****____****____****____****")
for i in instData:
    print(i.tag)