from itertools import product


class InputBit:

    def __init__(self, label, precedents=None, dependents=None):
        self.state = 0
        if precedents is None:
            self.pre = []
        else:
            self.pre = precedents
        if dependents is None:
            self.dep = []
        else:
            self.dep = dependents
        self.label = label
        # If precedent is set then all precedents must set this new instance as their dependent
        if precedents:
            for pre in precedents:
                pre.dep.append(self)
        # If dependents is set then all dependents must set this new instance as their precedent
        if dependents:
            for dep in dependents:
                dep.pre.append(self)

    def determine_state(self):
        pass


class OrGate(InputBit):

    def __init__(self, label, precedents=None, dependents=None):
        super().__init__(label, precedents, dependents)

    def determine_state(self):
        if self.pre:
            if any([pr.state for pr in self.pre]):
                self.state = 1
            else:
                self.state = 0


class AndGate(InputBit):

    def __init__(self, label, precedents=None, dependents=None):
        super().__init__(label, precedents, dependents)

    def determine_state(self):
        if self.pre:
            if all([pr.state for pr in self.pre]):
                self.state = 1
            else:
                self.state = 0


class NorGate(InputBit):

    def __init__(self, label, precedents=None, dependents=None):
        super().__init__(label, precedents, dependents)

    def determine_state(self):
        if self.pre:
            if any([pr.state for pr in self.pre]):
                self.state = 0
            else:
                self.state = 1


