import random
choices=["rock","paper","scissors"]
print("welcome to Rock,Paper,Scissors!")
while True:
    user_choice=input("Enter Rock,Paper,Scissors(or 'quit' to stop):")
    if user_choice=="quit":
        print("thanks for playing")
        break
    if user_choice not in choices:
        print("Invalid choice.please try again.")
        continue
    computer_choice=random.choice(choices)
    print(f"Computer chose:{computer_choice}")
    #determine the winner
    if user_choice==computer_choice:
        print("its a tie!")
    elif (user_choice=="rock" and computer_choice=="scissors") or \
         (user_choice=="paper" and computer_choice=="rock") or \
         (user_choice=="scissors" and computer_choice=="paper"):
        print("You win")
    else:
        print("COmputer wins")
    print('-'*20)