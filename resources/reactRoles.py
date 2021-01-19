import settings

r_dict = {
    "streakGuide": {
        "Classicmode": ["🟢", settings.config["modeRoles"]["classicmode"],
            "Assigns you Classicmode which implies no watching of pornography and no masturbation."],
        "Hardmode": ["🟡", settings.config["modeRoles"]["hardmode"],
            "Assigns you Hardmode which includes all rules of clasicmode plus no sex"],
        "Monkmode": ["🔴", settings.config["modeRoles"]["monkmode"],
            "Assigns you Monkmode which includes all rules of hardmode plus no potential arousal sources for media"],
        "AnonStreak": ["🕵", settings.config["modeRoles"]["anon-streak"],
            "Assigns you the anon-streak role, this allows you to keep your current streak secret"]
    },
    "utilityRoles": {
        "helper": ["🆘", settings.config["otherRoles"]["helper"]],
        "supportGroup": ["⚕", settings.config["otherRoles"]["support-group"]],
        "urgeKiller": ["🪳", settings.config["otherRoles"]["urge-killer"]],
        "virgin": ["👑", settings.config["otherRoles"]["virgin"]],
        "caveman": ["📵", settings.config["otherRoles"]["cavemanmode"]],
        "retention": ["⚓", settings.config["otherRoles"]["retention"]]
    },
    "gender": {
        "male": ["♂", settings.config["genderRoles"]["male"]],
        "female": ["♀", settings.config["genderRoles"]["female"]]
    },
    "religion": {
        "islam": ["☪", settings.config["religionRoles"]["islam"]],
        "christianity": ["✝", settings.config["religionRoles"]["christianity"]],
        "judaism": ["✡", settings.config["religionRoles"]["judaism"]],
        "else": ["♾", settings.config["religionRoles"]["religious-else"]]
    },
    "location": {
        "antarctica": ["🇦🇶", settings.config["continentRoles"]["antarctica"]],
        "oceania": ["🇦🇺", settings.config["continentRoles"]["oceania"]],
        "north-america": ["🇺🇸", settings.config["continentRoles"]["north-america"]],
        "south-america": ["🇧🇷", settings.config["continentRoles"]["south-america"]],
        "europe": ["🇪🇺", settings.config["continentRoles"]["europe"]],
        "africa": ["🇿🇦", settings.config["continentRoles"]["africa"]],
        "asia": ["🇨🇳", settings.config["continentRoles"]["asia"]]
    },
    "hobbies": {
        "hydrator": ["💧", settings.config["hobbies"]["hydrator"]],
        "productivity": ["✍", settings.config["hobbies"]["productivity"]],
        "book-club": ["📚", settings.config["hobbies"]["book-club"]],
        "fitness": ["🏋️‍♂️", settings.config["hobbies"]["fitness"]],
        "chess": ["♟", settings.config["hobbies"]["chess"]],
        "discussions": ["🗣", settings.config["hobbies"]["discussions"]],
        "relationships": ["💑", settings.config["hobbies"]["relationships"]]
    },
    "misc": {
        "memes": ["🚽", settings.config["misc"]["memes"]],
        "media": ["🗞", settings.config["misc"]["media"]],
        "polls": ["🗳", settings.config["misc"]["polls"]],
        "asylum": ["🤯", settings.config["misc"]["asylum"]]
    }
}
