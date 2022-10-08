from email.mime import base
import json
import base64
import random


class Game:

    def __init__(self, file, guesses, length, user, colors, fileData, validMoves):
        self.data = json.loads(fileData)
        self.file = file
        self.guesses = guesses
        self.length = length
        self.user = user
        self.colors = [color for sublist in colors for color in sublist]
        self.validMoves = validMoves

    def genCode(self):
        code = []
        while len(code) < self.length:
            rint = random.randint(0, len(self.colors)-1)
            if(self.colors[rint] not in code):
                code.append(self.colors[rint])
            self.data['code'] = base64.b64encode(
                bytes(' '.join(code), encoding='utf8')).decode('utf-8')
        self.updateData()

    def initBoard(self):
        temp_data = []
        for row in range(self.guesses):
            temp_row = []
            for value in range(self.length):
                temp_row.append('blank')
            temp_data.append(temp_row)
        self.data['state'] = temp_data
        self.updateData()

    def getState(self):
        return self.data['state']

    def makeMove(self, color):
        state = self.data['state']
        self.data['total_moves'] += 1
        flag = True
        for row in state:
            if flag:
                if 'blank' in row:
                    row[row.index('blank')] = color
                    self.updateData()
                    flag = False
                    return row

    def resetBoard(self):
        self.data['correct_position'] = 0
        self.data['correct_code'] = 0
        self.data['total_games'] += 1
        self.initBoard()
        self.updateData()

    def checkBoard(self, row):
        code = base64.b64decode(self.data['code']).decode("utf-8").split()
        self.data['correct_position'] = 0
        self.data['correct_code'] = 0
        if(code == row):
            if self.user not in self.data['users'].keys():
                self.data['users'][self.user] = 1
            else:
                self.data['users'][self.user] += 1
            self.resetBoard()
            return True
        elif (row == self.data['state'][-1]):
            self.resetBoard()
            return False
        else:
            temp = []
            for i in range(len(row)):
                if row[i] == code[i]:
                    temp.append(row[i])
                    self.data['correct_position'] += 1
                    continue
                elif row[i] in code:
                    if(temp.count(row[i]) != code.count(row[i])):
                        temp.append(row[i])
                        self.data['correct_code'] += 1
                    continue
            self.updateData()
            return None

    def isValid(self, move):
        if move[0] in self.validMoves and move[1] in self.colors:
            return True
        else:
            return False

    def updateData(self):
        self.jsonData = json.dumps(self.data)
