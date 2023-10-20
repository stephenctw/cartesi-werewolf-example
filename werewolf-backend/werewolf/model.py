# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import itertools
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import random
from datetime import datetime
from enum import Enum

Role = Enum("Role", ["MODERATOR", "WEREWOLF", "VILLAGER", "UNKNOWN"])
# 1 werewolf, 4 villagers, 1 moderater
NUMBER_OF_PLAYER = 6


class Player:
    """
    Werewolf player

    Encapsulates player status
    """

    def __init__(self, id: str, pub_key: str):
        self._id = id
        self._pub_key = pub_key

        self.role = Role.UNKNOWN
        self.alive = True
        self.can_be_voted = True
        self.has_voted = False
        self.has_moved = False
        self.votes_got = 0

    @property
    def alive(self):
        return self._alive

    @property
    def can_be_voted(self):
        return self._can_be_voted

    @property
    def has_moved(self):
        return self._has_moved

    @property
    def has_voted(self):
        return self._has_voted

    @property
    def votes_got(self):
        return self._votes_got

    @property
    def id(self):
        return self._id

    @property
    def role(self):
        return self._role

    @alive.setter
    def alive(self, alive: bool):
        self._alive = alive

    @can_be_voted.setter
    def can_be_voted(self, can_be_voted: bool):
        self._can_be_voted = can_be_voted

    @has_moved.setter
    def has_moved(self, has_moved: bool):
        self._has_moved = has_moved

    @has_voted.setter
    def has_voted(self, has_voted: bool):
        self._has_voted = has_voted

    @votes_got.setter
    def votes_got(self, votes_got: int):
        self._votes_got = votes_got

    @role.setter
    def role(self, role: Role):
        self._role = role

    def move(self):
        if self.role == Role.MODERATOR:
            raise ValueError("moderator cannot move")

        if self._has_moved:
            raise ValueError("player has already moved")

        self._has_moved = True

    def vote(self, candidate):
        if self.role == Role.MODERATOR:
            raise ValueError("moderator cannot vote")

        if self._has_voted:
            raise ValueError("voter has already voted")

        if not candidate._can_be_voted:
            raise ValueError("candidate cannot be voted")

        self._has_voted = True
        candidate._votes_got += 1

        return candidate._votes_got

    def reset_vote(self):
        self._has_voted = False
        self._votes_got = 0

    def print(self):
        print(f"""player {self.id} plays {self.role}, alive: {self.alive}, has_moved: {self.has_moved},
              has_voted: {self.has_voted}, got_votes: {self.votes_got}, can_be_voted: {self.can_be_voted}""")


