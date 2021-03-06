import settings

r_dict = {
    "streakGuide": {
        "Classicmode": ["🟢", settings.config["modeRoles"]["classicmode"],
            "Assigns you Classicmode which implies no watching of pornography and no masturbation."],
        "Hardmode": ["🟡", settings.config["modeRoles"]["hardmode"],
            "Assigns you Hardmode which includes all rules of Classicmode plus no sex"],
        "Monkmode": ["🔴", settings.config["modeRoles"]["monkmode"],
            "Assigns you Monkmode which includes all rules of Hardmode, plus no potential arousal sources from media"],
        "AnonStreak": ["🕵", settings.config["modeRoles"]["anon-streak"],
            "Assigns you the Anon Streak role, this allows you to keep your current streak secret"]
    },
    "Utility": {
        "Helper": ["🆘", settings.config["otherRoles"]["helper"]],
        "Chat Revive": ["❗", settings.config["otherRoles"]["chat-revive"]],
        "Support Group": ["⚕", settings.config["otherRoles"]["support-group"]],
        "Urge Killer": ["🪳", settings.config["otherRoles"]["urge-killer"]],
        "Virgin": ["👑", settings.config["otherRoles"]["virgin"]],
        "Caveman": ["📵", settings.config["otherRoles"]["cavemanmode"]],
        "Retention": ["⚓", settings.config["otherRoles"]["retention"]]
    },
    "Gender": {
        "Male": ["♂", settings.config["genderRoles"]["male"]],
        "Female": ["♀", settings.config["genderRoles"]["female"]]
    },
    "Religion": {
        "Islam": ["☪", settings.config["religionRoles"]["islam"]],
        "Christianity": ["✝", settings.config["religionRoles"]["christianity"]],
        "Judaism": ["✡", settings.config["religionRoles"]["judaism"]],
        "Religious Else": ["♾", settings.config["religionRoles"]["religious-else"]]
    },
    "Location": {
        "Antarctica": ["🇦🇶", settings.config["continentRoles"]["antarctica"]],
        "Oceania": ["🇦🇺", settings.config["continentRoles"]["oceania"]],
        "North-America": ["🇺🇸", settings.config["continentRoles"]["north-america"]],
        "South-America": ["🇧🇷", settings.config["continentRoles"]["south-america"]],
        "Europe": ["🇪🇺", settings.config["continentRoles"]["europe"]],
        "Africa": ["🇿🇦", settings.config["continentRoles"]["africa"]],
        "Asia": ["🇨🇳", settings.config["continentRoles"]["asia"]]
    },
    "Hobbies": {
        "Hydrator": ["💧", settings.config["hobbies"]["hydrator"]],
        "Productivity": ["✍", settings.config["hobbies"]["productivity"]],
        "Book Club": ["📚", settings.config["hobbies"]["book-club"]],
        "Fitness": ["🏋️‍♂️", settings.config["hobbies"]["fitness"]],
        "Chess": ["♟", settings.config["hobbies"]["chess"]],
        "Discussions": ["🗣", settings.config["hobbies"]["discussions"]],
        "Relationships": ["💑", settings.config["hobbies"]["relationships"]]
    },
    "Misc": {
        "Memes": ["🚽", settings.config["misc"]["memes"]],
        "Media": ["🗞", settings.config["misc"]["media"]],
        "Polls": ["🗳", settings.config["misc"]["polls"]],
        "Asylum": ["🤯", settings.config["misc"]["asylum"]]
    }
}
