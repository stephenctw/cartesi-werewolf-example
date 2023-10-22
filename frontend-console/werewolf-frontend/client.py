from network import Network
import time
import rsa
import random
import sys

NUMBER_OF_PLAYER = 6

player_ids = ["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
              "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
              "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
              "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
              "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
              "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc"]

def main():
    player_index = sys.argv[0]
    print("players index ", player_index)
    signer_address = player_ids[player_index]
    n = Network()

    public_key, private_key = rsa.newkeys(2048)
    # send public key to join the game
    n.send(public_key)

    # get game state and moderator
    while not moderator:
        g = n.inspect('')
        moderator = g._moderator
        time.sleep(1)
    
    if signer_address == moderator: 
        role = "MODERATOR"

        # randomly choose a werewolf and send out all roles
        other_players = list(g._players.keys()).remove(moderator)
        werewolf = random.choice(other_players)

        encrypted_roles = {}
        for i in range(0, NUMBER_OF_PLAYER):
            if player_ids[i] == moderator:
                continue
            elif player_ids[i] == werewolf:
                encrypted_roles[player_ids[i]] = rsa.encrypt("WEREWOLF".encode(), 
                            players[i].public_key)
            else:
                encrypted_roles[player_ids[i]] = rsa.encrypt("VILLAGER".encode(), 
                            players[i].public_key)
            n.send_on_chain(encrypted_roles)
    else:
        # wait for role
        while not role:
            g = n.inspect('')
            encrypted_role = g._players[signer_address].encrypted_role
            role = rsa.decrypt(encrypted_role, private_key).decode()

    print("\nYour role is *** ", role, " ***\n")

    # game begins

    g = n.inspect('')
    while signer_address in g._alives :
        # get the current round and _is_daytime
        round = g._rounds
        _is_daytime = g._is_daytime

        if _is_daytime == False:
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
                vimtim = action.rsplit(' ', 1)[-1]
                n.send_on_chain(vimtim)
        else:
            print("day breaks...\n")
            # discuss who is werewolf and vote
            if role != 'MODERATOR':
                vote_for = input('Who you think is werewolf?\n')
                n.send_on_chain(vote_for)
                # revote if tie?

        # wait till day/night toggles
        while(_is_daytime == g._is_daytime()):
            time.sleep(1)
            g = n.inspect('')

        # check if game has finished
        if role == 'MODERATOR':
            g = n.inspect('')
            alives = len(g._alives)
            werewolf_alive = (werewolf in g._alives)
            if alives > 2 and not werewolf_alive:
                n.send_on_chain("finish")
            elif alives == 2 and werewolf_alive:
                n.send_on_chain("finish")

    print("game ended.\n")
    n.send_on_chain(private_key)
