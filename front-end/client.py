from network import Network
import time
import rsa
import random

NUMBER_OF_PLAYER = 6

def main():
    n = Network()

    id = ''

    public_key, private_key = rsa.newkeys(2048)
    n.join_game(id, public_key)

    # get players id
    # assume the first player is moderator

    players = n.get_players()
    moderator = players[0]
    
    if id == moderator.id : 
        # if self is moderator
        # randomly choose a werewolf and send out all roles
        role = "MODERATOR"
        werewolf = random.randrange(1,6)
        for i in range(1, NUMBER_OF_PLAYER):
            if players[i].id == werewolf:
                n.send(players[i].id, rsa.encrypt("WEREWOLF".encode(), 
                            players[i].public_key))
            else:
                n.send(players[i].id, rsa.encrypt("VILLAGER".encode(), 
                            players[i].public_key))
    else:
        # wait for role
        role = rsa.decrypt(n.get_raw_data(), private_key).decode()

    print("\nYour role is *** ", role, " ***\n")

    # game begins

    while( n.is_finished() == False and n.is_alive() == True):
        # get the current round and is_day
        round = n.get_round()
        is_day = n.is_day()

        if is_day == False:
            print("night falls...\n")
            if role == 'WEREWOLF':
                victim = input('Who would you kill?\n')
                action = "round " + round + " kill " + victim
                n.send_on_chain(rsa.encrypt(action.encode(), 
                            moderator.public_key))
            elif role == 'VILLAGER':
                n.send_on_chain(rsa.encrypt("random message".encode(), 
                            moderator.public_key))
            elif role == 'MODERATOR':
                action = rsa.decrypt(n.get_raw_data(), private_key).decode()
                n.broadcast_all(action)
        else:
            print("day breaks...\n")
            # discuss who is werewolf and vote
            if role != 'MODERATOR':
                vote_for = input('Who you think is werewolf?\n')
                n.send_on_chain("round " + round + " vote for " + vote_for)
                vote_candidates = n.should_revote()
                while vote_candidates:
                    vote_for = input('Out of ' + vote_candidates + ' who you think is werewolf?\n')
                    n.send_on_chain("round " + round + " re-vote for " + vote_for)
                    vote_candidates = n.should_revote()

        # wait till day/night toggles
        while(is_day == n.is_day() and round == n.get_round()):
            time.sleep(1)

    print("game ended.\n")
    n.send_on_chain(private_key)
