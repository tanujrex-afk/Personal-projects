import random
import string
print("Welcome to Secure Password Generator!")
while True:
    length_input=input("Enter the password")
    if not length_input.isdigit():
        print("please enter a vlaid number.")
        continue
    length=int(length_input)
    if length<8:
        print("Passowrd is too short for security. try a number 8 or higher.")
        continue
    break
# gather all the characcter strings types
letters=string.ascii_letters
digits=string.digits
symbols=string.punctuation
all_characters=letters+digits+symbols
password="".join(random.choice(all_characters) for i  in range(length))
print(f"\nYour secure password is:{password}")