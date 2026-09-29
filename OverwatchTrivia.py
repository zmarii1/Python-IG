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
    "Zenyatta": "support",
}

def ask_question(hero_name, hero_role):
    print(f"What role is {hero_name}?")
    guess = input("Your answer: ").strip().lower()
    if guess == hero_role:
        print("Correct!")
        return True
    else:
        print(f"Incorrect. The correct answer is {hero_role}.")
        return False

def play_round(num_questions=len(heroes)):
    score = 0
    round_heroes = random.sample(list(heroes.items()), k=num_questions)
    for hero_num, (hero, role) in enumerate(round_heroes, start=1):
        print()
        print(f"Question {hero_num}/{len(round_heroes)}:")
        if ask_question(hero, role):
            score += 1
    return score, num_questions

try:
    num_questions = int(input(f"How many questions? (1-{len(heroes)}): "))
    if num_questions < 1 or num_questions > len(heroes):
        print("Not a valid number, playing all questions.")
        num_questions = len(heroes)
except ValueError:
    print("Not a valid number, playing all questions.")
    num_questions = len(heroes)

score, total = play_round(num_questions)
print(f"You got {score}/{total}!")