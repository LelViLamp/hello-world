ref1 = 1337
ref2 = ref1

print("ref1 is", ref1, "of type", type(ref1))
print("ref2 is", ref2, "of type", type(ref2))

ref2 = 1338

print("ref1 is", ref1, "of type", type(ref1))
print("ref2 is", ref2, "of type", type(ref2))

ref2 = "Hello World"

print("ref1 is", ref1, "of type", type(ref1))
print("ref2 is", ref2, "of type", type(ref2))

ref2 = ref1

print("They are the same?", ref1 == ref2)
print("Their IDs are", id(ref1), "and", id(ref2), "So they are the same?", id(ref1) == id(ref2))

ref1 = 1337
ref2 = 1337

print("They are the same?", ref1 == ref2)
print("Their IDs are", id(ref1), "and", id(ref2), "So they are the same?", id(ref1) == id(ref2))

ref1 = "Hello World"
ref2 = "Hello World"    # the same as ref1

print("They are the same?", ref1 == ref2)
print("Their IDs are", id(ref1), "and", id(ref2), "So they are the same?", id(ref1) == id(ref2))

ref1 = "Hello World"
ref2 = ref1             # the same as ref1

print("They are the same?", ref1 == ref2)
print("Their IDs are", id(ref1), "and", id(ref2), "So they are the same?", id(ref1) == id(ref2))

ref1 = [1, 2, 3]
ref2 = [1, 2, 3]        # NOT the same as ref1
ref3 = ref1             # the same as ref1

print("They are the same?", ref1 == ref2)
print("Their IDs are", id(ref1), "and", id(ref2), "So they are the same?", id(ref1) == id(ref2))

# own operator for this:
print(ref1 is ref2)
del ref1
del ref2, ref3          # ref4, ref5, ...