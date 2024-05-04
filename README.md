# Monte-Carlo Tree Search in Python for Chess
[![Visits Badge](https://badges.pufler.dev/visits/alexander-darwiche/chess-engine)](#)


### Overview
This document is meant to guide a user through how to use this repository to play a chess game
against a Monte-Carlo Tree Search or Random AI Agent. First, you will need to make sure you've got
Poetry Package Manager installed. To do this, navigate to: https://python-poetry.org/docs/

<br>

# Getting started
**(PVP)** <br>
Step 1: First step is to navigate to the folder containing the repository through the command prompt.

```
> cd chess-engine
```
Step 2: Next, you want to download the required libraries to ensure the program is working appropriately.
To do this, type the following:

```
> Poetry update
> Poetry shell
```

Step 3: Now you are within the virtual environment needed to run the code. Next, you can select to play either of the chess bots by typing:


```
> Poetry run python main.py
```

or 

```
> Poetry run python main_mcts.py
```

Step 4: Now you can play against the AI. You will be White pieces and the AI will be Black pieces in both implementations.

```
     Black Side

    a b c d e f g h
  +-----------------+
8 | r n b q k b n r |
7 | p p p p p p p p |
6 | - - - - - - - - |
5 | - - - - - - - - |
4 | - - - - - - - - |
3 | - - - - - - - - |
2 | P P P P P P P P |
1 | R N B Q K B N R |
  +-----------------+
    a b c d e f g h

    White Side

> What piece? (Input the notation for the location you'd like to move)
> Where to? (Input the notation for the location you'd like to move to)


```