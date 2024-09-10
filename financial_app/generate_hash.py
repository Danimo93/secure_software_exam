import bcrypt

# The password you want to hash
password = 'password'

# Generate the bcrypt hash
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

# Print the hashed password so you can copy it to your database
print(hashed_password)
