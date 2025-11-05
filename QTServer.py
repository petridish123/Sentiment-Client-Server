

import Server.GameServer


from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QLineEdit, QVBoxLayout, QGridLayout
)
import sys
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QIcon
import json
import websockets
from qasync import QEventLoop, asyncSlot
import asyncio

import Shared.game
import Server.Equations
"""
Purpose of this class:
Create a server from the gameserver class and give it a qt interface
A secondary purpose is to be able to create events and log them
"""



class QTServer(QWidget):

    def __init__(self, num_players : int = 1, url : str = "localhost", port : int = 8765, loop : QEventLoop | None = None):
        super().__init__()
        self.loop = loop

        self.server = Server.GameServer.Server(num_players, url, port)
        
        self.equation = Server.Equations.equation([])

        self.event_window = None
        self.camp_window = None
        self.names_window = None
        # self.layout : QGridLayout = QGridLayout()
        self.layout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)

        self.event_button =QPushButton("Create Event")
        self.event_button.clicked.connect(self.create_event)
        self.layout.addWidget(self.event_button)

        self.camp_button = QPushButton("Define Camps")
        self.camp_button.clicked.connect(self.define_camps)
        self.layout.addWidget(self.camp_button)

        self.names_button = QPushButton("Define Names")
        self.names_button.clicked.connect(self.define_names)
        self.layout.addWidget(self.names_button)


        loop.call_soon(lambda: loop.create_task(self.running_task()))
        self.server_task = None

        self.events = {}

        self.server.update_round.connect(self.new_round)
        self.server.start_game.connect(self.start_game)

    def start_game(self, *args, **kwargs):
        ID_players = None
        if "ID_players" in kwargs:
            ID_players = kwargs["ID_players"]
        elif "ID_players" in args:
            ID_players= args["ID_players"]
        else:
            sys.exit()
            return
        ids = [id for id in ID_players]
       
        self.equation = Server.Equations.equation(ids)        

    def new_round(self, *args, **kwargs):
        print(self.events)
        print(self.server.game.scores)
        t = 1
        if "round" in kwargs:
            t = kwargs["round"]-1
        if t not in self.events:
            self.events[t] = {"TYPE":[], "To":[],"From":[], "Watcher": []}
        # Do something here with the equation
        self.equation.update_matrices(self.server.game.scores, self.events[t], t)
        self.equation.all_reputations(t)
       

    async def running_task(self):

        self.server_task = asyncio.create_task(self.run())


    def create_event(self):
        if self.event_window is not None:
            self.event_window.close()
        print("attempting to create event window")
        self.event_window = eventWindow(self.server.ID_PLAYERS, self)
        self.event_window.show()
    
    def define_camps(self):
        if self.camp_window is not None:
            print(f"Camp window exists")
            self.camp_window.close()
        self.camp_window = campWindow(self)
        self.camp_window.show()

    def define_names(self):
        if self.names_window is not None:
            print("Names window exists")
            self.names_window.close()
        self.names_window = nameWindow(self.server.ID_PLAYERS,self)
        self.names_window.show()

    def clear_windows(self):
        self.camp_window = None
        self.event_window = None
        self.names_window = None
            
                

    def handle_new_event(self,event : dict):
        """
        This takes in an event that follows the type:
        {"TYPE":"HUNT"|"STUN", ID:{"TO":True|False, "FROM":True|False, "WATCHER":True|False}}
        I have the event reformatting to:
        {"TYPE": "HUNT"|"STUN", "To":[id1,id2...idn], "From":[id1,id2...idn], "Watcher":[id1,id2...idn]}
        then I turn this into a pd dataframe in the equation
        for all IDs/players involved.

        The goal of handle event is to be able to use it in the equation by Dr. Crandall not included in this repository.
        
        """
        assert "TYPE" in event, "There is no attr TYPE, wrong event"
        
        type = event["TYPE"]
        print(event)

        if not self.server.t in self.events:
            self.events[self.server.t] = {i : [event[i]] for i in event}
        else:
            for i in self.events[self.server.t]:
                
       
                self.events[self.server.t][i].append(event[i])
        # print(self.events)
    
    def set_names(self, player_id_names : dict): # Need to open a window and map all the names to the player IDs
        self.player_id_names = player_id_names
        asyncio.create_task(self.server.send_names(self.player_id_names))
        
    
    def set_camps(self, camps):
        self.camps = camps
        asyncio.create_task(self.server.send_camps(self.camps))

    
    def closeEvent(self, a0):
        print("Closing and cleaning up")
        if hasattr(self.server, "_close"):
            asyncio.create_task(self.server._close())

        self.server.game.save() # Saves in a json file
        self.server_task.cancel()
        a0.accept()
    
    

    async def run(self):
        await self.server.main()


