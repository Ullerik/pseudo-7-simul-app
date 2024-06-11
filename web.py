import numpy as np
import random

# Clock class

class Clock:
    def __init__(self):
        self.clocks = np.zeros(14, dtype=int) # first 4 are corners, next 8 are edges, last 2 are centers
        self.pins = np.ones(4, dtype=int)

    def __repr__(self):
        str_repr = f"Pins: {self.pins}\n"
        str_repr += f"corners: {self.clocks[:4]}\n"
        str_repr += f"edges front: {self.clocks[4:8]}\n"
        str_repr += f"edges back: {self.clocks[8:12]}\n"
        str_repr += f"centers: {self.clocks[12:]}\n"

        c = self.clocks
        p = self.pins
        str_repr = "Front:\n"
        str_repr += f"{c[3]} {c[4]} {c[0]}\n"
        # str_repr += f" {p[3]} {p[0]}\n"
        str_repr += f"{c[7]} {c[12]} {c[5]}\n"
        # str_repr += f" {p[2]} {p[1]}\n"
        str_repr += f"{c[2]} {c[6]} {c[1]}\n"
        str_repr += "Back:\n"
        str_repr += f"{(12-c[0])%12} {(12-c[8])%12} {(12-c[3])%12}\n"
        # str_repr += f" {-p[0]} {-p[3]}\n"
        str_repr += f"{(12-c[9])%12} {(12-c[13])%12} {(12-c[11])%12}\n"
        # str_repr += f" {-p[1]} {-p[2]}\n"
        str_repr += f"{(12-c[1])%12} {(12-c[10])%12} {(12-c[2])%12}\n"

        return str_repr

    def set_pins(self, pins):
        # pins is an array of 4 elements, 1 or -1
        self.pins = pins

    def change_pin(self, pin):
        # index 0-3, the pin changes from 1 to -1 or -1 to 1
        self.pins[pin] *= -1

    def change_piece(self, index, amount):
        # index 0-13, the piece changes by amount (0-11)
        self.clocks[index] = (self.clocks[index] + amount) % 12

    def apply_move(self, corner, amount):
        # corner is 0-3, amount is 0-11

        pin_list = []
        for i in range(4):
            if self.pins[i] == self.pins[corner]:
                pin_list.append(i)

        # make a list of the pieces that will turn
        turn_list = pin_list.copy() # corners

        # edges: if self.pins[corner] == 1, we look at the first 4 edges (4-7), if -1, we look at the last 4 edges (8-11)
        edge_start = 4 if self.pins[corner] == 1 else 8
        # for each pin in pin_list, we add the corresponding edge and the next % 4 edge to turn_list, only if they are not already in turn_list
        for pin in pin_list:
            if edge_start + pin not in turn_list:
                turn_list.append(edge_start + pin)
            if edge_start + (pin + 1) % 4 not in turn_list:
                turn_list.append(edge_start + (pin + 1) % 4)

        # if self.pins[corner] == 1, we turn the first center, if -1, we turn the second center
        turn_list.append(12 if self.pins[corner] == 1 else 13)
        
        # for each piece in turn_list, we change the piece by amount
        for i in turn_list:
            self.change_piece(i, amount)

    def y2(self):
        # swaps corners 0-1, and 2-3, edges 4 with 8, 5 with 9, 6 with 10, 7 with 11, and centers 12 with 13. Pins are inverted and swapped 0-1 and 2-3
        self.clocks[[0, 3]] = self.clocks[[3, 0]]
        self.clocks[[1, 2]] = self.clocks[[2, 1]]
        self.clocks[[4, 8]] = self.clocks[[8, 4]]
        self.clocks[[5, 11]] = self.clocks[[11, 5]]
        self.clocks[[6, 10]] = self.clocks[[10, 6]]
        self.clocks[[7, 9]] = self.clocks[[9, 7]]
        self.clocks[[12, 13]] = self.clocks[[13, 12]]
        # invert all clocks
        self.clocks = (12 - self.clocks)%12

        self.pins[0], self.pins[3] = self.pins[3], self.pins[0]
        self.pins[1], self.pins[2] = self.pins[2], self.pins[1]

        # invert pins:
        for i in range(4):
            self.pins[i] *= -1
# Scramble generator

