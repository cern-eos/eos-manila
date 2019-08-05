import os
import ConfigParser

path = os.path.expanduser('~') + "/eos_shares"
used = 0
#print(os.listdir(path))
#path = BEGIN_PATH
#used = 0

for root, directories, files in os.walk(path):
    for file in files:
        if file.endswith("share.ini"):
            #f = open(os.path.join(root, file))
            #try:
            configParser = ConfigParser.RawConfigParser()
            configParser.read(os.path.join(root, file))
            if (configParser.get('MANILA-SHARE-CONFIG', 'managed')).upper() == "TRUE":
                used = used + int(configParser.get('MANILA-SHARE-CONFIG', 'size'))
        else:
            continue

print(str(used))

