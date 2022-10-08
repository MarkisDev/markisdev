from github import Github, InputGitTreeElement
import feedparser
import dateutil.parser
from dominate.tags import *
import time
import os


class BlogUpdater:
    def __init__(self, filepath, token, repository, validMoves):
        self.filepath = filepath
        self.repo = Github(token).get_repo(repository)
        self.validMoves = validMoves

    def getFileData(self):
        self.file = self.repo.get_contents(
            self.filepath)
        self.fileData = self.file.decoded_content.decode('utf-8')

    def getPosts(self, link):
        feed = [item for item in feedparser.parse(link).entries]
        feed.sort(key=lambda x: dateutil.parser.parse(
            x['published']), reverse=True)
        return [{'title': i['title'], 'date': i['published'], 'link': i['link']}
                for i in feed[:5]]

    def genRecentPosts(self):
        thotflow = self.getPosts('https://thotflow.xyz/index.xml')
        hashnode = self.getPosts('https://rijuth.hashnode.dev/rss.xml')
        com = 'BLOGS'
        outerTab = table(tr(th('Thotflow'), th('Hashnode')))
        with outerTab:
            for i in range(min(len(thotflow), len(hashnode))):
                with outerTab:
                    tr(td(a(thotflow[i]['title'], href=thotflow[i]['link'])), td(
                        a(hashnode[i]['title'], href=hashnode[i]['link'])))
        outerTab.add(tr(td(a('Click here for more! :zap: ', href='https://thotflow.xyz')),
                     td(a('Click here for more! :zap: ', href='https://rijuth.hashnode.dev'))))
        outerTab = details(
            summary(b(':rocket: Click here for my blogs')), br(), outerTab)
        outer = div(comment(f'BEGIN {com}'), outerTab, comment(
            f'END {com}'))
        # Replacing outer div to only keep comment
        data = str(outer.render()).replace(
            '<div>', '', 1)[::-1].replace('>vid/<', '', 1)[::-1]
        self.getFileData()
        self.updateData(com, data)

        self.repo.update_file(
            self.filepath, 'Updated with new blogs', self.fileData, self.file.sha)

    def updateData(self, com, data):
        start = comment(f'BEGIN {com}')
        end = comment(f'END {com}')
        temp = self.fileData
        temp = temp.split(str(start))
        firstHalf = temp[0]
        lastHalf = temp[1].split(str(end))[1]
        self.fileData = '\n'.join([firstHalf.strip(), data, lastHalf.strip()])

    def isValid(self):
        issues = self.repo.get_issues(state='open')
        temp = []
        temp_dt = []
        for issue in issues:
            if(len(issue.title.split('|')) > 1):
                temp.append(issue)
                temp_dt.append(issue.created_at)
        if len(temp) <= 1:
            temp[0].edit(state="closed")
            temp[0].create_comment('Updated blogs :rocket:')
            temp[0].set_labels('blog')
            return True
        else:
            minIssue = temp[temp_dt.index(min(temp_dt))]
            minIssueTitle = minIssue.title.lower().split('|')
            if minIssueTitle[0] != 'blog':
                if minIssueTitle[0] in self.validMoves:
                    time.sleep(30)
                    return self.isValid()
                else:
                    minIssue.edit(state="closed")
                    minIssue.create_comment('Invalid issue, closing it...')
                    return self.isValid()
            else:
                minIssue.edit(state="closed")
                minIssue.create_comment('Updated blogs :rocket:')
                minIssue.set_labels('blog')
                return True


if __name__ == '__main__':
    run = BlogUpdater('README.md', os.environ['TOKEN'], os.environ['REPO'], [
                      'blog', 'mastermind'])
    if run.isValid():
        run.genRecentPosts()
