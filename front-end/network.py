import socket
from structure import *
import sys

class Network:
    server_ip = ""
    server_port = 5555

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((Network.server_ip, Network.server_port))

    def join_game(self, id, pk):
        self.server.send("Join. ID: ",id, "PK: ", pk)

    # send message
    def send(self, id, message):
        # send by socket

    def send_on_chain(self, message):

    def broadcast_all(self, message):

    # get data routine

    def get_data(self):
        data = self.client.recv(1024).decode()
        if not data:
            print('\nDisconnected from server\n')
            sys.exit()
        return data
    
    def get_raw_data(self):
        raw_data = self.client.recv(1024)
        if not raw_data:
            print('\nDisconnected from server\n')
            sys.exit()
        return raw_data
    
    def get_on_chain(self):

    def get_players(self): # Game._players
        return self.get_data()
    
    # get data from Player struct
    
    def is_alve(self) -> bool:
        self.server.send("Player\n")
        return Role(self.get_data()).is_alive
    
    # get data from GameState struct

    def is_finished(self) -> bool:
        self.server.send("GameState\n")
        return GameState(self.get_data()).is_finished
    
    def is_day(self) -> bool:
        self.server.send("GameState\n")
        return GameState(self.get_data()).is_day
    
    def get_round(self) -> int:
        self.server.send("GameState\n")
        return GameState(self.get_data()).round
    
    def should_revote(self)

    def get_mod_pk(self) 


