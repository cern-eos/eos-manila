import openstack

conn = openstack.connect(auth_url='http://188.185.71.204/identity/v3', 
                         username='admin', 
                         password='nomoresecret',
                         project_name='admin')
#print(conn.identity.users())

user_now = conn.identity.get_user('5e9be28237244bb184a8b6f77252b286')
print(user_now.name)

#for user in conn.identity.users():
#    print(user)
