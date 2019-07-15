import os

path = os.path.expanduser('~') + "/eos_shares"
used = 0
#print(os.listdir(path))

for root, directories, files in os.walk(path):

    for file in files:

        if file.endswith(".txt"):
            f = open(os.path.join(root, file))
            used = used + int(f.read())
            
            continue
        else:
            continue

print(used)
