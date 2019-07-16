import os
import shutil
#import string
#import random

def report(action, response):
   print("Share " + action  + "  with " +  response.msg + ". Code: " + str(response.response_code))
   #print("\n~ Available Shares [TOTAL: " + str(len(shares)) + " Shares] ~")
   #print(shares)

def create_share(request):
   #share = {}
   #share["name"] = request.name
   #share["id"] = request.id #''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
   
   #print(os.path.isdir("~/eos_shares/" + request.creator) is False)  
 
   #if os.path.isdir("~/eos_shares/" + request.creator) is False:
   #print("I am creating a new directory for the creator: " +  request.creator)
   #os.mkdir("~/eos_shares/" + request.creator)   

   # TODO: see if share name already exists
   path = os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.id
   #os.mkdir(path, 0755)
   os.makedirs(path)

   #want some way to record how large the share is -- storing a file with no. of GB
   file = open(path + "/size.txt", "w+")
   file.write(str(request.size))
   file.close()
   
   return path

def delete_share(request):
   return shutil.rmtree(os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.id, ignore_errors=True)

def change_share_size(request):
   
   file = open(os.path.expanduser('~') + "/eos_shares/" + request.creator + "/" + request.id + "/size.txt", 'w')
   file.write(str(request.new_size))
   file.close()


#def shrink_share(request):
   
