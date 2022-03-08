secret = 1337
guess = -1
attemptCounter = 0

while guess != secret:
    guess = int(input("Your guess: "))

    if guess < secret:
        print("too small")
    if guess > secret:
        print("too big")
    
    if guess == 42:
        print("but an attempt very much appreciated")
    
    attemptCounter = attemptCounter + 1

print("Great, you did it in", attemptCounter, "attempts!")