import random

heroes = {
    # Tank
    "D.Mon": "tank",
    "D.Va": "tank",
    "Domina": "tank",
    "Doomfist": "tank",
    "Hazard": "tank",
    "Junker Queen": "tank",
    "Mauga": "tank",
    "Orisa": "tank",
    "Ramattra": "tank",
    "Reinhardt": "tank",
    "Roadhog": "tank",
    "Sigma": "tank",
    "Winston": "tank",
    "Wrecking Ball": "tank",
    "Zarya": "tank",

    # DPS
    "Anran": "dps",
    "Ashe": "dps",
    "Bastion": "dps",
    "Cassidy": "dps",
    "Echo": "dps",
    "Emre": "dps",
    "Freja": "dps",
    "Genji": "dps",
    "Hanzo": "dps",
    "Junkrat": "dps",
    "Mei": "dps",
    "Pharah": "dps",
    "Reaper": "dps",
    "Shion": "dps",
    "Sierra": "dps",
    "Sojourn": "dps",
    "Soldier: 76": "dps",
    "Sombra": "dps",
    "Symmetra": "dps",
    "Torbjörn": "dps",
    "Tracer": "dps",
    "Vendetta": "dps",
    "Venture": "dps",
    "Widowmaker": "dps",

    # Support
    "Ana": "support",
    "Baptiste": "support",
    "Brigitte": "support",
    "Illari": "support",
    "Jetpack Cat": "support",
    "Juno": "support",
    "Kiriko": "support",
    "Lifeweaver": "support",
    "Lúcio": "support",
    "Mercy": "support",
    "Mizuki": "support",
    "Moira": "support",
    "Wuyang": "support",
}


def ask_question(hero_name, hero_role):
    if hero_role == "tank":
        return f"What role is {hero_name} in Overwatch? (tank/dps/support): "
    elif hero_role == "dps":
        return f"What role is {hero_name} in Overwatch? (tank/dps/support): "
    elif hero_role == "support":
        return f"What role is {hero_name} in Overwatch? (tank/dps/support): "
    else:
        return f"Invalid role: {hero_role}"  

def question_number():
    while True:
        try:
            num_questions = int(input("How many questions would you like to answer? "))
            if num_questions <= 0:
                print("Invalid input. Please enter a positive integer.")
            else:
                return num_questions
        except ValueError:
            print("Invalid input. Please enter a positive integer.")