from consts import ACCUSER_ACTIONS, INTEL_ACTIONS, SUMMARIZER_ACTIONS
from groq_utils import query_llama

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
        #######
        # your code here
        #
        # Allow your agent to have internal thought, and generating more tokens before arriving to the final decision.
        # Do this using your prompts.
        # Make sure the final output of your thought process is still in the format of (action, action_info), where action is one of the strings in INTEL_ACTIONS,
        # and action_info is the information needed to perform that action.
        #
        # if action is "respond", then action_info should be Yes or No, as an answer to the question being asked
        # if action is "respond-broad", then action_info should contain a list of all characters that have the requested property.
        #######
        raise NotImplementedError
        pass


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
        #######
        # your code here
        #
        # Allow your agent to have internal thought, and generating more tokens before arriving to the final decision.
        # Do this using your prompts.

        # Make sure the final output of your thought process is still in the format of (action, action_info), where action is one of the strings in ACCUSER_ACTIONS,
        # and action_info is the information needed to perform that action.
        #
        # if action is "request-specific", then action_info should be the specific question being asked
        # if action is "request-broad", then action_info should be the attribute being asked about (e.g. "hat")
        # if action is "accuse", then action_info should be the suspect being accused (e.g. "Suspect 1")

        # return action_name, action_info
        #######
        raise NotImplementedError
        pass


    def take_turn(self, comm_channel, turns_left=None):
        if self.allow_internal_thought:
            return self.take_turn_thought(comm_channel, turns_left=None)
        return self.take_turn_naive(comm_channel)

class SummerizerAgent(Agent):
    def __init__(self, name):
        super().__init__(name)

    def summarize(self, comm_channel):
        #######
        # your code here

        # return summary
        #######
        raise NotImplementedError

    def take_turn(self, comm_channel, turns_left=None):
        summary = self.summarize(comm_channel)
        return SUMMARIZER_ACTIONS[0], summary