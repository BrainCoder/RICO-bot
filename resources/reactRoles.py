import settings

r_dict = {
    "streakGuide": {
        "Classicmode": ["π’", settings.config["modeRoles"]["classicmode"],
            "Assigns you Classicmode which implies no watching of pornography and no masturbation."],
        "Hardmode": ["π‘", settings.config["modeRoles"]["hardmode"],
            "Assigns you Hardmode which includes all rules of Classicmode plus no sex"],
        "Monkmode": ["π΄", settings.config["modeRoles"]["monkmode"],
            "Assigns you Monkmode which includes all rules of Hardmode, plus no potential arousal sources from media"],
        "AnonStreak": ["π΅", settings.config["modeRoles"]["anon-streak"],
            "Assigns you the Anon Streak role, this allows you to keep your current streak secret"]
    },
    "Utility": {
        "Helper": ["π", settings.config["otherRoles"]["helper"]],
        "Chat Revive": ["β", settings.config["otherRoles"]["chat-revive"]],
        "Support Group": ["β", settings.config["otherRoles"]["support-group"]],
        "Urge Killer": ["πͺ³", settings.config["otherRoles"]["urge-killer"]],
        "Virgin": ["π", settings.config["otherRoles"]["virgin"]],
        "Caveman": ["π΅", settings.config["otherRoles"]["cavemanmode"]],
    },
    "Gender": {
        "Male": ["β", settings.config["genderRoles"]["male"]],
        "Female": ["β", settings.config["genderRoles"]["female"]]
    },
    "Religion": {
        "Islam": ["βͺ", settings.config["religionRoles"]["islam"]],
        "Christianity": ["β", settings.config["religionRoles"]["christianity"]],
        "Judaism": ["β‘", settings.config["religionRoles"]["judaism"]],
        "Religious Else": ["βΎ", settings.config["religionRoles"]["religious-else"]]
    },
    "Location": {
        "Antarctica": ["π¦πΆ", settings.config["continentRoles"]["antarctica"]],
        "Oceania": ["π¦πΊ", settings.config["continentRoles"]["oceania"]],
        "North-America": ["πΊπΈ", settings.config["continentRoles"]["north-america"]],
        "South-America": ["π§π·", settings.config["continentRoles"]["south-america"]],
        "Europe": ["πͺπΊ", settings.config["continentRoles"]["europe"]],
        "Africa": ["πΏπ¦", settings.config["continentRoles"]["africa"]],
        "Asia": ["π¨π³", settings.config["continentRoles"]["asia"]]
    },
    "Hobbies": {
        "Productivity": ["β", settings.config["hobbies"]["productivity"]],
        "Book Club": ["π", settings.config["hobbies"]["book-club"]],
        "Fitness": ["ποΈββοΈ", settings.config["hobbies"]["fitness"]],
        "Chess": ["β", settings.config["hobbies"]["chess"]],
        "Discussions": ["π£", settings.config["hobbies"]["discussions"]],
        "Investing": ["π", settings.config["hobbies"]["investing"]]
    },
    "Misc": {
        "Memes": ["π½", settings.config["misc"]["memes"]],
        "Media": ["π", settings.config["misc"]["media"]],
        "Polls": ["π³", settings.config["misc"]["polls"]],
        "Asylum": ["π€―", settings.config["misc"]["asylum"]],
        "Relationships": ["π", settings.config["misc"]["relationships"]],
        "Counting": ["π’", settings.config["misc"]["counting"]]
    }
}
