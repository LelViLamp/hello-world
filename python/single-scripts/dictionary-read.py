capitals = {}

fobj = open("single-scripts/eu-capitals.csv", "r")
for line in fobj:
    record = line.split(",")
    # country = record[0]
    # capital = record[1]
    capitals[record[0].strip()] = record[1].strip().replace(";", "")
fobj.close()

print("You can now query this 'database' of EU member states and its capitals")
print("To exit, send an empty query")

cancel = False
while not cancel:
    country = input("Please enter the English name of an EU member state: ").strip()
    if country == "":
        cancel = True
    elif country in capitals:
        print("The capital of", country, "is", capitals[country])
    else:
        print(country, "is not an EU member state")

print("The program has terminated as wished by the user")
