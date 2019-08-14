import os
import shutil
import ConfigParser
#import random

BEGIN_PATH = os.path.expanduser('~') + "/eos_shares/"
configParser = ConfigParser.RawConfigParser()

def report(action, response):
   print("Share " + action  + ": " +  response.msg + ". Code: " + str(response.code) + "\n")

def create_share(request):
   #access CERN share export location by using "request.share_location"

   #this is the location that the share will be created
   path = BEGIN_PATH + request.creator + "/" + request.share_name
  
   #check to see if the path already exists 
   if os.path.isdir(path):
      path = "1"
   else:
      os.makedirs(path)

      #want some way to record how large the share should be -- storing a file with no. of GB
      file = open(path + "/share.ini", "w+")
      file.write("[MANILA-SHARE-CONFIG]\n")
      file.write("managed = True\n")
      file.write("size = " + str(request.quota) + "\n")
      file.close()
 
   return path

def delete_share(request):
   old_path = BEGIN_PATH + request.creator + "/" + request.share_name
   shutil.rmtree(old_path, ignore_errors=True)
   
   return old_path 
   
def change_share_size(request):
   path = BEGIN_PATH + request.creator + "/" + request.share_name + "/share.ini"
 
   configParser.read(path)
   configParser.set("MANILA-SHARE-CONFIG", "size", str(request.quota))
   
   f = open(path, 'w')
   configParser.write(f)
   f.close()

#def shrink_share(request):
#def extend_share(request):

def manage_existing(request):
   if not os.path.isdir(request.share_location):
      #can't manage a share path that does not exist
      return -1
   
   size = 0
   ini_path = request.share_location + "/share.ini"

   #check the size.txt in the folder for the TOTAL size of the share, NOT used
   try:
       if not os.path.isfile(ini_path): #check to see if the new share already has an .ini file -- if not, create one
          file = open(ini_path, "w+")
          file.write("[MANILA-SHARE-CONFIG]\n")
          file.close()
       else: #save the size of the share if the .ini file already exists
          configParser.read(ini_path)
          size = configParser.get("MANILA-SHARE-CONFIG", "size")
       
       #if the user has specified the size of the share in the request, use that instead
       if request.quota:
          size = request.quota

       #update the .ini file
       configParser.set("MANILA-SHARE-CONFIG", "size", size)
       configParser.set("MANILA-SHARE-CONFIG", "managed", "True")
       
       f = open(ini_path, 'w')
       configParser.write(f)
       f.close()

       #update share name -- nonfunctional :(
       folder_name = request.share_location[request.share_location.rindex("/"):]
       os.system("manila update " + request.share_id + " --name " + folder_name)
   except ValueError:
       size = -1

   return size

def unmanage(request):
   ini_path = request.share_location + "/share.ini"
   configParser.read(ini_path)
   configParser.set("MANILA-SHARE-CONFIG", "managed", "False") #ini no longer recognizes this share
   
   f = open(ini_path, 'w')
   configParser.write(f)
   f.close()

def get_used_capacity():
   # if the eos_shares path does not exist, create it so that get_capacities does not fail
   if not os.path.isdir(BEGIN_PATH):
      os.mkdir(BEGIN_PATH)
      return "0"

   path = BEGIN_PATH
   used = 0

   #simply getting the sum of all the shares to report back to manila
   for root, directories, files in os.walk(path):
       for file in files:
           if file.endswith("share.ini"):
               try:
                   configParser.read(os.path.join(root, file))
                   if (configParser.get('MANILA-SHARE-CONFIG', 'managed')).upper() == "TRUE":
                       used = used + int(configParser.get('MANILA-SHARE-CONFIG', 'size')) 
               except ValueError:
                   continue
           else:
               continue
   
   return used

def get_total_capacity():
   return 50
