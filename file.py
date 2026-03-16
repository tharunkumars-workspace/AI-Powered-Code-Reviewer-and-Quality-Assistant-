file = open("data.txt", "w")
file.write("Hello, World!\n")
file.write("Welcome to Python programming.\n")
file.close()


file = open("data.txt", "r")
content = file.read()
print(content)
file.close()



file = open("data.txt", "a")
file.write("This is an additional line.\n")
file.close()