class eventWindow(QWidget):
    def __init__(self, players : dict, mainwindow : QTServer):
        super().__init__()

        self.layout : QGridLayout = QGridLayout()
        self.setLayout(self.layout)

        self.label_names = {0:"From", 1:"To", 2:"Watcher"}

        self.to_col = 1
        self.from_col = 0
        self.watcher_col = 2

        self.cur_row = 0

        self.data = {"TYPE":"HUNT"}

        self.mainwindow = mainwindow

        
        """
        What I want is to get all the players and their ID's
        Then make the events based on their IDS
        
        """
        for i in range(self.from_col, self.watcher_col + 1):
            label = QLabel(self.label_names[i])
            self.layout.addWidget(label, self.cur_row, i)
        self.cur_row += 1
        for ID in players:
            """Create a row for the player. Watcher, to and from"""
            self.create_row(ID)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.close)
        self.layout.addWidget(self.submit_button, self.cur_row, 0)

        self.Hunt_button = QPushButton("Hunt")
        self.Hunt_button.clicked.connect(self.set_hunt)
        self.layout.addWidget(self.Hunt_button, self.cur_row, 1)

        self.Stun_button = QPushButton("Stun")
        self.Stun_button.clicked.connect(self.set_stun)
        self.layout.addWidget(self.Stun_button, self.cur_row, 2)

    def info_button_creator(self, ID : int,to : bool = False, from_ : bool = False, watcher :bool = False):
        self.data[ID] = {"To" : False, "From": False, "Watcher": False}
        def _():
            if to:
                self.data[ID]["To"] = not self.data[ID]["To"]
            elif from_:
                self.data[ID]["From"] = not self.data[ID]["From"] 
            elif watcher:
                self.data[ID]["Watcher"] = not self.data[ID]["Watcher"]
            # print(self.data)
        return _

    def set_hunt(self): self.data["TYPE"] = "HUNT"
    def set_stun(self): self.data["TYPE"] = "STUN"


    def create_row(self, ID : int):
        for i in self.label_names:
            col = int(i)
            name = f"Player {ID}"
            button1 = QPushButton(name)
            # button1.clicked.connect(callable)
            if col == 0 :
                button1.clicked.connect(self.info_button_creator(ID,from_ = True))
            elif col == 1:
                button1.clicked.connect(self.info_button_creator(ID,to = True))
            elif col == 2:
                button1.clicked.connect(self.info_button_creator(ID,watcher= True))
                            
            self.layout.addWidget(button1, self.cur_row, col)
        self.cur_row += 1

    def format_event(self):
        event = {"TYPE" : self.data["TYPE"], "To":[], "From":[], "Watcher":[]}
        for id in self.data:
            if id != "TYPE": #The formatting is stupid right now and it isn't that good
                #The id is now a number
                for type in self.data[id]:
                    if self.data[id][type]:
                        event[type].append(id)
        self.data = event
        return self.data

    def close(self):
        # Send the event to the server
        self.format_event()
        self.mainwindow.handle_new_event(self.data)
        self.mainwindow.clear_windows()
        super().close()
        self.deleteLater()


class nameWindow(QWidget):
    # This class will allow the server to set the names of the players for easier allocation of sentiments
    def __init__(self, players :dict, mainwindow : QTServer):
        super().__init__()

        self.layout : QGridLayout = QGridLayout()
        self.setLayout(self.layout)

        # Need to make the names layout

        self.mainwindow = mainwindow

        self.cur_row = 0

        self.names = {}


        for ID in players:
            self.create_row(ID)
            self.cur_row += 1
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.close)
        self.layout.addWidget(self.submit_button, self.cur_row, 0)



    def create_row(self, ID:int) -> None :
        label = QLabel(f"player {ID} :")
        l_edit = QLineEdit()
        self.layout.addWidget(label, self.cur_row, 0)
        self.layout.addWidget(l_edit, self.cur_row, 1)

        l_edit.textChanged.connect(self.update_name(ID))
    
    def update_name(self, ID:int) -> callable:
        def _(new_text):
            self.names[ID] = new_text
        return _

    def close(self):
        # I need to make a QT window function that takes the names and sends them to the client.
        print(self.names)
        self.mainwindow.set_names(self.names)
        self.mainwindow.clear_windows()
        super().close()
        self.deleteLater()


class campWindow(QWidget):

    def __init__(self, mainwindow : QTServer):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        self.input = QLineEdit()
        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.close)
        self.layout.addWidget(QLabel("Number of camps:"))
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)

        self.mainwindow : QTServer = mainwindow

    def close(self):
        # send the information to the main server
        self.mainwindow.set_camps(self.input.text())
        self.mainwindow.clear_windows()
        super().close()
        self.deleteLater()

"""
TODO:

- Send camps to the clients so they correctly open
- make the UI cleaner and display the camp that is selected.
- Save data
- Refactor code so that it is a class that holds the windows, and the class runs the server
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop()
    asyncio.set_event_loop(loop)
    window = QTServer(3, loop = loop)
    window.show()
    with loop:
        loop.run_forever()
