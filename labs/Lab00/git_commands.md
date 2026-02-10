### Git - Undo uncommitted changes
```
git status
git restore <file> (or . for the whole current directory)
```

### Unstage staged changes
If you’ve used git add but haven’t committed yet:
```
git restore --staged .
```
OR
```
git reset
```
This unstages the changes but keeps changes in your working directory.

### Fully reset to the last commit (Destructive)
To discard all changes (staged + unstaged) and reset your working tree to match the latest commit exactly:
```
git reset --hard HEAD
```

### Undo committed changes
1) Undo the last local commit but keep its changes
```
git reset --soft HEAD~1
```
This moves the HEAD one commit back but leave changes staged for a new commit

if you want them unstaged
```
git reset HEAD~1
```

2) Undo a commit and also discard its changes
if you want to **remove** a commit and its changes entirely:
```
git reset --hard HEAD~1
```
⚠️ This erases that commit and its changes (locally). Only do this if you haven’t pushed it or you don’t need it anymore.
To return to a specific commit:
```
git reset --hard <commit-hash>
```

3) Undo a commit but keep history intact
If the commit has been shared (pushed to a remote) and you want to safely undo this effect:
```
git revert <commit-hash> 
```





### Take the whole directory back to "as-it-was" at a previous commit without rewriting history
```
git revert --no-commit <commit-hash>..HEAD
git commit -m "Revert to <commit-hash> state"
```
This reverses every change from the commit after <commit-hash> 
up to HEAD by applying inverse changes, then commits them.

Your branch history stays intact and you avoid rewriting shared history.

## Detach - go back and create a new branch on a vious commit:
```
git checkout <commit-hash>
```