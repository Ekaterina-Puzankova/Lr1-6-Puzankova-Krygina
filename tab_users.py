import mysql.connector


db_config = {
    'user': 'Ekaterina Puzankova',
    'password': 'EkaterinaPuzankova!!!',
    'host': 'LAPTOP-VJNPBOQI',
    'database': 'polzovateli_bota'
}


cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

cursor.execute("SELECT * FROM users")


for row in cursor:
  print(row)

cursor.close()
cnx.close()