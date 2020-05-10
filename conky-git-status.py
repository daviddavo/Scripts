#!/usr/bin/python3

import sys, os
import threading
import logging
import sh
import git
from git import Repo

FIND_MAXDEPTH=2 # ./**/.git

TITLE_STRING = "${{goto 40}}${{color2}}{0}${{color}}{1}"

def item_string(item, symbol=None, color="#5F9EA0"):
    if isinstance(item, git.diff.Diff):
        path = item.a_path
        if symbol == None: symbol = item.change_type
    else:
        path = item

    path = path.replace("#", "\\#")

    return "${{alignr}}{0} ${{color {2}}}{1}${{color}}".format(path, symbol, color)

def should_fetch(path):
    return False

def should_status(path):
    return True

def fetching(path):
    return False 

def fetch(path):
    pass

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

def process_status(repo, dname):
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

def process_repo(path, dname):
    if dname==None:
        dname = os.path.basename(path)

    repo = Repo(path)
    logging.debug(repo)
    logging.debug(f"bare             {repo.bare}")
    logging.debug(f"working_dir      {repo.working_dir}")
    logging.debug(f"git_dir          {repo.git_dir}")
    logging.debug(f"working_tree_dir {repo.working_tree_dir}")
    # logging.debug(f"git              {repo.git}")
    # logging.debug(f"active_branch    {repo.active_branch}")

    try:
        if should_fetch(path):
            if not fetching:
                fetch(path)
            else:
                # Show title but with a "fetching" thing
                pass
        elif should_status(path):
            # TODO: Instead of master, use current branch
            # TODO: Display current branch in title if it's different to master
            ahead = sum(1 for _ in repo.iter_commits("master..origin/master"))
            behind = sum(1 for _ in repo.iter_commits("origin/master..master"))
            if repo.is_dirty():
                display_title(path, dname, ok=False, ahead=ahead, behind=behind)
                process_status(repo, dname)
            else:
                display_title(path, dname, ok=True, ahead=ahead, behind=behind)

    except Exception as e:
        display_title(path, dname, error=True)
        logging.exception(f"Couldn't process repo {dname} in {path}")

def main(argv):
    repos_arr = [
        ("~/.config/yadm/repo.git/", "Yadm"), 
        ("~/Scripts", "Scripts")
    ]
    repos_arr.extend([(x.strip('\n'), None) for x in sh.find(os.path.expanduser("~/Documentos"), 
        "-name", ".git", "-type", "d", "-prune", "-maxdepth", FIND_MAXDEPTH)])

    for path, dname in repos_arr:
        path = os.path.expanduser(path)
        head,tail = os.path.split(path)
        if tail == ".git": path = head

        process_repo(path, dname)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main(sys.argv)
