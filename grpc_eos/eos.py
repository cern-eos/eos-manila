import os
import shutil
#import string
#import random

BEGIN_PATH = os.path.expanduser('~') + "/eos_shares/"

def report(action, response):
   print("Share " + action  + ": " +  response.msg + ". Code: " + str(response.code) + "\n")

def create_share(request):   
   path = BEGIN_PATH + request.creator + "/" + request.share_name
   
   if os.path.isdir(path):
      path = "1"
   else:
      os.makedirs(path)

      #want some way to record how large the share is -- storing a file with no. of GB
      file = open(path + "/size.txt", "w+")
      file.write(str(request.quota))
      file.close()
 
   return path

def delete_share(request):
   old_path = BEGIN_PATH + request.creator + "/" + request.share_name
   shutil.rmtree(old_path, ignore_errors=True)
   
   return old_path 
   
def change_share_size(request):
   file = open(BEGIN_PATH + request.creator + "/" + request.share_name + "/size.txt", 'w')
   file.write(str(request.quota))
   file.close()

#def shrink_share(request):
#def extend_share(request):

def get_used_capacity():
   # if the eos_shares path does not exist, create it so that get_capacities does not fail
   if not os.path.isdir(BEGIN_PATH):
      os.mkdir(BEGIN_PATH)
      return "0"

   path = BEGIN_PATH
   used = 0

   for root, directories, files in os.walk(path):
       for file in files:
           if file.endswith(".txt"):
               f = open(os.path.join(root, file))                    
               try:
                   used = used + int(f.read())
                   continue                    
               except ValueError:
                   continue
           else:
               continue
   
   return str(used)
