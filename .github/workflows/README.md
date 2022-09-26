# Github actions README

This is an introduction about auto-cherry-pick workflow.


take 202205 branch for example:
1. pr_cherrypick_prestep:
```mermaid
graph
Start(Origin PR) --> A{merged ?}
A -- NO --> A
A -- YES --> A1{Approved<br> for 202205<br> Branch ?}
A1 -- NO --> A1
A1 -- YES --> A2(pr_cherrypick_prestep)
B(pr_cherrypick_prestep)
B -->  B1{cherry pick<br>conflict ?}
B1 -- YES --> B2(Add tag:<br>Cherry Pick Confclit_202205) --> B3(Add comment:<br>refer author code conflict)
B1 -- NO --> B4(Create New PR) --> B5(New PR add tag:<br> automerge) --> B6(New PR add comment:<br>Origin PR link) --> B7(Origin PR add tag:<br>Created PR to 202205 Branch) --> B8(Origin PR add comment:<br>New PR link)
```
2. automerge:
```mermaid
graph
Start(PR azp finished successfully) --> A{author:<br>mssonicbld?}
A -- NO --> END(END)
A -- YES --> B{tag:<br>automerge?} --> C(Merge PR)
```
3. pr_cherrypick_poststep:
```mermaid
graph
A(PR is Merged) --> B{tag:<br>automerge}
B -- NO --> END(END)
B -- YES --> B1{comment:<br>link to origin PR?} -- NO --> END
B1 -- YES --> C(Origin PR remove tag:<br> Created PR to 202205 Branch) --> D(Origin PR add tag:<br> Included in 202205 Branch)
```
