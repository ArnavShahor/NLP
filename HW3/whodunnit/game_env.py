import numpy as np

from suspect_creator import SuspectCreator
from suspect import Suspect
from agents import AccuserAgent, IntelAgent, SummerizerAgent
from consts import *


class Env:
    def __init__(self, game_conf):
        self.agent_count = 3 if game_conf['include_summerizer'] else 2
        self.attribute_file = game_conf['attribute_file']
        self.conf = game_conf

        # Initialize suspects for the environment, and choose culprit.
        self.suspect_creator = SuspectCreator(self.attribute_file)
        self.suspects = self.suspect_creator.create_suspects(self.conf['suspect_count'])
        self.culprit_index = np.random.randint(self.conf['suspect_count'])
        self.culprit = self.suspects[self.culprit_index]
        self.suspect_count = len(self.suspects)
        self.possible_suspects = set(range(1, self.suspect_count + 1))

        # Create Agents
        self.accuser = AccuserAgent(AGENT_NAMES[0], self.culprit.generate_suspect_description(), self.suspect_count, allow_internal_thought=game_conf['allow_internal_thought'])
        self.intel = IntelAgent(AGENT_NAMES[1], self.suspects, allow_internal_thought=game_conf['allow_internal_thought'])
        self.agents = [self.accuser, self.intel]
        if game_conf['include_summerizer']:
            self.summerizer = SummerizerAgent(name=AGENT_NAMES[2], suspect_sount=self.suspect_count)
            self.agents.append(self.summerizer)

        self.full_game_log = f"""Suspects:
{self.intel.all_descriptions_string}
==
The culprit is: {self.culprit_index + 1}
==
Communication channel:
"""
        self.comm_channel =  ""

        self.turn_count = 0
        self.cur_player_idx = 0
        self.max_turn_count = game_conf['max_turn_count']

    def test_accusation(self, accusation_name):
        """accusation_name should be the suspect being accused (e.g. "Suspect 1")"""
        accused_index = int(accusation_name.split(" ")[1]) - 1
        return accused_index == self.culprit_index

    def handle_agent_outputs(self, outputs):
        if self.cur_player_idx == 0: # ACCUSER
            if outputs[0] == ACCUSER_ACTIONS[0]: # request-specific
                self.full_game_log += f"{self.agents[self.cur_player_idx].name} asked a specific question: {outputs[1]}\n"
                self.comm_channel += f"{self.agents[self.cur_player_idx].name} asked a specific question: {outputs[1]}\n"
            elif outputs[0] == ACCUSER_ACTIONS[1]: # request-broad
                self.full_game_log += f"{self.agents[self.cur_player_idx].name} asked a broad question about: {outputs[1]}\n"
                self.comm_channel += f"{self.agents[self.cur_player_idx].name} asked a broad question about: {outputs[1]}\n"
            elif outputs[0] == ACCUSER_ACTIONS[2]: # accuse
                success = self.test_accusation(outputs[1])
                if success:
                    self.full_game_log += f"{self.agents[self.cur_player_idx].name} accused {outputs[1]} and was correct!\n"
                    return True
                else:
                    self.full_game_log += f"{self.agents[self.cur_player_idx].name} accused {outputs[1]} and was wrong.\n"
                    self.comm_channel += f"{self.agents[self.cur_player_idx].name} accused {outputs[1]} and was wrong.\n"
        elif self.cur_player_idx == 1: # INTEL
            self.full_game_log += f"{self.agents[self.cur_player_idx].name} responded with: {outputs[1]}\n"
            self.comm_channel += f"{self.agents[self.cur_player_idx].name} responded with: {outputs[1]}\n"
        elif self.cur_player_idx == 2: # SUMMARIZER
            if outputs[0] == SUMMARIZER_ACTIONS[0]:
                self.comm_channel = outputs[1]
                self.full_game_log += f"{self.agents[self.cur_player_idx].name} summarized the game so far: {outputs[1]}\n"
        return False

    def game_loop(self):
        for t in range(self.max_turn_count):
            self.turn_count = t
            curr_player = self.agents[self.cur_player_idx]
            outputs = curr_player.take_turn(self.comm_channel[:], self.max_turn_count - t)
            if self.handle_agent_outputs(outputs):
                print(f"Turn {t}: The culprit was currectly accused")
                return True
            self.cur_player_idx = (self.cur_player_idx + 1) % self.agent_count
        print("The agents failed to find the culprit within the turn limit.")
        return False



