import random
word_pool=["python","computer","programming","developer","keyboard","gadget"]
secret_word= random.choice(word_pool)
guessed_letters=["_"]*len(secret_word)
attempts_left=7
wrong_gueeses=[]
print("Welcome to Hangman")
#main game loop
while attempts_left>0 and "_" in guessed_letters:
    print("\nWord to guess:"+"".join(guessed_letters))
    print(f"Attempts left:{attempts_left}")
    print(f"Wrong letters gueesed:{','.join(wrong_gueeses)}")
    guess=input("Guess a letter:").lower()
    #validation: make sure they enterd exactly one letter
    if len(guess)!=1 or not guess.isalpha():
        print("please enter a single valid letter.")
        continue
    #check if they already tried this letter
    if guess in guessed_letters or guess in wrong_gueeses:
        print("you have already guessed taht letter!")
        continue
    #check if the guessed letter is in the secret word
    if guess in secret_word:
        print(f"Good Job!'{guess}' is in the word.")
        for index in range(len(secret_word)):
            if secret_word[index]== guess:
                guessed_letters[index]=guess
    else:
        print(f"Sorry,'{guess}' is not in the word")
        wrong_gueeses.append(guess)
        attempts_left-=1
#check the final game state
if "_" not in guessed_letters:
    print(f"\nCongrajualtions! you Won!the word was:{secret_word}")
else:
    print(f"\nGame over! you ran out of attempts. the word was:{secret_word}")
