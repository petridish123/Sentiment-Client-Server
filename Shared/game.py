
"""
Player:

name
points
scores
cur round

"""
import numpy as np

class player:
    def __init__(self,label,name, points = 0):
        self.points = points
        self.label = label
        self.name = name
        self.scores = {0:{}}
        self.cur_round = 0

    def update_points(self,points):
        self.points = points
        if self.label:
            self.label.text = str(points)



    
    def get_average_from_round(self, round: int):
        if round in self.scores:
            new_scores = list(self.scores[round].values())
            total = 0
            n = 0 
            for score in new_scores:
                n+=1
                total += score
            average = total / n
            return average
        else:
            print("There is no such round logged")
            return 0


"""
Game is the rules that is going to be on the server side

Game holds the collection of players and modifies them correctly
This is the data object


"""

class game:

    def __init__(self,):
        self.id_players = {}
        self.players_id = {}
        self.num_players = 0

        self.scores = {}
        self.round = 1
    
    def add_player(self, player_name : str|None = None, PLAYER : player|None = None) -> int:
        if not player_name:
            player_name = self.make_ID()
        if not PLAYER:
            PLAYER = player(None, player_name)
        self.id_players[player_name]  = PLAYER
        self.players_id[PLAYER] = player_name
        self.num_players += 1

        return player_name

    def make_ID(self,) -> int:
        if self.num_players in self.id_players or self.num_players == 0:
            new_id = self.num_players
            while new_id in self.id_players or new_id == 0:
                new_id += 1
            return new_id
        else: return self.num_players

    def start_game(self) -> int:
        
        return self.num_players
    
    def remove_player(self, player_name = None, player:player |None = None):
        if player_name and player_name in self.id_players:
            temp_player = self.id_players[player_name]
            self.id_players.pop(player_name)
            self.players_id.pop(temp_player)
            self.num_players -= 1


    def new_round(self):
        self.round += 1
        self.scores[self.round] = {}
    
    def set_score(self, player_ID_from, scores,camp = None):
        if not self.round in self.scores:
            self.scores[self.round] = {}
        self.scores[self.round][player_ID_from] = {}
        for ID in scores:
            self.scores[self.round][player_ID_from][ID] = scores[ID]
        self.scores[self.round][player_ID_from]["CAMP"] = camp # Setting the camp
        if len(self.scores[self.round]) >= self.num_players:
            print("all allocation collected")
            return True
        print(f"{len(self.scores[self.round])} / {self.num_players} collected")
        return False
    
    def save(self):
        """
        This function will check to see if the path exists, then iterate until a new file can be written.
        
        """
        import json
        import os
        i = 0
        path = f"Save_data/Save_{i}.json"
        while os.path.exists(path):
            i += 1
            path = f"Save_data/Save_{i}.json"
         
        with open(path, "w") as f:
            f.writelines(json.dumps(self.scores))

    





from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QLineEdit, QVBoxLayout, QGridLayout
)

class sub_player:

    def __init__(self, ID, layout : QGridLayout|QVBoxLayout, row : int) -> None:
        self.current_allocation : int = 0 
        self.scores : dict = {0:0} # for each round, append a score
        self.layout : QGridLayout|QVBoxLayout= layout
        self.cur_row : int= row
        self.ID = ID
        self.cur_round : int = 0
        self.widgets  = []

    def add_player(self) -> None:
        
        self.name = QLabel("Player: " + str(self.ID))
        self.layout.addWidget(self.name, self.cur_row, 0)
        self.widgets.append(self.name)

        self.new_label = QLabel("Sentiment: Neutral")
        self.layout.addWidget(self.new_label, self.cur_row, 6)
        self.widgets.append(self.new_label)


        button = QPushButton("Very Negative")
        button.setFixedWidth(100)
        button.clicked.connect(self.set_score( -2))
        self.layout.addWidget(button,self.cur_row,1)
        self.widgets.append(button)

        button = QPushButton("Negative")
        button.setFixedWidth(100)
        button.clicked.connect(self.set_score(-1))
        self.layout.addWidget(button,self.cur_row,2)
        self.widgets.append(button)

        button = QPushButton("Neutral")
        button.setFixedWidth(100)
        button.clicked.connect(self.set_score(0))
        self.layout.addWidget(button,self.cur_row,3)
        self.widgets.append(button)

        button = QPushButton("Positive")
        button.setFixedWidth(100)
        button.clicked.connect(self.set_score(1))
        self.layout.addWidget(button,self.cur_row,4)
        self.widgets.append(button)

        button = QPushButton("Very Positive")
        button.setFixedWidth(100)
        button.clicked.connect(self.set_score(2))
        self.layout.addWidget(button,self.cur_row,5)
        self.widgets.append(button)
    
    def change_row(self, new_row):
        self.cur_row  = new_row
        for widget in self.widgets:
            column = self.get_widget_column(widget)
            self.layout.removeWidget(widget)
            self.layout.addWidget(widget,self.cur_row, column)
    
    def off_yerself(self):
        for widget in self.widgets:
            self.layout.removeWidget(widget)
            widget.hide()
            widget.deleteLater()

    def get_widget_column(self, widget):
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget() == widget:
                row, column, row_span, col_span = self.layout.getItemPosition(i)
                return column
        return None

    def set_score(self, amount : int):
        def _():
            self.current_allocation = amount
            self.scores[self.cur_round] = amount
            self.new_label.setText({-2:"Very Negative", -1:"Negative", 0:"Neutral", 1: "Positive", 2:"Very Positive"}[amount])
        return _
    
    def set_round(self, round_num) -> None:
        self.cur_round = round_num
    
    def increment_round(self) -> None:
        self.set_round(self.cur_round + 1)
    
    def get_score(self) -> tuple:
        return self.ID, self.current_allocation
    
    def change_name(self, name) -> None:
        self.name.setText(name)
    

class player_matrix:
    """
    The purpose of this class is to hold all methods and variables
    for each player's ideas about how other players think about eachother
    """


    def __init__(self, ID, ID_players):
        self.ID_players = ID_players
        self.ID = ID
        self.matrix = self.create_blank_matrix(ID_players)
        self.reputations : dict = {0:self.create_blank_reputation(ID_players)} # This is the starting reputations at time 0

    
    def create_blank_matrix(self, ID_players):
        new_matrix = np.matrix(np.array([np.zeros(shape= (len(ID_players))) for i in range(len(ID_players))]))
        return new_matrix
    
    def create_blank_reputation(self, ID_players):
        new_dict = {id:1 for id in ID_players } # gets the id and maps it to a value, much easier to manage than a list
        return new_dict

    def get_reputation(self,t,j):
        # Gets the reputation at time t of player j
        assert t in self.reputations, "This time has not been created yet"
        assert j in self.reputations[t], "This reputation does not exist yet"
        return self.reputations[t][j]
    
    def create_new_t_reputation(self,t): # Creates a new slot for reputation scores to go into.
        self.reputations[t] = self.create_blank_reputation(self.ID_players)

    def add_value(self, ID_from, ID_to, value):
        """
        This takes the value and adds it to player k's belief about the from and to player's interactions
        Returns the new value
        """

        self.matrix[ID_from][ID_to] += value
        return self.matrix[ID_from][ID_to]

    def get_belief(self, ID_from : int|None = None, ID_to : int|None = None):
        if ID_from == None:
            return self.matrix
        if ID_to == None:
            return self.matrix[ID_from]
        return self.matrix[ID_from][ID_to]
        # Will get the belief(s) of a specific player to another, or the entire thing if not specified
    def save_copy(self):
        return self.matrix.copy()
    
    def __str__(self):
        return str(self.matrix)
   