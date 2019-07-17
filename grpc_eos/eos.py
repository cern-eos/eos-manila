import os
import shutil
#import string
#import random

def report(action, response):
   print("Share " + action  + ": " +  response.msg + ". Code: " + str(response.code))

def create_share(request):   
   path = os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.share_name
   
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
   old_path = os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.share_name
   shutil.rmtree(old_path, ignore_errors=True)
   
   return old_path 
   
def change_share_size(request):
   file = open(os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.share_name + "/size.txt", 'w')
   file.write(str(request.quota))
   file.close()


#def shrink_share(request):
   