def gen_scramble():
    # how it works:
    # first a UR move, then DR, then DL, then UL, then U, then R, then D, then L, then ALL, then y2, then U, then R, then D, then L, then ALL

    moves = ["UR", "DR", "DL", "UL", "U", "R", "D", "L", "ALL", "y2", "U", "R", "D", "L", "ALL"]

    scramble = ""
    for move in moves:
        turn = random.randint(0, 11)
        # if turn > 6, we make it 12-turn and add a - instead of a +
        sign = "+" if turn <= 6 else "-"
        turn = 12 - turn if turn > 6 else turn

        # y2 should be added plain
        if move == "y2":
            scramble += f"{move} "
        else:
            scramble += f"{move}{turn}{sign} "

    return scramble[:-1] # remove the last space

# Scramble interpreter

def scramble_interpretor(scramble):
    # returns a list of numbers 0-11
    # UR5+ DR6+ DL0+ UL6+ U1+ R5+ D5+ L5+ ALL3+ y2 U5+ R0+ D2- L5- ALL0+ 
    # converts to [5, 1, 10, 5, 3, 2, 0, 0, 0, 6, 8, 1, 5, 0]
    moves = scramble.split()
    turns = []
    for move in moves:
        if move != "y2":
            sign = move[-1]
            move = move[:-1]
            amount = int(move[-1])
            if sign == "-":
                amount = 12 - amount
            turns.append(amount)
    
    return turns

pin_dict = {
    "UR": [1, -1, -1, -1],
    "DR": [-1, 1, -1, -1],
    "DL": [-1, -1, 1, -1],
    "UL": [-1, -1, -1, 1],
    "U": [1, -1, -1, 1],
    "R": [1, 1, -1, -1],
    "D": [-1, 1, 1, -1],
    "L": [-1, -1, 1, 1],
    "ALL": [1, 1, 1, 1],
}

pin_states = []
for key in ["UR", "DR", "DL", "UL", "U", "R", "D", "L", "ALL"]:
    pin_states.append(pin_dict[key].copy())
for key in ["U", "R", "D", "L", "ALL"]:
    pin_states.append(pin_dict[key].copy())

def scramble_clock(clock, scramble, pin_states = pin_states, corners = [0,1,2,3,0,1,2,3,0,0,1,2,3,0]):
    turns = scramble_interpretor(scramble)
    for i in range(9):
        clock.set_pins(pin_states[i])
        clock.apply_move(corners[i], turns[i])

    clock.y2()
    
    for i in range(9, 14):
        clock.set_pins(pin_states[i])
        clock.apply_move(corners[i], turns[i])


def get_random_clock():
    clock = Clock()
    scramble = gen_scramble()
    scramble_clock(clock, scramble)
    return clock, scramble


# cases
def case1(clock):
    # check for L shape on one side, then the other side
    for i in range(4):
        if clock.clocks[12] == clock.clocks[4+i] == clock.clocks[4+((i+1)%4)]:
            return True
    for i in range(4):
        if clock.clocks[13] == clock.clocks[8+i] == clock.clocks[8+((i+1)%4)]:
            return True
    return False

def case2(clock, flip = True):
    # we only check for one side. if it doesn't find the case, then we do a y2 and call the function again with flip = False

    # center-edge match on one side and edge-edge match on the opposite side in a specific way. center-edge, then the edge on the other side (4 and 8, 5 and 9, 6 and 10, 7 and 11), and the final edge on the opposite side should be the one anticlockwise, so 8->9->10->11->8, or 7->6->5->4->7
    for i in range(4):
        if clock.clocks[12] == clock.clocks[4+i]:
            # we found a center-edge match
            # now we need to check for the edge-edge match on the other side
            # we simply calculate the next numbers and check if they match
            if clock.clocks[8+i] == clock.clocks[8+((i+1)%4)]:
                return True
    if flip:
        clock.y2()
        return case2(clock, False)
    return False

