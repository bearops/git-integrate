#!/usr/bin/env python
import re
import sys
import time
import datetime
import subprocess


DEFAULT_BRANCH_PATTERN = re.compile(r'^origin/release_\d{4}_\d{1,2}_\d{1,2}$')


def abort_merge():
    cmd = "git reset --hard origin && git checkout master"
    subprocess.call(cmd, shell=True)


def get_remote_branches(pattern=None, merged_only=False):
    cmd = "git branch --remotes --list"
    if merged_only:
        cmd = "%s --merged origin/master" % cmd

    branches = subprocess.check_output(cmd, shell=True).split()

    if pattern:
        branches = [branch for branch in branches if re.match(pattern, branch)]

    return branches


def get_time_stamp(branch_name):
    year, month, day = map(int, re.findall(r'\d+', branch_name)[:3])
    return year * 10000 + month * 100 + day


def get_todays_time_stamp():
    now = datetime.datetime.now()
    return now.year * 10000 + now.month * 100 + now.day


def integrate(branches):
    tag = "integration_%s" % int(time.mktime(time.localtime()))

    cmd = "git checkout -b %s origin/master" % tag
    print cmd
    subprocess.call(cmd, shell=True)
    dev_null = open("/dev/null", "wb")

    for branch in branches:
        cmd = "git merge --no-ff --quiet --no-edit %s" % branch
        ret = subprocess.call(cmd, stdout=dev_null, shell=True)
        print "Ret => %s" % ret
        if ret != 0:
            abort_merge()
            print("ok, that's enough.")
            sys.exit()


def main():
    try:
        pattern = sys.argv[1]
    except IndexError:
        pattern = DEFAULT_BRANCH_PATTERN
    else:
        pattern = re.compile(pattern)

    all_branches = get_remote_branches(pattern=pattern)
    merged_branches = get_remote_branches(pattern=pattern, merged_only=True)
    unmerged_branches = list(set(all_branches) - set(merged_branches))
    unmerged_legit_branches = filter(
        lambda x: re.match(DEFAULT_BRANCH_PATTERN, x),
        unmerged_branches)

    print "Release branches to integrate:"
    todays_time_stamp = get_todays_time_stamp()
    branches_to_integrate = [b for b in unmerged_legit_branches
                             if get_time_stamp(b) >= todays_time_stamp]

    integrate(branches_to_integrate)


if __name__ == '__main__':
    main()