class Game:
    """
    Werewolf game state

    The game can last for several rounds to finish. For each round, the werewolf kills one villager during the night,
    the moderator will anounce the victim the next day.
    The remaining villagers try to vote out the suspicious werewolf, who will be killed based on the vote.
    When there's a tie, revote is required.
    The game ends when all players from one party are all killed.
    """

    def __init__(self):
        self.__reset()

    def __reset(self):
        self._started = False
        self._is_daytime = True
        self._rounds = 0
        self._players = {}
        self._move_history = []
        self._moves = 0
        self._votes = 0
        self._alives = {}
        self._inputs = []

    def __try_get_player(self, id: str):
        return self._players.get(id)

    def __get_player(self, id: str):
        player = self._players.get(id)

        if player is None:
            raise ValueError("player is not found")

        return player

    def __advance(self):
        self._rounds += 1

    def __toggle_day(self):
        self._is_daytime = not self._is_daytime
        self._moves = 0
        for v in self._alives:
            player = self.__get_player(v)
            player.has_moved = False

        if self._is_daytime:
            self.__advance()

    def __kill(self, victim_id: str):
        victim = self.__get_player(victim_id)

        if not victim.alive:
            raise ValueError("victim already died")

        victim.alive = False
        self._alives.remove(victim_id)

        self.__toggle_day()

    def new_player(self, id: str, pub_key: str):
        if self._started:
            raise ValueError("game has started, please join the next one")

        if self.__try_get_player(id) is not None:
            raise ValueError("player already joined")

        self._players[id] = Player(id, pub_key)

        if len(self._players) == NUMBER_OF_PLAYER:
            # TODO: select one player to be the moderator
            # moderator should assign roles to other player
            moderator = random.choice(list(self._players.keys()))
            # print(f"moderator: {moderator}")

            self._players["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"].role = Role.MODERATOR
            self._players["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"].can_be_voted = False

    def handle_vote(self, voter_id: str, candidate_id: str):
        if not self._is_daytime:
            raise ValueError("cannot vote in nights")

        voter = self.__get_player(voter_id)

        if not voter.alive:
            raise ValueError("voter already died")

        candidate = self.__get_player(candidate_id)

        if not candidate.alive:
            raise ValueError("candidate already died")

        voter.vote(candidate)
        self._votes += 1

        if self._votes == len(self._alives):
            # sort the votes of alives in decending order
            alives = list(
                filter(lambda p: p.alive, self._players.values()))
            alives.sort(
                key=lambda p: p.votes_got, reverse=True)
            highest = alives[0].votes_got
            highest_candidate = alives[0].id

            highest_ties = list(
                filter(lambda p: p.votes_got == highest, alives))
            if len(highest_ties) > 1:
                print("revote!")
                self._votes = 0
                # more than one highest vote, requires revote
                for v in alives:
                    self._players[v._id].can_be_voted = False
                    self._players[v._id].votes_got = 0
                    self._players[v._id].has_voted = False

                for tie in highest_ties:
                    self._players[tie._id].can_be_voted = True
            else:
                for v in alives:
                    self._players[v._id].can_be_voted = True
                    self._players[v._id].votes_got = 0
                    self._players[v._id].has_voted = False
                self.__kill(highest_candidate)

    def handle_kill(self, victim_id: str):
        if self._is_daytime:
            raise ValueError("cannot kill in daytime")

        if self._moves != len(self._alives):
            raise ValueError("everyone has to make a move")

        self.__kill(victim_id)

    def finish(self, moderator_key: str):
        # TODO: replay the game with moderator key revealed
        self.__reset()
        return True

    def handle(self, data):
        if not self._started:
            if len(self._players) == NUMBER_OF_PLAYER:
                self.handle_player_role(data)
            else:
                self.handle_new_player(data)
        else:
            self._inputs.append(data)
            if self._is_daytime:
                self.handle_day(data)
            else:
                self.handle_night(data)

    def handle_move(self, player_id: str, encrypted_move: str):
        if self._is_daytime:
            raise ValueError("cannot move in daytime")

        player = self.__get_player(player_id)

        if not player.alive:
            raise ValueError("player already died")

        player.move()
        self._moves += 1
        self._move_history.append(encrypted_move)

    def dispatch_roles(self, encrypted_roles):
        # TODO: store somewhere for later validation
        self._alives = set(list(encrypted_roles.keys()))
        self._started = True
        self.__toggle_day()
        return True

    def handle_player_role(self, data):
        # TODO: require moderator being sender
        roles = data
        alives = []
        for role in roles:
            player = self.__get_player(role[0])
            player.role = role[1]
            alives.append(role[0])

        self._alives = set(alives)

        self._started = True
        self.__toggle_day()

    def handle_new_player(self, data):
        return True

    def handle_day(self, data):
        return True

    def handle_night(self, data):
        # if sender is moderater
        self.handle_kill("?")
        # if not, record player move (encrypted)
        # TODO: record player moves
        return True

    def print(self):
        print("==================================================================")
        print(
            f"game round: {self._rounds}, daytime: {self._is_daytime}, game started: {self._started}")
        for i, m in enumerate(self._move_history):
            print(f"{i}th move history: {m}")
        for p in self._players.values():
            p.print()

## testing below ##


keys = []

for i in range(0, NUMBER_OF_PLAYER):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    keys.append((private_key, public_key))

g = Game()

g.print()

player_ids = ["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",  # default moderator
              "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
              "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
              "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
              "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
              "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc"]

for i in range(0, NUMBER_OF_PLAYER):
    g.new_player(player_ids[i], keys[i][1])

g.print()

salt = [b"99", b"100", b"101", b"102", b"103", b"104"]
bytes_roles = [b"MODERATOR", b"WEREWOLF", b"VILLAGER",
               b"VILLAGER", b"VILLAGER", b"VILLAGER"]
encrypted_roles = {}

# skip moderator itself
for i in range(1, NUMBER_OF_PLAYER):
    # the roles are dispatched with a salt adding to the end
    encrypted_roles[player_ids[i]] = keys[i][1].encrypt(bytes_roles[i] + salt[i], padding.OAEP(
        mgf=padding.MGF1(
            algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))

g.dispatch_roles(encrypted_roles)

# the frontend player should decrypt its role
for i in range(1, NUMBER_OF_PLAYER):
    # truncate out the salt after decode
    if bytes_roles[i] != keys[i][0].decrypt(encrypted_roles[player_ids[i]], padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))[:8]:
        raise ValueError("decrypted role doesn't match")

g.print()

# every alive send his move
g.handle_move(player_ids[1], keys[1][1].encrypt(b"KILL 0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc" + salt[1], padding.OAEP(
    mgf=padding.MGF1(
        algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
)))

for i in range(2, 6):
    g.handle_move(player_ids[i], keys[i][1].encrypt(b"NOTHING" + salt[i], padding.OAEP(
        mgf=padding.MGF1(
            algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )))

g.handle_kill(player_ids[5])

g.print()

g.handle_vote(player_ids[1],
              player_ids[1])
g.handle_vote(player_ids[2],
              player_ids[1])
g.handle_vote(player_ids[3],
              player_ids[3])
g.handle_vote(player_ids[4],
              player_ids[3])
g.print()

# revote
g.handle_vote(player_ids[1],
              player_ids[1])
g.handle_vote(player_ids[2],
              player_ids[1])
g.handle_vote(player_ids[3],
              player_ids[1])
g.handle_vote(player_ids[4],
              player_ids[3])
g.print()

# finish game and try to replay

# when only one player left

# g.handle_kill("E")
# g.print()
