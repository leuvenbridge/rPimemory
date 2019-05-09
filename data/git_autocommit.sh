#!/bin/bash

# This bash script pulls git repo, commit changes and push the repo back

# cd to git local repo
cd ~/Documents/git/rPimemory

# pull repo
git pull ssh://git@github.com/foragingBRAIN/rPimemory.git

# add all changes
git add -A

# get date
now=$(date +%Y_%m_%d-%H_%M_%S)

# commit changes with date as message
git commit -m "rPi $now"

# push commit
git push ssh://git@github.com/foragingBRAIN/rPimemory.git

