AGENT_NAMES = ["Alex", "Beth", "Charlie", "David", "Elizabeth", "Fred", "Ginny"]
DEFAULT_ATTRIBUTE_FILE = 'utils/attributes_small.json'

ACCUSER_ACTIONS = ['request-specific', 'request-broad', 'accuse']
INTEL_ACTIONS = ['respond', 'respond-broad']
SUMMARIZER_ACTIONS = ['summerize']


#############################

FILLER_WORD = '<FILLER>'
NEGATE_WORD = '<NEGATE>'
ATTRIBUTE_TO_FORMAT = {
    'hat': 'is wearing a <FILLER> hat',
    'mood': 'is in a <FILLER> mood',
    'shirt_color': 'their shirt color is <FILLER>',
    'shirt_decal': 'they have an image of <FILLER> on their shirt',
    'pants': 'they are wearing <FILLER> pants',
    'pants_color': 'their pants color is <FILLER>',
    'eye_color': 'their eye color is <FILLER>',
    'eye_glasses': 'they have <FILLER> eye glasses',
    'hobby': "their hobby is <FILLER>",
    "shirt": "they're wearing a <FILLER> shirt",
    "shoe_color": "they have <FILLER> shoes",
    "hair": "their hair is <FILLER>",
    "watch": "they have a <FILLER> watch",
    "socks": "has a pair of <FILLER> socks", 
    "jacket": "a <FILLER> jacket on",
    "height": "is somewhat <FILLER>",
    "age": "looks to be <FILLER>", 
    "build": "is of a <FILLER> build",
    "personality": "has an <FILLER> personality", 
    "interests": "is known to be interested in <FILLER>",
    'occupation': "they are currently a <FILLER> in their field"
}

CHOSEN_NAME = "Chosen"
ATTRIBUTE_TO_SHARE = {
    'hat': f'The {CHOSEN_NAME} is wearing a <FILLER> hat',
    'mood': f'The {CHOSEN_NAME} is in a <FILLER> mood',
    'shirt_color': f'The {CHOSEN_NAME}\'s shirt color is <FILLER>',
    'shirt_decal': f'The {CHOSEN_NAME} has an image of <FILLER> on their shirt',
    'pants': f'The {CHOSEN_NAME} is wearing <FILLER> pants',
    'pants_color': f'The {CHOSEN_NAME}\'s pants color is <FILLER>',
    'eye_color': f'The {CHOSEN_NAME}\'s eye color is <FILLER>',
    'eye_glasses': f'The {CHOSEN_NAME} has <FILLER> eye glasses',
    'watch': f"The {CHOSEN_NAME} has a <FILLER> watch",
    'hobby': f"The {CHOSEN_NAME}'s hobby is <FILLER>",
    "shirt": f"The {CHOSEN_NAME} is wearing a <FILLER> shirt",
    "shoe_color": f"The {CHOSEN_NAME} have <FILLER> shoes",
    "hair": f"The {CHOSEN_NAME}'s hair is <FILLER>",
    "watch": f"The {CHOSEN_NAME} has a <FILLER> watch",
    "socks": f"The {CHOSEN_NAME} has a pair of <FILLER> socks", 
    "jacket": f"The {CHOSEN_NAME} has a <FILLER> jacket on",
    "height": f"The {CHOSEN_NAME} is known to be <FILLER>",
    "age": f"The {CHOSEN_NAME} is <FILLER>", 
    "build": f"The {CHOSEN_NAME} has a <FILLER> build",
    "personality": f"The {CHOSEN_NAME} has an <FILLER> personality", 
    "interests": f"The {CHOSEN_NAME} is known to be interested in <FILLER>",
    "occupation": f"The {CHOSEN_NAME} is a <FILLER> in their field"
}


ATTRIBUTE_TO_RESPONSE = {
    'hat': 'Character ID is <NEGATE>wearing a <FILLER> hat',
    'mood': 'Character ID is <NEGATE>in a <FILLER> mood',
    'shirt_color': 'Character ID\'s shirt color is <NEGATE><FILLER>',
    'pants': 'Character ID is <NEGATE>wearing <FILLER> pants',
    'pants_color': 'Character ID\'s pants color is <NEGATE><FILLER>',
    'eye_color': 'Character ID\'s eye color is <NEGATE><FILLER>',
    'eye_glasses': 'Character ID is <NEGATE>wearing <FILLER> eye glasses',
    'hobby': "Character ID's hobby is <NEGATE><FILLER>",
    "shirt": "Character ID is <NEGATE>wearing a <FILLER> shirt",
    "shoe_color": "Character ID shoes are <NEGATE><FILLER>",
    "hair": "Character ID's hair is <NEGATE><FILLER>",
    "watch": "Character ID is <NEGATE>wearing a <FILLER> watch"
}


def get_attribute_message(attr_key, attr_info):
    return ATTRIBUTE_TO_FORMAT[attr_key].replace(FILLER_WORD, attr_info)

def get_share_message(attr_key, attr_info):
    return ATTRIBUTE_TO_SHARE[attr_key].replace(FILLER_WORD, attr_info)

def get_response_message(attr_key, attr_info, requested_id, negate=False):
    answer = ATTRIBUTE_TO_RESPONSE[attr_key].replace(FILLER_WORD, attr_info).replace("ID", str(requested_id))
    answer = answer.replace(NEGATE_WORD, "not " if negate else "")
    return answer

