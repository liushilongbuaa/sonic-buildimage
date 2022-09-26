# Github actions README

This is an introduction about auto-cherry-pick workflow.


The workflow only works for release branches, such as 202???,201811,201911. Let's take 202205 branch as an example:
1. pr_cherrypick_prestep:
```mermaid
graph LR
A(PR with tag:<br> Approved for 202205 Branch)
B(Merged PR)
A -- author merge PR --> C[trigger pr_cherrypick_prestep]
B -- Release owner add tag:<br> Approved for 202205 Branch --> C
C --no conflict<br> create cherry pick PR --> D(New PR)
C -- if conflict<br>Add tag: Cherry Pick Confclit_202205 --> F(Old PR)
D -- Add tag: automerge<br>Add link to Old PR in comment --> D
```
2. automerge:  automerge will merge PRs when its author is mssonicbld and its PR checks passed.
```mermaid
graph LR
A(PR) -- azp checks succeeded<br>author is mssonicbld --> B(trigger automerge)
B --> C[Merge PR]
```
3. pr_cherrypick_poststep:
```mermaid
graph LR
A(prestep created PR) -- completed --> B[trigger pr_cherrypick_poststep]
B -- edit Origin PR --> C[Remove tag: Created PR to 202205 Branch<br>Add tag: Included in 202205 Branch]
```
