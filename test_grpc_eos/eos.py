import string
import random

def report(action, id, response, shares):
   print("Share (" + id  + ") " + action  + "  with " +  response.msg + ". Code: " + str(response.response_code))
   print("\n~ Available Shares [TOTAL: " + str(len(shares)) + " Shares] ~")
   print(shares)
   print("\n")


def create_share(request):
   share = {}
   share["name"] = request
   share["id"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

   return share
