import re

from consts import ACCUSER_ACTIONS, INTEL_ACTIONS, SUMMARIZER_ACTIONS
from groq_utils import query_llama


def _parse_final_action(response):
    """Extract the final ACTION/INFO fields from a reasoning-laden response.

    The reasoning agents think out loud before answering, so we take the LAST
    occurrence of each tag and keep only its first line, ignoring any
    chain-of-thought text that precedes or follows the final answer block.
    Returns (action_part, info_part) as stripped strings.
    """
    action_idx = response.rfind("ACTION:")
    info_idx = response.rfind("INFO:")
    if action_idx != -1 and info_idx != -1 and info_idx > action_idx:
        action_part = response[action_idx + len("ACTION:"):info_idx]
        info_part = response[info_idx + len("INFO:"):]
    else:
        action_part = ""
        info_part = response.split("INFO:")[-1]

    action_part = action_part.strip().splitlines()[0].strip() if action_part.strip() else ""
    info_part = info_part.strip().splitlines()[0].strip() if info_part.strip() else ""
    return action_part, info_part


class Agent:
    def __init__(self, name):
        self.name = name
    def take_turn(self, comm_channel):
        raise NotImplementedError

class IntelAgent(Agent):
    def __init__(self, name, suspects, allow_internal_thought=False):
        super().__init__(name)
        self.suspects = suspects
        self.all_suspects_descriptions = ["Suspect " + str(i + 1) + ": " + s.generate_suspect_description() for i, s in
                                          enumerate(suspects)]
        self.all_descriptions_string = "\n".join(self.all_suspects_descriptions)
        self.allow_internal_thought = allow_internal_thought

    def take_turn_naive(self, comm_channel):
        last_message = comm_channel.split("\n")[-2]  # Simplified extraction of the last message

        sys_prompt = f"""
                You are an Intel Agent. You have access to the suspect data: 
                {self.all_descriptions_string}        
                You are getting asked question and need to answer based on the suspect data you have.

                for each question, decide if it is a 'specific' question (Yes/No) or a 'broad' question (asking about specific trait/attibute).
                Return your answer in the following format:
                ACTION: [respond/respond-broad]
                INFO: [for specific question, Yes/No. For broad question, list of suspects that match the trait/attribute]
                
                You are not allowed to include any resoning process or extra tokens, only the final answer in the specified format.
                """
        prompt = f"""
                {last_message}
                """

        response = query_llama(prompt, sys_prompt=sys_prompt)

        # Simple parsing logic (Assuming the LLM follows the format)
        if "respond-broad" in response:
            action = "respond-broad"
            # Extract info logic here (simplified)
            action_info = response.split("INFO:")[-1].strip()
        else:
            action = "respond"
            action_info = response.split("INFO:")[-1].strip()

        return action, action_info


    def take_turn_thought(self, comm_channel, turns_left=None):
        lines = [l for l in comm_channel.split("\n") if l.strip()]
        last_message = lines[-1] if lines else comm_channel

        sys_prompt = f"""
                You are the Intel Agent in a deduction game. You have full access to all suspect data:
                {self.all_descriptions_string}

                The Accuser asks you questions to identify a hidden culprit. Answer truthfully and
                precisely, using ONLY the suspect data above.

                There are two kinds of questions:
                - specific: a Yes/No question about ONE particular suspect
                  (e.g. "Does Suspect 2 wear a brown hat?"). Use ACTION: respond and put Yes or No in INFO.
                - broad: asks which suspects have a given trait/attribute
                  (e.g. "which suspects have blue eyes?"). Use ACTION: respond-broad and put the
                  comma-separated list of matching suspects in INFO (e.g. "Suspect 1, Suspect 3").
                  If none match, put "None".

                Think step by step FIRST: identify the question type, find the relevant attribute,
                and check each suspect against it. You may write out this reasoning.
                Then, on the LAST two lines, output EXACTLY this format and nothing after it:
                ACTION: respond OR respond-broad
                INFO: <Yes/No for specific, or the comma-separated suspect list for broad>
                """
        prompt = f"""
                Question to answer:
                {last_message}
                """
        response = query_llama(prompt, sys_prompt=sys_prompt, temperature=0.3, max_tokens=1024)

        action_part, action_info = _parse_final_action(response)
        action = "respond-broad" if "broad" in action_part.lower() else "respond"
        return action, action_info


    def take_turn(self, comm_channel, turns_left=None):
        if self.allow_internal_thought:
            return self.take_turn_thought(comm_channel, turns_left)
        return self.take_turn_naive(comm_channel)

