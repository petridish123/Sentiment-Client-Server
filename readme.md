# Summary

This is the prototype of a research tool used at BYU in dr. Crandall's lab.

This tool, when completed, will be implemented into another project called "GridHunt"

GridHunt (GH) is a fast pace real-time stag hare problem representation where
individuals will work together to either hunt the larger prey and all benefit
or hunt the smaller prey and scare off the bigger prey.

This tool will be implemented into GH to also model the social aspect of the stag hare problem,
using "sentiments."

Sentiments are how a player feels about another player.
A sentiment comes from {-2,-1,0,1,2} which is represented as words from 
{very negative, negative, neutral, positive, very positive}.

The hope is that as a player collaborates with another player, they will increase their sentiment
modeling relationships in this problem simulation.

After we model relationships in the problem, we hope to see if there is a trend
between the relationships and the success of an individual.

The end research goal is to find a relationship between relationships and success/
Social and economic success. This, we believe, will model real life
so that we can find how people in poverty stay there and how they can 
get out of poverty in the United States.

# Applications

The reason this tool is being developed is to assist in the development of ai agents in the game GridHunt as described above.

We believe that there are 2 spaces that humans think in when playing the GridHunt game: Physical and Reputations.

These spaces can be described in many ways such as monetarily, and mentally repectively. After playing GridHunt nemerous times, we
have found that people tend to act in their best interst to gain more money, but with respect to the reputations of others as percieved by themselves.

When designing bots, it is important that they not only observe the potential monetary benefits of an action, but also the reputation that they may gain.

An objective of this study is to see if bots who think in the reputation space (using reputations and beliefs about other players) will be able to 
maximize their reputation and monetary profit in the GridHunt game and also potentially find strategies to play this collaborative game.

# How to setup

1) Set up a venv
    ```
    python -m venv venv
    ```
2) Install the libraries listed below:
    - numpy
    - qasync
    - websockets
    - PyQt6
3) Install the shared files as a library
    ```
    python -m pip install ./Shared  (if Shared is in the directory with your venv)
    ```
4) Activate your venv by running
    ```
    ./venv/Scripts/activate
    ```

This concludes the setup and required libraries to run the program on your machine.

# How to use
## Setup server and client
1) Run the server
    ```
    python ./QTServer.py
    ```

2) Run the number of clients specified in the QTServer (typically 3) by running this command in X terminals
    ```
    python ./qtwebsocket
    ```

This concludes the setup of the program, the following steps are instruction on how to interact with the program

## Use client

1) This is currently changing but will be updated when the project finalizes.

## Use server