from github import Github, InputGitTreeElement


class GithubAPI:

    def __init__(self, token, repository, issue, validMoves):
        self.token = token
        self.repo = Github(token).get_repo(repository)
        self.issue = self.repo.get_issue(issue)
        self.validMoves = validMoves

    def fetchFromRepo(self, filepath):
        return self.repo.get_contents(filepath).decoded_content.decode('utf-8')

    def writeToRepo(self, filepath, message, content, sha):
        self.repo.update_file(filepath, message, content, sha)

    def closeIssue(self):
        self.issue.edit(state="closed")

    def addComment(self, message):
        self.issue.create_comment(message)

    def addLabel(self, label):
        self.issue.set_labels(label)

    def addReaction(self, reaction):
        self.issue.create_reaction(reaction)

    def createGitBlob(self, content):
        return self.repo.create_git_blob(content, 'utf-8')

    def getBranch(self, name):
        for branch in self.repo.get_branches():
            if branch.name == name:
                return branch

    def getGitTree(self, branch):
        return self.repo.get_git_tree(branch.commit.sha)

    def createInputElement(self, path, mode, fileType, sha):
        return InputGitTreeElement(path, mode, fileType, sha=sha)

    def createGitTree(self, baseTree, *inputElements):
        return self.repo.create_git_tree([element for element in inputElements], baseTree)

    def addCommit(self, message, tree, *parents):
        return self.repo.create_git_commit(message, tree, [parent for parent in parents])

    def getRef(self, refString):
        return self.repo.get_git_ref(refString)

    def updateRef(self, ref, sha):
        ref.edit(sha=sha)

    def isValid(self):
        issues = self.repo.get_issues(state='open')
        temp = []
        temp_dt = []
        for issue in issues:
            if(len(issue.title.split('|')) > 1):
                temp.append(issue)
                temp_dt.append(issue.created_at)
        if len(temp) <= 1:
            return (True, self.issue.number)
        else:
            minIssue = temp[temp_dt.index(min(temp_dt))]
            if self.issue.number == minIssue.number:
                return (True, self.issue.number)
            else:
                if minIssue.title.lower().split('|')[0] in self.validMoves:
                    return (False, minIssue.number)
                else:
                    minIssue.edit(state="closed")
                    minIssue.create_comment('Invalid issue, closing it...')
                    return self.isValid()

    def getRecentMoves(self):
        users = []
        issues = self.repo.get_issues(
            state='all', labels=['mastermind'], sort='updated', direction='desc')
        for i in range(len(list(issues)[:3])):
            users.append(
                (issues[i].user.login, issues[i].user.html_url, issues[i].title.split('|')[1]))
        return users