class AccuserAgent(Agent):
    def __init__(self, name, culprit_description, suspect_sount, allow_internal_thought=False):
        super().__init__(name)
        self.culprit_description = culprit_description
        self.suspect_count = suspect_sount
        self.allow_internal_thought = allow_internal_thought

    def take_turn_naive(self, comm_channel):
        sys_prompt = f"""
                You are the Accuser. Your goal is to find the culprit.
                There are {self.suspect_count} suspects in total.
                The culprit is described as follows: 
                {self.culprit_description}.

                Your only way to get information is by asking the Intel Agent questions about the suspects.
                if you think that you have enough information to decide who the culprit is, you can and should directly accuse him.
                Do it as soon as you are certain, because you only have a limited number of turns to find the culprit.
                """
        prompt = f"""                
                Game History: 
                {comm_channel}

                Choose your next move:
                1. request-specific: Ask a Yes/No question about a trait of a specific suspect.
                2. request-broad: Ask for all characters with a certain trait/attribute
                3. accuse: Name the suspect if you are enough certain. and no other suspect can fit the description you have.

                Return:
                ACTION: [action_name]
                INFO: [specific question about one suspect OR trait for broad request OR suspect name to accuse]
                
                You are not allowed to include any resoning process or extra tokens, only the final answer in the specified format.
                """

        response = query_llama(prompt, sys_prompt=sys_prompt)

        # Logic to map response to ACCUSER_ACTIONS
        if "accuse" in response.lower():
            return "accuse", response.split("INFO:")[-1].strip()
        elif "request-broad" in response.lower():
            return "request-broad", response.split("INFO:")[-1].strip()
        else:
            return "request-specific", response.split("INFO:")[-1].strip()


    def take_turn_thought(self, comm_channel, turns_left=None):
        turns_str = f"You have {turns_left} turns left." if turns_left is not None else ""
        sys_prompt = f"""
                You are the Accuser in a deduction game with {self.suspect_count} suspects,
                numbered "Suspect 1" ... "Suspect {self.suspect_count}".
                The culprit matches this description:
                {self.culprit_description}

                You do NOT see the suspects' descriptions. Your ONLY way to gather information is by
                asking the Intel Agent. {turns_str} You lose if you run out of turns, so be efficient
                and accuse as soon as exactly one suspect can match the culprit.

                Reason step by step before acting:
                1. List the culprit's key attributes from the description above.
                2. Go through the game history and, for EACH suspect, track which culprit attributes
                   are confirmed or ruled out. Maintain the set of suspects still consistent with ALL
                   the evidence gathered so far.
                3. Decide:
                   - If exactly ONE suspect is still consistent with every known culprit attribute, ACCUSE it.
                   - Otherwise, ask the SINGLE most informative next question. Prefer a request-broad
                     that splits the remaining candidates, and never repeat a question already asked.

                Your actions:
                - request-specific: a Yes/No question about a trait of ONE specific suspect.
                - request-broad: ask which suspects have a certain attribute value (e.g. "brown hat").
                - accuse: name the suspect you are certain is the culprit.

                Write out your reasoning first. Then, on the LAST two lines, output EXACTLY this
                format and nothing after it:
                ACTION: request-specific OR request-broad OR accuse
                INFO: <the question text for request-*, OR "Suspect N" for accuse>
                """
        prompt = f"""
                Game history so far:
                {comm_channel if comm_channel.strip() else "(empty - no questions have been asked yet)"}
                """
        response = query_llama(prompt, sys_prompt=sys_prompt, temperature=0.3, max_tokens=1024)

        action_part, action_info = _parse_final_action(response)
        low = action_part.lower()
        if "accuse" in low:
            # Normalize to the exact "Suspect N" format Env.test_accusation expects.
            match = re.search(r"\d+", action_info)
            accusation = f"Suspect {match.group()}" if match else action_info
            return "accuse", accusation
        elif "broad" in low:
            return "request-broad", action_info
        else:
            return "request-specific", action_info


    def take_turn(self, comm_channel, turns_left=None):
        if self.allow_internal_thought:
            return self.take_turn_thought(comm_channel, turns_left)
        return self.take_turn_naive(comm_channel)

class SummerizerAgent(Agent):
    def __init__(self, name, suspect_sount=None):
        super().__init__(name)
        self.suspect_count = suspect_sount

    def summarize(self, comm_channel):
        # Nothing to compress yet: return the channel unchanged.
        if not comm_channel.strip():
            return comm_channel

        count_str = f"{self.suspect_count} suspects" if self.suspect_count else "several suspects"
        sys_prompt = f"""
                You are the Summarizer in a deduction game with {count_str} (referred to as
                "Suspect 1", "Suspect 2", ...). You are given the current communication channel
                between the Accuser and the Intel agent, and you must REWRITE it into a shorter
                version that lets the game continue without losing any information.

                You MUST preserve every evidentiary detail exactly:
                - For each suspect, keep every confirmed fact: which attribute values they DO have
                  and which they DO NOT have.
                - Keep the result of every question the Accuser asked and every answer the Intel gave.
                - Keep any accusation that was made and whether it was wrong.

                Rules:
                - Do NOT invent, guess, or alter any fact. If it was not stated, do not add it.
                - Do NOT drop any clue; a lost clue can cause the Accuser to fail.
                - Be concise: merge redundant statements and organize the facts per suspect.
                - Output ONLY the rewritten channel text, with no preamble or extra commentary.
                """
        prompt = f"""
                Current communication channel:
                {comm_channel}
                """
        summary = query_llama(prompt, sys_prompt=sys_prompt, temperature=0.2, max_tokens=1024)
        # Trailing newline keeps the naive Intel's last-message parsing intact after a rewrite.
        return summary.strip() + "\n"

    def take_turn(self, comm_channel, turns_left=None):
        summary = self.summarize(comm_channel)
        return SUMMARIZER_ACTIONS[0], summary