def case3(clock, flip = True):
    # check only one side, if it doesn't find the case, then we do a y2 and call the function again with flip = False
    # L = U and C = D on the same side (any orientation), so center-edge, and edge-edge where those two are the two edges clockwise from the edge in the center-edge pair

    for i in range(4):
        if clock.clocks[12] == clock.clocks[4+i]:
            # we found a center-edge match
            # now we need to check for the edge-edge match on the same side
            # we simply calculate the next numbers and check if they match
            if clock.clocks[4+((i+1)%4)] == clock.clocks[4+((i+2)%4)]:
                if not flip:
                    clock.y2() # we need to do a y2 to get back to the original state
                return True
            
    if flip:
        clock.y2()
        return case3(clock, False)

    return False

def case4(clock, flip = True):
    # C=D x2 R=D
    # check only one side, if it doesn't find the case, then we do a y2 and call the function again with flip = False
    
    for i in range(4):
        if clock.clocks[12] == clock.clocks[4+i]:
            # we found a center-edge match
            # now we need to check for the edge-edge match on the same side
            # we simply calculate the next numbers and check if they match

            # we need to first check the edge on the opposite side, by checking by the pattern below:
            # 4-10, 5-11, 6-8, 7-9, so if our edge is 4, we need to check if 10 and the one anticlockwise from that one is the same

            if clock.clocks[8 + ((i+2)%4)] == clock.clocks[8 + ((i+3)%4)]:
                if not flip:
                    clock.y2() # we need to do a y2 to get back to the original state
                return True
    if flip:
        clock.y2()
        return case4(clock, False)

    return False

def case5(clock):
    # check for line shape on both sides
    for i in range(2):
        if clock.clocks[12] == clock.clocks[4+i] == clock.clocks[4+((i+2)%4)]:
            return True
    for i in range(2):
        if clock.clocks[13] == clock.clocks[8+i] == clock.clocks[8+((i+2)%4)]:
            return True
    return False

def case6(clock):
    # C = D & C = D
    for i in range(4):
        if clock.clocks[12] == clock.clocks[4+i]:
            # we found a center-edge match
            # now we need to check for center-edge on the other side such that the edge is opposite of the one we found
            # 4-10, 5-11, 6-8, 7-9, so if our edge is 4, we check if 10 is the same as the center (13)
            if clock.clocks[8 + ((i+2)%4)] == clock.clocks[13]:
                return True
    return False

def case7(clock, flip = True):
    # u = c & (U-C+D) + (ul-l) + (dr-r) = (u-c+d) + (UL-L) + (DR-R) (capital letters front side and small letters back side, split by a y2)
    c = clock.clocks
    for i in range(4):
        if c[13] == c[8+(-i)%4]:
            # left hand side: (U - C + D) + (l - ul) + (r - dr)
            lhs = (c[4+i] - c[12] + c[4+(i+2)%4]) + (c[8+(-i+1)%4] - c[(-i)%4]) + (c[8+(-i+3)%4] - c[(2-i)%4])
            # right hand side: (12-d) + (UL - L) + (DR - R)
            rhs = (12-c[8+(2-i)%4]) + (c[(3+i)%4] - c[4+(3+i)%4]) + (c[(1+i)%4] - c[4+(1+i)%4])
            if lhs%12 == rhs%12:
                if not flip:
                    clock.y2()
                return True
    if flip:
        clock.y2()
        return case7(clock, False)
    return False



import streamlit as st

case_functions = [case1, case2, case3, case4, case5, case6, case7]
case_names = ["L shape", "CE & EE (opposite sides)", "L=U & C=D (same side)", "C=D & R=D (opposite side)", "Line shape", "C=D & C=D (opposite sides)", "Slash move skip"]


def scramble(selected_cases):
    if not selected_cases:
        st.warning("Please select at least one case to test.")
        return None, None
    
    while True:
        clock, scr = get_random_clock()
        if any(case(clock) for case in selected_cases):
            return scr, clock

# Streamlit app
st.title("Epic Clock Scrambler")
st.write("Select the cases you want to test for and click 'Generate Scramble':")

selected_cases = []
for i, case_name in enumerate(case_names):
    if st.checkbox(f"Case {i+1}: {case_name}"):
        selected_cases.append(case_functions[i])

font_size = 20

if st.button("Generate Scramble"):
    scr, clock = scramble(selected_cases)
    if scr and clock:
        st.write("**Scramble:**")
        st.write(scr)
        st.write("**Clock:**")
        st.write(clock,)

st.write("Made by Ulrik Bredland (2012BRED01)")