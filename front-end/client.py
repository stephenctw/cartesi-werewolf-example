from network import Network
import time

def main():
    n = Network()
    role = n.get_role()
    print("\nYour role is *** ", role, " ***\n")

    while( n.is_finished() == False and n.is_alive() == True):
        # get the current round and is_day
        round = n.get_round()
        is_day = n.is_day()

        if role == 'WEREWOLF':
            # 
        elif role == 'VILLAGER':
            #
        elif role == 'MODERATOR':


        # wait till day/night switch
        while(is_day == n.is_day()):
            time.sleep(1)
