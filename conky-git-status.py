#!/usr/bin/python3

import sys, os
from datetime import datetime, timedelta
import logging
import sh
import pickle
import git
from git import Repo

FIND_MAXDEPTH=2 # ./**/.git
TITLE_STRING = "${{goto 40}}${{color2}}{0}${{color}}{1}"
YADM_REPO = os.path.expanduser("~/.config/yadm/repo.git")
DEFAULT_MEMENTO_PATH = "/tmp/conky-git-status.pickle"
FETCH_INTERVAL = timedelta(seconds=30)

class RepoMemento:
    coso = "Holiiiii"
    fetching = False
    lastfetch = None

    """
    def __getstate__(self):
        logging.info(self.__dict__)
        return self.__dict__
    """

class ProgramMemento:
    __repodict = {}

    def __init__(self):
        pass

    def __getitem__(self, key):
        path = key
        if isinstance(key, Repo): path = key.git_dir
        else: raise TypeError("Key should be repo")

        if not path in self.__repodict.keys():
            self.__repodict[path] = RepoMemento()

        return self.__repodict[path]

    def save(self, path = DEFAULT_MEMENTO_PATH):
        with open(path, 'wb') as f:
            pickle.dump(self.__repodict, f)

    def load_if_possible(self, path = DEFAULT_MEMENTO_PATH):
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            self.load(path)
        else:
            logging.debug("Creating new pickle file")

    def load(self, path = DEFAULT_MEMENTO_PATH):
        with open(path, 'rb') as f:
            # There is no problem in python with doing this :D
            self.__repodict = pickle.load(f)

def item_string(item, symbol=None, color="#5F9EA0"):
    if isinstance(item, git.diff.Diff):
        path = item.a_path
        if symbol == None: symbol = item.change_type
    else:
        path = item

    path = path.replace("#", "\\#")

    return "${{alignr}}{0} ${{color {2}}}{1}${{color}}".format(path, symbol, color)

def should_fetch(repo, memento):
    lastfetch = memento[repo].lastfetch
    return lastfetch is not None and lastfetch + FETCH_INTERVAL < datetime.now()

def should_status(path):
    return True

def fetching(path, memento):
    return False 

def fetch(repo, memento):
    memento[repo].lastfetch = datetime.now()
    for remote in repo.remotes:
        logging.info(f"Fetching remote {remote} in repo {repo.git_dir}")
        remote.fetch()

def display_title(path, displayname=None, ok=True, error=False, ahead=0, behind=0, fetching=False):
    bhstr = ""
    
    if error:
        bhstr = "${alignr}${color red}ERR${color}"
    else:
        if ahead > 0 and behind == 0:
            bhstr = f"${{alignr}}${{color green}}[{ahead}]${{color}}"
        elif ahead == 0 and behind > 0:
            bhstr = f"${{alignr}}${{color red}}[{behind}]${{color}}"
        elif ahead > 0 and behind > 0:
            bhstr = f"${{alignr}}${{color green}}[{ahead},${{color red}}{behind}]${{color}}"
        elif ok and ahead == 0 and behind == 0:
            bhstr = f"${{alignr}}${{color #5f9ea0}}OK${{color}}"

    print(TITLE_STRING.format(displayname, bhstr))

def process_status(repo, dname, display_untracked=True):
    
    if display_untracked:
        # Untracked file
        for path in repo.untracked_files:
            print(item_string(path, symbol="??", color="yellow")) 
            pass

    # Non-staged files
    for item in repo.index.diff(None):
        # print("\n".join([f">>> {attr}: {getattr(item, attr)}" for attr in dir(item) if not attr.startswith("__")]))
        print(item_string(item, color="red"))
        # print("-"*60)

    for item in repo.index.diff("HEAD"):
        # print("\n".join([f">>> {attr}: {getattr(item, attr)}" for attr in dir(item) if not attr.startswith("__")]))
        print(item_string(item, color="green"))
        # print("-"*60)

def process_repo(path, dname, memento, display_untracked=True):
    if dname==None:
        dname = os.path.basename(path)

    repo = Repo(path)
    logging.debug(repo)
    logging.debug(f"bare              {repo.bare}")
    logging.debug(f"working_dir       {repo.working_dir}")
    logging.debug(f"git_dir           {repo.git_dir}")
    logging.debug(f"working_tree_dir  {repo.working_tree_dir}")
    logging.debug(f"common_dir        {repo.common_dir}")
    logging.debug(f'is_git_dir        {git.repo.fun.is_git_dir(path)}')
    logging.debug(f'display_untracked {display_untracked}')
    # logging.debug(f"git              {repo.git}")
    # logging.debug(f"active_branch    {repo.active_branch}")

    try:
        if fetching(repo, memento):
            # Show title but with a "fetching" thing
            pass
        elif should_fetch(repo, memento):
            logging.info(f"Should fetch {repo}")
            fetch(repo, memento)

        if should_status(path):
            # TODO: Instead of master, use current branch
            # TODO: Display current branch in title if it's different to master
            ahead = sum(1 for _ in repo.iter_commits("master..origin/master"))
            behind = sum(1 for _ in repo.iter_commits("origin/master..master"))
            if repo.is_dirty():
                display_title(path, dname, ok=False, ahead=ahead, behind=behind)
                process_status(repo, dname, display_untracked)
            else:
                display_title(path, dname, ok=True, ahead=ahead, behind=behind)

    except Exception as e:
        display_title(path, dname, error=True)
        logging.exception(f"Couldn't process repo {dname} in {path}")

def main(argv):
    repos_arr = [
        ("~/Scripts", "Scripts")
    ]
    repos_arr.extend([(x.strip('\n'), None) for x in sh.find(os.path.expanduser("~/Documentos"), 
        "-name", ".git", "-type", "d", "-prune", "-maxdepth", FIND_MAXDEPTH)])

    memento = ProgramMemento()
    memento.load_if_possible()
    # We process yadm this way cos it's special
    os.environ["GIT_DIR"] = YADM_REPO
    process_repo(YADM_REPO, "Yadm", memento, False)
    del os.environ["GIT_DIR"]

    for path, dname in repos_arr:
        path = os.path.expanduser(path)
        head,tail = os.path.split(path)
        if tail == ".git": path = head
        
        process_repo(path, dname, memento)

    memento.save()

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main(sys.argv)
