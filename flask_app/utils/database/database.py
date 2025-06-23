import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow




class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    def getResumeData(self):
        institutions = self.query("SELECT * FROM institutions")
        data = {}

        for institution in institutions:
            inst_id = institution['inst_id']
            data[inst_id] = {
                'type': institution['type'],
                'name': institution['name'],
                'department': institution['department'],
                'address': institution['address'],
                'city': institution['city'],
                'state': institution['state'],
                'zip': institution['zip'],
                'positions': {}
            }
            
            positions = self.query("SELECT * FROM positions WHERE inst_id = %s", (inst_id,))
            for position in positions:
                pos_id = position['position_id']
                data[inst_id]['positions'][pos_id] = {
                    'title': position['title'],
                    'start_date': position['start_date'],
                    'end_date': position['end_date'],
                    'responsibilities': position['responsibilities'],
                    'experiences': {}
                }

                experiences = self.query("SELECT * FROM experiences WHERE position_id = %s", (pos_id,))
                for experience in experiences:
                    exp_id = experience['experience_id']
                    data[inst_id]['positions'][pos_id]['experiences'][exp_id] = {
                        'name': experience['name'],
                        'description': experience['description'],
                        'hyperlink': experience['hyperlink'],
                        'start_date': experience['start_date'],
                        'end_date': experience['end_date'],
                        'skills': {}
                    }

                    skills = self.query("SELECT * FROM skills WHERE experience_id = %s", (exp_id,))
                    for skill in skills:
                        skill_id = skill['skill_id']
                        data[inst_id]['positions'][pos_id]['experiences'][exp_id]['skills'][skill_id] = {
                            'name': skill['name'],
                            'skill_level': skill['skill_level']
                        }
                        
        return data

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        messages = []

        existing_user = self.query("SELECT * FROM users WHERE email = %s", (email,))
        if existing_user:
            stored_password = existing_user[0].get('password', '')
            if password and not stored_password:
                try:
                    user_id = existing_user[0]['user_id']
                    encrypted_password = self.onewayEncrypt(password)

                    self.insertRows(
                        table='users',
                        columns=['user_id', 'email', 'password', 'role'],
                        parameters=[[user_id, email, encrypted_password, role]]
                    )

                    messages.append(f"Updated user with new password: {email}")
                    return {'success': 1, 'message': ', '.join(messages)}

                except Exception as e:
                    messages.append(f"Error processing user {email}: {str(e)}")
                    return {'success': 0, 'message': ', '.join(messages)}
            
            messages.append(f"User already exists: {email}")
            return {'success': 1, 'message': ', '.join(messages)}

        encrypted_password = self.onewayEncrypt(password)
        try:
            self.insertRows(
                table='users',
                columns=['email', 'password', 'role'],
                parameters=[[email, encrypted_password, role]]
            )
            messages.append(f"Successfully created user: {email}")
            return {'success': 1, 'message': ', '.join(messages)}

        except Exception as e:
            messages.append(f"Error creating user: {email}. Error: {str(e)}")
            return {'success': 0, 'message': ', '.join(messages)}

    # def authenticate(self, email='me@email.com', password='password'):
    #     # return {'success': 1}
    #     encrypted_password = self.onewayEncrypt(password)

    #     user = self.query("SELECT * FROM users WHERE email = %s AND password = %s", (email, encrypted_password))
    #     if user:
    #         return {'success': 1}
    #     else:
    #         return {'success': 0, 'message': 'Authentication failed'}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


