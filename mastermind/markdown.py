from dominate.tags import *
from dominate.util import text


class Markdown:
    def __init__(self, file, repository, fileData):
        self.file = file
        self.repository = repository
        self.fileData = fileData

    def genGameBoard(self, state, correctPosition, correctToken):
        tab = table()
        score = div(table(tr(th(f"Position : {correctPosition}", th(f"Color : {correctToken}")))), align="left")
        genTh = True
        com = 'GAME_BOARD'
        for i in range(len(state)):
            inner = tab.add(tr())
            for j in range(len(state[i])):
                if genTh:
                    inner.add(th(img(src=f'images/{state[i][j]}.png')))
                else:
                    inner.add(td(img(src=f'images/{state[i][j]}.png')))
            genTh = False
        tab = div(tab, align='left')
        outer = div(comment(f'BEGIN {com}'), score, tab, comment(
            f'END {com}'))
        # Replacing outer div to only keep comment
        data = str(outer.render()).replace(
            '<div>', '', 1)[::-1].replace('>vid/<', '', 1)[::-1]
        self.updateData(com, data)

    def genChoiceBoard(self, colors):
        tab = table()
        genTh = True
        com = 'CHOICE_BOARD'
        for i in range(len(colors)):
            inner = tab.add(tr())
            for j in range(len(colors[i])):
                if genTh:
                    inner.add(th(a(img(src=f'images/{colors[i][j]}.png'), href=f"https://github.com/{self.repository}/issues/new?title=mastermind|{colors[i][j]}")))
                else:
                    inner.add(td(a(img(src=f'images/{colors[i][j]}.png'), href=f"https://github.com/{self.repository}/issues/new?title=mastermind|{colors[i][j]}")))
            genTh = False
        tab = div(tab, align='left')
        outer = div(comment(f'BEGIN {com}'), tab, comment(
            f'END {com}'))
        # Replacing outer div to only keep comment
        data = str(outer.render()).replace(
            '<div>', '', 1)[::-1].replace('>vid/<', '', 1)[::-1]
        self.updateData(com, data)

    def genRecentMoves(self, users):
        tab = table()
        com = 'RECENT_MOVES'
        tab.add(tr(th('User'), th('Move')))
        for user in users:
            tab.add(tr(td(a(f'@{user[0]}', href=user[1])), td(img(src=f'images/{user[2]}.png'))))
        tab = div(tab, align='left')
        outer = div(comment(f'BEGIN {com}'), tab, comment(
            f'END {com}'))
        # Replacing outer div to only keep comment
        data = str(outer.render()).replace(
            '<div>', '', 1)[::-1].replace('>vid/<', '', 1)[::-1]
        self.updateData(com, data)

    def genMetaData(self, moves, games, players, winner):
        com = 'METADATA'
        metadata = []
        metadata.append(f'https://img.shields.io/badge/Moves%20played-{moves}-blue?style=for-the-badge')
        metadata.append(f'https://img.shields.io/badge/Completed%20games-{games}-brightgreen?style=for-the-badge')
        metadata.append(f'https://img.shields.io/badge/Total%20players-{players}-blueviolet?style=for-the-badge')
        inner = p()
        for data in metadata:
            with inner:
                img(src=data)
        para = p(b(__pretty=False))
        with para:
            text(":trophy: Recent user with winning move is ")
            a(f'@{winner}', href=f'https://github.com/{winner}')
            text(' :tada:')
        mainDiv = div(inner, para)
        outer = div(comment(f'BEGIN {com}'), mainDiv, comment(
            f'END {com}'))
        data = str(outer.render()).replace(
            '<div>', '', 1)[::-1].replace('>vid/<', '', 1)[::-1]
        self.updateData(com, data)

    def updateData(self, com, data):
        start = comment(f'BEGIN {com}')
        end = comment(f'END {com}')
        temp = self.fileData
        temp = temp.split(str(start))
        firstHalf = temp[0]
        lastHalf = temp[1].split(str(end))[1]
        self.fileData = '\n'.join([firstHalf.strip(), data, lastHalf.strip()])
