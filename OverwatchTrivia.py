import random

heroes = {
"Ana": "support" ,
"Anran": "dps" ,
"D.Mon": "tank" ,
"Tracer": "dps" ,
"Mercy" : "support" ,
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

score = 0

round_heroes = random.sample(list(heroes.items()), k=3)

for hero_num, (hero, role) in enumerate(round_heroes, start=1):
    print()
    
    print(f"Question {hero_num}/{len(round_heroes)}:")
    if ask_question(hero, role):
        score += 1

print(f"You got {score}/{len(round_heroes)}!")