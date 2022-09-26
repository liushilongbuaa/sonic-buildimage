# Github actions README

This is an introduction about auto-cherry-pick workflow.


take 202205 branch for example:
1. pr_cherrypick_prestep:
```mermaid
sequenceDiagram
 participant  Origin PR
 participant  github action
 participant  New PR
 Note  right of  Origin PR: with tag:<br> Approved for 202205 Branch
 Note  right of  Origin PR: merge PR
 Origin PR->>github action: trigger pr_cherrypick_prestep
 Note  right of github action: if no conflict
 github action->>New PR: mssonicbld create PR
 Note  right of New PR: Add tag: automerge<br>Add link to Origin PR in comment
 github action->> Origin PR: Add tag: Created PR to 202205 Branch <br> Add comment: @author code conflict
```
2. automerge:  automerge will merge PRs when its author is mssonicbld and its PR checks passed.
3. pr_cherrypick_poststep:
```mermaid
sequenceDiagram
 participant  Origin PR
 participant  github action
 participant  New PR
 Note  right of  New PR: with tag:<br> automerge
 Note  right of  New PR: author is mssonicbld
 New PR->>github action: trigger pr_cherrypick_poststep
 github action->>Origin PR: Remove tag: Created PR to 202205 Branch<br>Add tag: Included in 202205 Branch
```
