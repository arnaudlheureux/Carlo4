# Arnaud L'Heureux

import random as rand
import time
import math

class Board:
    def __init__(self, nlines, ncolumns, data = []):
        self.nlines = nlines
        self.ncolumns = ncolumns
        self.data = []

        if(data == []) :
            for i in range(0, nlines):
                temp = []
                for j in range(0, ncolumns):
                    temp.append("_")
                self.data.append(temp)
        else :
            for i in range(0, nlines):
                temp = []
                for j in range(0, ncolumns):
                    temp.append(data[i][j])
                self.data.append(temp)

    def show(self):
        line = ""
        for i in range(0, self.ncolumns):
            line += str(i) + " "
        print(line)

        for i in range(0, self.nlines):
            line = ""
            for j in range(0, self.ncolumns):
                line += self.data[i][j] + " "
            print(line)

    def play(self, col, player):
        if(self.data[0][col] != '_'):
            return
        else :
            bottomFound = False
            i = 0

            while(not bottomFound):
                if(self.data[i][col] == '_' and i+1 == self.nlines):
                    self.data[i][col] = player
                    return col
                elif(self.data[i][col] == '_' and self.data[i+1][col] != '_'):
                    self.data[i][col] = player
                    return col
                i += 1

    # returns the list of potential moves given a certain board
    def potentialMoves(self):
        result = []

        for i in range(0, self.ncolumns):
            tempBoard = Board(self.nlines, self.ncolumns, self.data)

            # Using player T as temp, the actual value shouldn't matter
            if(tempBoard.play(i, 'T') == i):
                result.append(i)
            temp = None
            tempBoard = None

        return result

    #Returns if a player won ('X' or '0') or not ('_'), in case of a draw, returns '-'
    def check(self):
        # checking for a draw
        count = 0
        for i in range (0, self.nlines):
            for j in range (0, self.ncolumns):
                if(self.data[i][j] == '_'):
                    count += 1
        if (count == 0):
            # The grid has no empty spots and the game is thus a tie
            return '-'

        # Horizontal Check
        for i in range (0, self.nlines):
            for j in range (0, self.ncolumns - 3):
                if (self.data[i][j] == self.data[i][j+1] and self.data[i][j+1] == self.data[i][j+2] and self.data[i][j+2] == self.data[i][j+3] and self.data[i][j] != '_'):
                    return self.data[i][j];

        # Vertical Check
        for i in range (0, self.nlines - 3):
            for j in range (0, self.ncolumns):
                if (self.data[i][j] == self.data[i+1][j] and self.data[i+1][j] == self.data[i+2][j] and self.data[i+2][j] == self.data[i+3][j] and self.data[i][j] != '_'):
                    return self.data[i][j];

        # Ascending Diagonal Check 
        for i in range (3, self.nlines):
            for j in range (0, self.ncolumns - 3):
                if (self.data[i][j] == self.data[i-1][j+1] and self.data[i-1][j+1] == self.data[i-2][j+2] and self.data[i-2][j+2] == self.data[i-3][j+3] and self.data[i][j] != '_'):
                    return self.data[i][j];

        # Descending Diagonal Check 
        for i in range (3, self.nlines):
            for j in range (3, self.ncolumns):
                if (self.data[i][j] == self.data[i-1][j-1] and self.data[i-1][j-1] == self.data[i-2][j-2] and self.data[i-2][j-2] == self.data[i-3][j-3] and self.data[i][j] != '_'):
                    return self.data[i][j];
        return '_'

class Node:
    def __init__(self, board, numPlayout, numWins, parent = None):
        self.board = board
        self.numPlayout = numPlayout 
        self.numWins = numWins
        self.parent = parent
        self.children = []

    def addChild(self, child):
        self.children.append(child)

# Steps of monte carlo tree search
# 1 - Selection
# 2 - Simulation
# 3 - Backpropagation
# Receives a board and a budget and returns the most visited root child
# from the MCTS
def monteCarloTreeSearch(budget, board) :
    root = Node(board, 0, 0)

    for i in range(0, budget):
        node, height = selection(root, 0)

        # Determining which player's turn it is
        player = 'X'
        if(height % 2 == 0):
            player = '0'

        tempBoard = Board(node.board.nlines, node.board.ncolumns, node.board.data)

        result = simulate(tempBoard, player)

        if(result == 'X'):
            result = 1
        else:
            result = 0

        backProp(node, result)

    # return the best move, aka root child with highest playouts
    maxPlayouts = 0
    bestChild = None
    for child in root.children :
        if(child.numPlayout > maxPlayouts):
            maxPlayouts = child.numPlayout
            bestChild = child

    # determining which move was made from board state
    move = -1
    for i in range(0, root.board.nlines):
        for j in range(0, root.board.ncolumns):
            if(root.board.data[i][j] != bestChild.board.data[i][j]):
                move = j
    return move 


# Receives a node and recursively applies the selection policy until
# it reaches a node that hasen't been created or a terminal node
def selection(node, height) :
    if(node.board.check() == '_'):
        temp = node.board.potentialMoves()
        # We check if all possible children have been created
        if(len(temp) == len(node.children)):
            # We must select a child
            maxScore = - 1
            bestChild = None
            for child in node.children :
                score = child.numWins / child.numPlayout
                score += math.sqrt(2.0*math.log(node.numPlayout)/float(child.numPlayout))

                if(score > maxScore):
                    maxScore = score
                    bestChild = child

            return selection(bestChild, height + 1)

        else:
            # We must create a child (expand) and select it
            move = temp[len(node.children)]
            newBoard = Board(node.board.nlines, node.board.ncolumns, node.board.data)
            newChild = Node(newBoard, 0, 0, node)
            node.children.append(newChild)

            player = 'X'
            if(height % 2 == 1):
                player = '0'

            newChild.board.play(move, player)

            return newChild, height
    else :
        #We have reached a terminal node
        return node, height

# Returns an outcome of a simulated game
def simulate(board, player):
    temp = board.check()
    if(temp == '_'):
        # Non-terminal game state
            potentialMoves = board.potentialMoves()
            # making a random move
            board.play(rand.choice(potentialMoves), player)

            # Switching players
            if(player == '0'):
                player = 'X'
            else :
                player = '0'

            return simulate(board, player)

    else:
        return temp

def backProp(node, result):
    node.numPlayout += 1
    node.numWins += result

    if(node.parent != None):
        backProp(node.parent, result)

def interactiveMode():
    #Human player plays 0's and computer plays X's

    board = Board(6,7)
    gameOver = False
    player = '0'


    while (not gameOver):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print("Selectionnez la colonne dans laquelle vous voulez placer un\n\'0\' en appuyant sur le numéro de la colonne suivit de \"enter\"\n")
        board.show()
        # Human's Turn to play
        if(player == '0'):
            col = int(input())
            board.play(col, '0')

        # Computer's turn to play
        else :
            board.play(monteCarloTreeSearch(5000, board), 'X')

        # Check if there's a win
        res = board.check()

        if(res != '_' and res != '-'):
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            board.show()
            gameOver = True
            print(res + " Has won the game !")
        elif(res == '-'):
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            board.show()
            gameOver = True
            print("Game is a tie!")
        else :
            if(player == '0'):
                player = 'X'
            else :
                player = '0'

interactiveMode()

