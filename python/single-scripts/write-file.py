capitals = { "UK":      "London",
             "Iceland": "Reykyavík",
             "Norway":  "Oslo" }

fobj = open("single-scripts/non-eu-capitals.csv", "w")
for country in capitals:
    fobj.write("{}, {};\n".format(country, capitals[country]))
fobj.close()