
import base64
from game import Game
from githubApi import GithubAPI
from markdown import Markdown
import os
from enum import Enum


class Constants(Enum):
    COLORS = [['red', 'blue', 'white'], ['purple', 'green', 'orange']]
    BOARD = 'mastermind/board.json'
    README = 'README.md'
    BRANCH = 'main'
    VALID_MOVES = ['mastermind', 'blog']


class Runner:
    def __init__(self, token, issue, repo):
        self.token = token
        self.issue = issue
        self.repo = repo
        self.colors = Constants.COLORS.value
        self.github = GithubAPI(
            token, repo, issue, Constants.VALID_MOVES.value)
        self.username = self.github.issue.user.login
        self.game = Game(Constants.BOARD.value, 7, 4,
                         self.username, self.colors, self.github.fetchFromRepo(Constants.BOARD.value), Constants.VALID_MOVES.value)
        self.markdown = Markdown(
            Constants.README.value, repo, self.github.fetchFromRepo(Constants.README.value))

    def playMove(self):
        self.move = self.github.issue.title.lower().split('|')
        if len(self.move) > 1 and self.game.isValid(self.move):
            valid = self.github.isValid()
            if valid[0]:
                self.github.addLabel('mastermind')
                row = self.game.makeMove(self.move[1])
                self.updateData(f'@{self.username} played {self.move[1]}!')
                if 'blank' in row:
                    self.github.addComment(f'Your move has been played! :rocket:')
                    self.github.addReaction('rocket')
                else:
                    result = self.game.checkBoard(row)
                    if (result == True):
                        self.game.genCode()
                        self.game.data['winner'] = self.github.issue.user.html_url
                        self.updateData(f'@{self.username} won and started a new game!')
                        self.github.addComment(f'Congratulations @{self.username}!\n You won :tada:')
                        self.github.addLabel('winner')
                        self.github.addReaction('hooray')
                    elif (result == False):
                        code = base64.b64decode(
                            self.game.data['code']).decode('utf-8')
                        self.updateData(f'@{self.username} started a new game!')
                        self.github.addComment(f'Uh-oh!\n @{self.username} the code was ***{code}*** :confused:')
                        self.github.addReaction('confused')
                    else:
                        self.updateData(f'@{self.username} completed a guess and got hints!')
                        self.github.addComment(f'Oops!\n @{self.username} keep trying :rocket:')
                        self.github.addReaction('rocket')
            else:
                self.github.addComment(f'Hey @{self.username}\n Your move wasn\'t executed since #{valid[1]} is currently active!\nPlease wait 30s before trying again! :muscle: ')
                self.github.addReaction('confused')

        else:
            self.github.addComment(f'Hey...No cheating!\n You played an invalid move :eyes:')
            self.github.addReaction('eyes')
        self.github.closeIssue()

    def writeFile(self, message):
        boardContents = self.game.jsonData
        readmeContents = self.markdown.fileData
        boardBlob = self.github.createGitBlob(boardContents)
        readmeBlob = self.github.createGitBlob(
            readmeContents)
        branch = self.github.getBranch(Constants.BRANCH.value)
        baseTree = self.github.getGitTree(branch)
        readmeInputTree = self.github.createInputElement(
            Constants.README.value, '100644', 'blob', readmeBlob.sha)
        boardInputTree = self.github.createInputElement(
            Constants.BOARD.value, '100644', 'blob', boardBlob.sha)
        newTree = self.github.createGitTree(
            baseTree, readmeInputTree, boardInputTree)
        commit = self.github.addCommit(message, newTree, branch.commit.commit)
        ref = self.github.getRef(f'heads/{Constants.BRANCH.value}')
        self.github.updateRef(ref, commit.sha)

    def updateData(self, msg):
        self.markdown.genGameBoard(self.game.getState(
        ), self.game.data['correct_position'], self.game.data['correct_code'])
        self.markdown.genRecentMoves(self.github.getRecentMoves())
        self.markdown.genMetaData(self.game.data['total_moves'], self.game.data['total_games'],
                                  len(self.game.data['users']), self.game.data['winner'])
        self.writeFile(msg)


if __name__ == '__main__':
    run = Runner(os.environ['TOKEN'], int(
        os.environ['ISSUE_NUMBER']), os.environ['REPO'])
    run.playMove()
