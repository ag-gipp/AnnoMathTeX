import os
import urllib3
urllib3.disable_warnings()
from github import Github



class DataRepoHandler:

    def __init__(self, token=os.getenv('apikey', False)):
        self.token = token

        if not token:
            print('Token not set')
            return

        self.g = Github(self.token)
        self.repo = self.g.get_repo("ag-gipp/dataAnnoMathTex")
        self.user = self.g.get_user()

    def commit_file(self, file_name, file_content):
        self.repo.create_file(file_name, "commiting file {}".format(file_name), file_content)
        return

    def delete_file(self, file_name):
        contents = self.repo.get_contents(file_name)
        self.repo.delete_file(file_name, "Deleting file {}".format(file_name), contents.sha)
        return


if __name__ == '__main__':
    """
    For testing purposes
    """
    from .key import token
    d = DataRepoHandler(token)
    d.commit_file('test.txt', 'test commit', 'test content')









