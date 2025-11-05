from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGridLayout
)
import sys



import json
import websockets
from qasync import QEventLoop, asyncSlot
import asyncio



from Shared.game import player, sub_player

url = "127.0.0.1"
PORT = 8765


class QtWebsocket(QWidget):

    def __init__(self,):
        super().__init__()
        self.game_running = False

        self.ID = None

        self.setWindowTitle("Client")

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.resize(200,150)
        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.send_allocation) # connect to a function
        self.layout.addWidget(self.button,0,1)
        
        self.camp_button = QPushButton("Select Camp")
        self.camp_button.clicked.connect(self.create_camp_menu) # Connect this to opening a camp window 
        self.layout.addWidget(self.camp_button, 0, 2)


        self.round_num = 0
        self.round_num_label = QLabel("Round: " + str(self.round_num))
        self.layout.addWidget(self.round_num_label, 0 , 0)


        self.row = 1
        self.player : player|None = None

        self.players = {} #ID : row

        self.round_allocations = {}
        self.cur_round = 0

        self.socket = None

        self.window = None

        self.camp :int | None = None

        self.camps : list|None = []

        self.run()

    def change_round_num(self, new_int: int):
        self.round_num = new_int
        self.round_num_label.setText("Round: " + str(self.round_num))

    @asyncSlot()    
    async def send_message(self, message = "Hello!"):
        new_message = {
            "MESSAGE":message
        }
        new_message = json.dumps(new_message).encode()
        await self.socket.send(new_message)

    @asyncSlot()
    async def send_allocation(self):
        if not self.player or not self.game_running: 
            print("Game not running or Player not created")
            return
        self.round_allocations = {int(ID):self.players[ID].current_allocation for ID in list(self.players.keys())}
        new_message = {
            "ALLOCATION" : self.round_allocations,
            "ID" : self.player.name,
            "CAMP" : self.camp,
        }
        print("sending allocations: ", new_message)
        new_message = json.dumps(new_message).encode()
        await self.socket.send(new_message)

    def make_player(self, ID):
        self.player = player(None, ID, 0)
        self.ID = ID

    async def handle_message(self,message):
        message = json.loads(message.decode())
        # print(message)
        if "ID" in message:
            self.make_player(message["ID"])

        if "STARTGAME" in message:
            self.game_running = True
            # self.player_ids = message["STARTGAME"]
            for i in range(len(message["STARTGAME"])):
                player_id = message["STARTGAME"][i]
                if not self.ID:
                    break
                elif player_id == self.ID:
                    continue
                new_player = sub_player(player_id,self.layout,self.row)
                self.row += 1
                new_player.add_player()
                self.players[player_id] = new_player
            self.setWindowTitle(f"Player : {self.ID}")
            # pass # Create multiple players here
        if "MINUSPLAYER" in message:
            old_player = self.remove_player(message["MINUSPLAYER"])
            old_player.off_yerself()
            move_row  = old_player.cur_row
            for player in self.players:
                pl = self.players[player]
                if pl.cur_row > move_row:
                    print("MOVING")
                    # pl.change_row(pl.cur_row-1)
                else:
                    print(f"Oldrow : {move_row} and {pl.cur_row}")
            sys.exit()
        if "ROUND" in message:
            self.change_round_num(message["ROUND"])
        if "CAMPS" in message:
            self.camps = [i for i in range(1, 1 + int(message["CAMPS"]))]
        if "NAMES" in message:
            for i in message["NAMES"]:#self.players:
                if int(i) == self.ID:
                    self.setWindowTitle(message["NAMES"][i])
                self.players[int(i)].change_name(message["NAMES"][i])


                    
    
    def remove_player(self, ID):
        old_player = self.players[ID]
        self.players.pop(ID)
        return old_player

    @asyncSlot()
    async def run(self):
        while not self.socket: # Keep trying to connect
            try:
                self.socket = await websockets.connect("ws://localhost:8765")
            except Exception as e:
                pass
                
        await self.socket.send(json.dumps({"REQUEST" : "CONNECT"}).encode())

        while True:
            try:
                message = await self.socket.recv()
                await self.handle_message(message)
            except KeyboardInterrupt:
                print("AWW")
                sys.exit()
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected")
                sys.exit()

    def clear_window(self):
        self.window = None
    
    def set_camp(self, camp):
        self.camp = camp
    
    def create_camp_menu(self):
        if self.window is not None:
            self.window.close()
        self.window = campWindow(self.camps, mainwindow=self)
        self.window.show()

    def closeEvent(self, a0):
        print("Closing and cleaning up")
        if self.window and hasattr(self.window, "close"):
            self.window.close()
        a0.accept()




class campWindow(QWidget):
    """
    Based off the event window in the QTServer file, so if there are errors, they probably stem from that
    I will be changing this so that it opens a window that has several camps on it and a list of the people in that camp
    And it will return a simple number for the camp which the QTWebsocket class will add to their allocations to send back
    """
    def __init__(self, camps : dict|list ,players : dict|None = None, mainwindow : QtWebsocket|None = None):
        
        super().__init__()

        self.layout : QGridLayout = QGridLayout()
        self.setLayout(self.layout)

        self.mainwindow = mainwindow

        self.camp = 0

        """
        This window is going to look something like this:
        |------------------------------|-|[]|X|
        |              Camps                  |
        | |Camp 1| |Camp 2| |Camp 3| ....     |
        | Player1  Player4                    |
        | Player2                             |
        |                                     |
        | |Submit|                            |
        |-------------------------------------|

        where the |Camp X| is a button
        "Camps" is a label
        And for now the players will not show up
        """
        self.cur_col = 0
        self.cur_row = 0

        for camp in camps: # This iterates over the camps and gets the name of the camp
            if type(camp) == type(dict):
                pass # create the player labels
            name = f"camp {camp}"
            button = QPushButton(name)
            button.clicked.connect(self.set_camp(camp)) # This creates a helper function that sets the window's camp to whatever was selected
            self.layout.addWidget(button, self.cur_row, self.cur_col)
            self.cur_col += 1
        self.cur_row += 1
    
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.close)
        self.layout.addWidget(self.submit_button,self.cur_row+1,0)

    def set_camp(self, ID : int) -> callable:
        
        def _():
            self.camp = ID
        
        return _



    def close(self):
        # Send the camp to the client

        self.mainwindow.set_camp(self.camp)
        self.mainwindow.clear_window()
        super().close()
        self.deleteLater()



def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # set_style(app, "C:/Users/Mango/Desktop/Python_server_client/Python-server/rules/style.css")
    window = QtWebsocket()
    window.show()
    # sys.exit(app.exec())
    with loop:
        loop.run_forever()

def set_style(app : QApplication, sheet : str):
    with open(sheet, "r") as f:
        if not f:
            return False
        lines = f.read()
        # print(lines) 
        
        app.setStyleSheet(lines)

if __name__ == "__main__":
    main()