class Circuit:

    """Linked list of bits"""

    def __init__(self):
        self.elements = []

    def add(self, elements):
        if not isinstance(elements, type({})):
            self.elements.append(elements)
        else:
            for element in elements.values():
                self.elements.append(element)

    def remove(self, element):
        self.elements.remove(element)

    def switch(self, element):
        if element.state:
            element.state = 0
        else:
            element.state = 1
        # Only recalculate if it has no precedents (i.e. a battery)
        if not element.pre:
            self.recalculate_states()

    def set_state(self, input_bit, value):
        if isinstance(input_bit, InputBit):
            input_bit.state = value
            self.recalculate_states()

    def recalculate_states(self):
        for element in self.elements:
            element.determine_state()

    def generate_truth_table(self, inputs, outputs):
        truth_table = []
        width = (len(inputs) * 2 - 1) + (len(outputs) * 2 - 1) + 7
        # Top Border
        truth_table.append(["#" for i in range(0, width)])
        # Headers
        truth_table.append(["# "])
        # Input Headers
        for i in range(0, len(inputs) * 2 - 1):
            if (i + 1) % 2 != 0:
                name = inputs[i // 2].label
                truth_table[1].append(name)
            else:
                truth_table[1].append("|")
        truth_table[1].append(" | ")
        # Output headers
        for i in range(0, len(outputs) * 2 - 1):
            if (i + 1) % 2 != 0:
                name = outputs[i // 2].label
                truth_table[1].append(name)
            else:
                truth_table[1].append("|")
        truth_table[1].append(" #")
        # Values
        for i, p in enumerate(product("10", repeat=len(inputs))):
            truth_table.append(["# "])
            for j in range(0, len(inputs) * 2 - 1):
                if (j + 1) % 2 != 0:
                    self.set_state(inputs[j // 2], int(p[j // 2]))
                    truth_table[i + 2].append(p[j // 2])
                else:
                    truth_table[i + 2].append("|")
            truth_table[i + 2].append(" | ")
            for j in range(0, len(outputs) * 2 - 1):
                if (j + 1) % 2 != 0:
                    truth_table[i + 2].append(str(outputs[j // 2].state))
                else:
                    truth_table[i + 2].append("|")
            truth_table[i + 2].append(" #")
        # Bottom border
        truth_table.append(["#" for i in range(0, width)])
        # Print it
        for line in truth_table:
            print("".join(line))


if __name__ == "__main__":

    circ = Circuit()
    # circ_e = address decoder elements
    circ_e = {"power": InputBit(label="P", precedents=[]),
                            # Address selector bits ABC
                            "A": InputBit(label="A"),
                            "B": InputBit(label="B"),
                            "C": InputBit(label="C")}

    # I input setup (ABC = 111)
    circ_e["IA"] = AndGate(label="IA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["IB"] = AndGate(label="IB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["IC"] = AndGate(label="IC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["IAAndIB"] = AndGate(label="IAAndIB", precedents=[circ_e["IA"], circ_e["IB"]])
    Iinp1 = circ_e["IC"]
    Iinp2 = circ_e["IAAndIB"]

    # Address Decoder
    # J input setup (ABC = 110)
    circ_e["JA"] = AndGate(label="JA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["JB"] = AndGate(label="JB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["JC"] = AndGate(label="JC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["JAAndJB"] = AndGate(label="JAAndJB", precedents=[circ_e["JA"], circ_e["JB"]])
    circ_e["NotJC"] = NorGate(label="NotJC", precedents=[circ_e["JC"]])
    Jinp1 = circ_e["NotJC"]
    Jinp2 = circ_e["JAAndJB"]
    
    # K input setup (ABC = 101)
    circ_e["KA"] = AndGate(label="KA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["KB"] = AndGate(label="KB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["NotKB"] = NorGate(label="NotKB", precedents=[circ_e["KB"]])
    circ_e["KC"] = AndGate(label="KC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["KAAndNotKB"] = AndGate(label="KAAndNotKB", precedents=[circ_e["KA"], circ_e["NotKB"]])
    Kinp1 = circ_e["KAAndNotKB"]
    Kinp2 = circ_e["KC"]

    # L input setup (ABC = 100)
    circ_e["LA"] = AndGate(label="LA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["LB"] = AndGate(label="LB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["NotLB"] = NorGate(label="NotLB", precedents=[circ_e["LB"]])
    circ_e["LC"] = AndGate(label="LC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["NotLC"] = NorGate(label="NotLC", precedents=[circ_e["LC"]])
    circ_e["LAAndNotLB"] = AndGate(label="LAAndNotLB", precedents=[circ_e["LA"], circ_e["NotLB"]])
    Linp1 = circ_e["LAAndNotLB"]
    Linp2 = circ_e["NotLC"]

    # M input setup (ABC = 011)
    circ_e["MA"] = AndGate(label="MA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["NotMA"] = NorGate(label="NotMA", precedents=[circ_e["MA"]])
    circ_e["MB"] = AndGate(label="MB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["MC"] = AndGate(label="MC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["NotMAAndMB"] = AndGate(label="NotMAAndMB", precedents=[circ_e["NotMA"], circ_e["MB"]])
    Minp1 = circ_e["NotMAAndMB"]
    Minp2 = circ_e["MC"]
    
    # N input setup (ABC = 010)
    circ_e["NA"] = AndGate(label="NA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["NotNA"] = NorGate(label="NotNA", precedents=[circ_e["NA"]])
    circ_e["NB"] = AndGate(label="NB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["NC"] = AndGate(label="NC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["NotNC"] = NorGate(label="NotNC", precedents=[circ_e["NC"]])
    circ_e["NotNAAndNB"] = AndGate(label="NotNAAndNB", precedents=[circ_e["NotNA"], circ_e["NB"]])
    Ninp1 = circ_e["NotNAAndNB"]
    Ninp2 = circ_e["NotNC"]

    # O input setup (ABC = 001)
    circ_e["OA"] = AndGate(label="OA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["NotOA"] = NorGate(label="NotOA", precedents=[circ_e["OA"]])
    circ_e["OB"] = AndGate(label="OB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["NotOB"] = NorGate(label="NotOB", precedents=[circ_e["OB"]])
    circ_e["OC"] = AndGate(label="OC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["NotOAAndNotOB"] = AndGate(label="NotOAAndNotOB", precedents=[circ_e["NotOA"], circ_e["NotOB"]])
    Oinp1 = circ_e["NotOAAndNotOB"]
    Oinp2 = circ_e["OC"]

    # P input setup (ABC = 000)
    circ_e["PA"] = AndGate(label="PA", precedents=[circ_e["power"], circ_e["A"]])
    circ_e["NotPA"] = NorGate(label="NotPA", precedents=[circ_e["PA"]])
    circ_e["PB"] = AndGate(label="PB", precedents=[circ_e["power"], circ_e["B"]])
    circ_e["NotPB"] = NorGate(label="NotPB", precedents=[circ_e["PB"]])
    circ_e["PC"] = AndGate(label="PC", precedents=[circ_e["power"], circ_e["C"]])
    circ_e["NotPC"] = NorGate(label="NotPC", precedents=[circ_e["PC"]])
    circ_e["NotPAAndNotPB"] = AndGate(label="NotPAAndNotPB", precedents=[circ_e["NotPA"], circ_e["NotPB"]])
    Pinp1 = circ_e["NotPC"]
    Pinp2 = circ_e["NotPAAndNotPB"]

    # Outputs IJKLMNOP
    circ_e["I"] = AndGate(label="I", precedents=[Iinp1, Iinp2])
    circ_e["J"] = AndGate(label="J", precedents=[Jinp1, Jinp2])
    circ_e["K"] = AndGate(label="K", precedents=[Kinp1, Kinp2])
    circ_e["L"] = AndGate(label="L", precedents=[Linp1, Linp2])
    circ_e["M"] = AndGate(label="M", precedents=[Minp1, Minp2])
    circ_e["N"] = AndGate(label="N", precedents=[Ninp1, Ninp2])
    circ_e["O"] = AndGate(label="O", precedents=[Oinp1, Oinp2])
    circ_e["P"] = AndGate(label="P", precedents=[Pinp1, Pinp2])

    circ.add(circ_e)

    circ.switch(circ_e["power"])
    truth_table_inputs = [circ_e["power"], circ_e["A"], circ_e["B"], circ_e["C"]]
    truth_table_outputs = [circ_e["I"], circ_e["J"], circ_e["K"], circ_e["L"], circ_e["M"], circ_e["N"], circ_e["O"], circ_e["P"]]
    circ.generate_truth_table(inputs=truth_table_inputs, outputs=truth_table_outputs)


