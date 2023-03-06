
# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
import pyodbc
import time
import MySQLdb

class Error(Exception):
    """Timer error"""

#Timer class
class Timer:
    def __init__(self):
        self.startTime = None

    def start(self):
        """Start a new timer"""
        if self.startTime is not None:
            raise Error("Timer is running.")

        self.startTime = time.perf_counter()

    def stop(self,type):
        """Stop the timer, and report the time"""
        if self.startTime is None:
            raise Error("Timer is not running.")

        Time = time.perf_counter() - self.startTime
        self.startTime = None
        print(f"{type}: {Time:0.4f} seconds")
        return Time

# Part 1 - Building a Blockchain
class Project:
    def __init__(self):
        self.projectId=0
        self.project_name=None
        self.address=None
        self.owner=None
        
    def set(self,projectId,project_name,address):
        self.projectId=projectId
        self.project_name=project_name
        self.address=address
    
        
    def get(self):
        project={'projectId': self.projectId,
                 'project_name':self.project_name,
                 'address': self.address,
                 'owner':self.owner}
        return project
        
class Activity:
    def __init__(self):
       self.activity_no=0
       self.project=None
       self.activity_name=None
       self.duration=None
       self.price=0
       self.start_date=None
       self.finish_date=None
       self.status=None
       self.approved=None
       #    self.deal=None
       self.delays=0
       self.contract_name=None
       
    def set(self,activity_no,project,activity_name,duration,price,start_date,finish_date,status,approved,delays,contract_name):
       self.activity_no=activity_no
       self.project=project
       self.activity_name=activity_name
       self.duration=duration
       self.price=price
       self.start_date=start_date
       self.finish_date=finish_date
       self.status=status
       self.approved=approved
       self.delays=delays
       self.contract_name=contract_name
       
    def get(self):
        act={'activity_no': self.activity_no,
             'project':self.project,
             'activity_name': self.activity_name,
             'duration':self.duration,
             'price':self.price,
             'start_date':self.start_date,
             'finish_date':self.finish_date,
             'status':self.status,
             'approved':self.approved,
             'delays':self.delays,
             'contract_name':self.contract_name}
        return act
    
class Contract:
    def __init__(self):
        self.contract_no=0
        self.contract_name=None
        self.project=None
        self.amount=0
        self.date=None
        self.Type=None
        self.parties=None
        self.penalty=0
        self.status=None
        
    def set(self,contract_no,contract_name,project,amount,date,Type,parties,penalty,status): 
        self.contract_no=contract_no
        self.contract_name=contract_name
        self.project=project
        self.amount=amount
        self.date=date
        self.Type=Type
        self.parties=parties
        self.penalty=penalty
        self.status=status
        
    def get(self):
        contract={'contract_no':self.contract_no,
                  'contract_name':self.contract_name,
                  'project': self.project,
                  'amount': self.amount,
                  'date': self.date,
                  'Type': self.Type,
                  'parties':self.parties,
                  'penalty':self.penalty,
                  'status':self.status}
        return contract
#class user
class User:
    
    def __init__(self):
        self.userId=None
        self.username=None
        self.password=None
        self.companyName=None
        self.credit=0
        self.identity=None
        self.email=None
        
    def set(self,userId,username,password,companyName,credit,identity,email):
        self.userId=userId
        self.username=username
        self.password=password
        self.companyName=companyName
        self.credit=credit
        self.identity=identity
        self.email=email
        
        
    def get(self):
        user={'userId':self.userId,
              'username':self.username,
              'password': self.password,
              'companyName': self.companyName,
              'credit':self.credit,
              'identity':self.identity,
              'email':self.email}
        return user
   
class Notification:
    def __init__(self):
        self.notifyId=0
        self.notification=None
        self.contract_name=None
        self.timestamp=None
        self.identity=None
        self.username=None
        
    def set(self,notifyId,notification,contract_name,timestamp,identity,username):
        self.notifyId=notifyId
        self.notification=notification
        self.contract_name=contract_name
        self.timestamp=timestamp
        self.identity=identity
        self.username=username
        
    def get(self):
        notification={'notifyId':self.notifyId,
              'notification':self.notification,
              'contract_name':self.contract_name,
              'timestamp':self.timestamp,
              'identity':self.identity,
              'username':self.username}
        return notification
class Claim:
    def __init__(self):
        self.claimId=0
        self.claim=None
        self.status=None
        self.username=None
        self.timestamp=None
        
    def set(self,claimId,claim,status,username,timestamp):
        self.claimId=claimId
        self.claim=claim
        self.status=status
        self.username=username
        self.timestamp=timestamp
    def get(self):
        claim={'claimId':self.claimId,
               'claim':self.claim,
               'status':self.status,
               'username':self.username,
               'timestamp':self.timestamp}
        return claim
"""   
class auth:

    def encryption(self,message):
    
        encrypted_message=public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        )
        
        return  encrypted_message
    
    def decryption(sellf,message):
        original_message = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        )
        return original_message
"""
class Blockchain:
    
    
    def __init__(self):
        self.user=[]
        self.chain = []
        self.transactions = []
        self.description=[]
        self.project=[]
        self.activity=[]
        self.contract=[]
        self.create_block(proof = 1, previous_hash = '0',contract_current=[],activity_current=[])
        self.nodes = set()
    #first blockchain only
    def create_block(self, proof, previous_hash,contract_current,activity_current):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions,
                 'project':self.project,
                 'contract': contract_current,
                 'activity':activity_current,
                 'party':self.user,
                 'description':self.description}
        self.transactions = []
        self.user=[]
        self.claim=[]
        self.project=[]
        self.activity=[]
        self.contract=[]
        self.description=[]
        self.chain.append(block)
        return block
    

    def get_previous_block(self):
        return self.chain[-1]
    
    def add_user(self,name):
        self.user.append(name)
        
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block,indent=4, sort_keys=True, default=str).encode()
        return hashlib.sha256(encoded_block).hexdigest()
        
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_project(self,project):
        self.project.append(project)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_activity(self,activity):
        self.activity.append(activity)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
        
    def add_contract(self,contract):
        self.contract.append(contract)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_description(self,message):
        self.description.append(message)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self,longest_chain):
        self.chain=longest_chain
        return True

# Part 2 - Mining our Blockchain
own_notification=[]
# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5001
node_address = str(uuid4()).replace('-', '')
block_cont=[]
block_act=[]
# Creating a Blockchain

blockchain = Blockchain()

"""connection_string='Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=.\Smart_Contract.accdb'"""
connection_string=MySQLdb.connect("Smart_Contract.accdb")
user=User() 

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    t=Timer()
    t.start()
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    contract_currunt=blockchain.contract
    block_cont.append(contract_currunt)
    activity_currunt=blockchain.activity
    block_act.append(activity_currunt)
    blockchain.add_transaction(sender = node_address, receiver = 'Owner', amount = 1)
    block = blockchain.create_block(proof, previous_hash,contract_currunt,activity_currunt)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions'],
                'project':block['project'],
                'contract': contract_currunt,
                'activity':activity_currunt,
                'party':block['party'],
                'description':block['description']}
    time=t.stop("Time elapsed for mining the block:")
    with open('Latency.txt', 'a', encoding='utf-8') as f:
               f.write(str(time)+'\n')
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200
# Getting ALL contracts
@app.route('/get_contracts', methods = ['GET'])
def get_contracts():
    list_contract=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from contract ")
    for row in cursor.fetchall():
        contract=Contract()
        contract.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        list_contract.append(contract.get())
    cursor.close()
    conn.close()
    response = {'contracts': list_contract}
    return jsonify(response), 200
# Getting ALL projects
@app.route('/get_projects', methods = ['GET'])
def get_projects():
    list_project=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from project ")
    for row in cursor.fetchall():
        project=Project()
        project.set(row[0],row[1],row[2])
        list_project.append(project.get())
    cursor.close()
    conn.close()
    response = {'projects': list_project}
    return jsonify(response), 200
# Getting ALL admins
@app.route('/get_admins', methods = ['GET'])
def get_users():
    users=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from user")
    for row in cursor.fetchall():
        user=User()
        user.set(row[1],row[3],row[4],row[5],row[6])
        users.append(user.get())
    cursor.close()
    conn.close()
    response = {'users': users}
    return jsonify(response), 200

@app.route('/remove_admin', methods = ['POST'])
def remove_admin():
    json = request.get_json()
    contract_keys = ['username']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    user=json['username']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("delete from user where username=?",user)
    conn.commit()
    cursor.execute("insert into notification([notification],[timestamp],[identity]) VALUES(?,?)",(f'admin username:{user} has been removed',datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.close()
    conn.close()
    response = {'message': f'admin username:{user} has been removed'}
    return jsonify(response), 201

@app.route('/get_activities', methods = ['GET'])
def get_act():
    t=Timer()
    t.start()
    list_activity=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from activity ")
    for row in cursor.fetchall():
        activity=Activity()
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
        list_activity.append(activity.get())
    cursor.close()
    conn.close()   
    response = {'activities': list_activity}
    time=t.stop("Time elapsed for query the block:")
    with open('Query.txt', 'a', encoding='utf-8') as f:
               f.write(str(time)+'\n')
    return jsonify(response), 200
# Getting ALL info for the node
@app.route('/get_info', methods = ['GET'])
def get_info():
    response = user.get()
    return jsonify(response), 200
# Getting ALL claims for the node
@app.route('/get_claims', methods = ['GET'])
def get_claims():
    claims=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from claim ")
    for row in cursor.fetchall():
        claim=Claim()
        claim.set(row[0],row[1],row[2],row[3],row[4])
        claims.append(claim.get())
    cursor.close()
    conn.close() 
    response = {'claims': claims}
    return jsonify(response), 200

#contractor method for getting claim
@app.route('/get_claim', methods = ['GET'])
def get_claim():
    claims=[]
    username = request.args.get('username')
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from claim where username=?",username)
    for row in cursor.fetchall():
        claim=Claim()
        claim.set(row[0],row[1],row[2],row[3],row[4])
        claims.append(claim.get())
    cursor.close()
    conn.close() 
    response = {'claims': claims}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200
# authorization part
    
@app.route('/login', methods = ['POST'])
def login():
    json = request.get_json()
    username=(json['username'],)
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select username,password,identity,credit,companyName,email from user where username=?",username)
    result = cursor.fetchone()
    cursor.close()
    conn.close() 
    if not result:
            return 'wrong username', 400
    if result[1]==json['password']:
        user.username=result[0]
        user.identity=result[2]
        user.credit=result[3]
        user.companyName=result[4]
        user.email=result[5]
        response = {'message': f'You are logged in as {user.identity}'}
    else:
        return 'wrong password', 400
    return jsonify(response), 201
# notifying owner
@app.route('/get_all_notifications', methods = ['GET'])
def notify():
    notify_list=[]
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute(f"select * from notification where identity='{user.identity}'")
    for row in cursor.fetchall():
        notification=Notification()
        notification.set(row[0],row[1],row[2],row[3],row[4],row[5])
        notify_list.append(notification.get())
    cursor.close()
    conn.close()   
    response = {'notfications': notify_list}
    return jsonify(response), 200
# Adding a new admin
@app.route('/add_admin', methods = ['POST'])
def add_admin():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    contract_keys = ['username','password', 'identity']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    username=json['username']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into user([username],[password],[identity]) VALUES(?,?,?)",(username,json['password'],json['identity']))
    conn.commit()
    cursor.execute("insert into notification([notification],[timestamp],[identity],[username]) VALUES(?,?,?,?)",(f'admin: {username} is added.',datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.close()
    conn.close()
    response = {'message': f'admin: {username} is added.'}
    return jsonify(response), 201

#adding project
@app.route('/add_project', methods = ['POST'])
def add_project():
    json = request.get_json()
    contract_keys = ['project_name','address']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    project_name=json['project_name']
    project=Project()
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into project([project_name],[address]) VALUES(?,?)",(project_name,json['address']))
    conn.commit()
    cursor.execute("insert into notification([notification],[timestamp],[identity],[username]) VALUES(?,?,?,?)",(f'project: {project_name} is added.',datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from project where project_name=?",project_name)
    for row in cursor.fetchall():
        project.set(row[0],row[1],row[2])
    cursor.close()
    conn.close()
    index=blockchain.add_project(project.get())
    blockchain.add_description({'message': f'project: {project_name} is added'})
    response = {'message': f'project: {project_name} is added to block {index}'}
    return jsonify(response), 201
#adding user(contractor,owner,consultant)
@app.route('/add_user', methods = ['POST'])
def add_user():
    json = request.get_json()
    contract_keys = ['username','password', 'companyName','identity','email']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    username=json['username']
    identity=json['identity']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into user([username],[password],[companyName],[credit],[identity],[email]) VALUES(?,?,?,?,?,?)",(json['username'],json['password'],json['companyName'],0,json['identity'],json['email']))
    conn.commit()
    cursor.execute("insert into notification([notification],[timestamp],[identity],[username]) VALUES(?,?,?,?)",(f'contractor: {username} is added',datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.close()
    conn.close()
    index=blockchain.add_description({'message': f'{identity}: {username} is added'})
    response = {'message': f'contactor: {username} is added to block {index}.'}
    return jsonify(response), 201

@app.route('/status_update', methods = ['POST'])
def status_update():
    json = request.get_json()
    if user.identity!="contractor":
        return 'unauthorized party',400
    transaction_keys = ['activity_name','contract_name','status']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    activity=Activity()
    contract_name=json['contract_name']
    activity_name=json['activity_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("update activity  set status=? where activity_name=? and contract_name=?",(json['status'],json['activity_name'],json['contract_name']))
    conn.commit()
    cursor.execute("insert into notification([notification],[timestamp],[identity],[username]) VALUES(?,?,?,?)",(f'contractor updated status of activity: {activity_name} in contract: {contract_name}',datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]) 
    cursor.close()
    conn.close() 
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'contractor updated status of activity: {activity_name} in contract: {contract_name}'})
    response = {'message': f'contractor updated status of activity: {activity_name} in contract: {contract_name} to block {index}'}
    return jsonify(response), 201

#activity amount is paid out by owner
@app.route('/pay', methods = ['POST'])
def pay():
    json = request.get_json()
    transaction_keys = ['contract_name','activity_name','owner_username','contractor_username','retention']
    owner_username=json['owner_username']
    contract_name=json['contract_name']
    contractor_username=json['contractor_username']
    retention=json['retention']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    activity_name=json['activity_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select price from activity where activity_name=?",activity_name)
    amount=cursor.fetchone()
    print(amount[0])
    cursor.execute("select credit from user where username = ?",owner_username)
    credit=cursor.fetchone()
    cal=amount[0]-(amount[0]*retention/100)
    credit[0]=credit[0]-cal# retention
    cursor.execute("update user  set credit = 0 where username = ?",contractor_username)
    conn.commit()
    cursor.execute("update user  set credit = ? where username =? ",(credit[0],owner_username))
    conn.commit()
    cursor.execute("update user  set credit = ? where username = ? ",(cal,contractor_username))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",( f'contractor:{contractor_username} has received the activity amount {cal} of activity {activity_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.close()
    conn.close()
    index=blockchain.add_description({'message': f'contractor:{contractor_username} has received the activity amount of contract {activity_name}'})
    blockchain.add_user(user.username)
    response = {'message': f'contractor:{contractor_username} has received the activity amount {amount[0]} of contract {activity_name} to block {index}'}
    
    return jsonify(response), 201
 #contract amount is paid out by owner
@app.route('/paycontract', methods = ['POST'])
def paycontract():
     json = request.get_json()
     transaction_keys = ['contract_name','activity_name','owner_username','contractor_username','retention']
     owner_username=json['owner_username']
     contract_name=json['contract_name']
     contractor_username=json['contractor_username']
     retention=json['retention']
     if not all(key in json for key in transaction_keys):
         return 'Some elements of the transaction are missing', 400

     conn = pyodbc.connect(connection_string)
     conn.autocommit=True
     cursor = conn.cursor()
     cursor.execute("select amount from contract where contract_name=?",contract_name)
     amount=cursor.fetchone()
     cursor.execute("select credit from user where username = ?",owner_username)
     credit=cursor.fetchone()
     cal=amount[0]*(retention*0.01)
     print(cal)
     credit[0]=credit[0]-cal# retention
     cursor.execute("update user  set credit = 0 where username = ?",contractor_username)
     conn.commit()
     cursor.execute("update user  set credit = ? where username =? ",(credit[0],owner_username))
     conn.commit()
     cursor.execute("update user  set credit = ? where username = ? ",(cal,contractor_username))
     conn.commit()
    
     cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",( f'contractor:{contractor_username} has received the retention amount {cal} of contract {contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
     conn.commit()
     cursor.close()
     conn.close()
     index=blockchain.add_description({'message': f'contractor:{contractor_username} has received the retention amount of contract {contract_name}'})
     blockchain.add_user(user.username)
     response = {'message': f'contractor:{contractor_username} has received the retention amount {retention} of contract {contract_name} to block {index}'}
     return jsonify(response), 201   
 
#approving the contract by consultant
@app.route('/approve', methods = ['POST'])
def approve():
    json = request.get_json()
    transaction_keys = ['activity_name','contract_name','approved']
    activity=Activity()
    activity_name=json['activity_name']
    contract_name=json['contract_name']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing ', 400
    
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("update activity  set approved=? where activity_name=? and contract_name=?",(json['approved'],json['activity_name'],json['contract_name']))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Consultant name: {user.username} approved activity:{activity_name} in contract no.{contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]) 
    cursor.close()
    conn.close()  
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Consultant {user.username} approved activity:{activity_name} in contract: {contract_name} '})    
    response = {'message':f'Consultant {user.username} approved activity:{activity_name} in contract: {contract_name} to block {index}'}
    return jsonify(response), 201
#approving the contract by consultant
@app.route('/not_approve', methods = ['POST'])
def not_approve():
    json = request.get_json()
    transaction_keys = ['activity_name','contract_name','approved']
    activity=Activity()
    activity_name=json['activity_name']
    contract_name=json['contract_name']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing ', 400
    
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("update activity  set approved=? where activity_name=? and contract_name=?",(json['approved'],json['activity_name'],json['contract_name']))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Consultant name: {user.username} did not approve  activity:{activity_name} in contract no.{contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]) 
    cursor.close()
    conn.close()  
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Consultant {user.username} did not approved activity:{activity_name} in contract: {contract_name} '})    
    response = {'message':f'Consultant {user.username} did not approved activity:{activity_name} in contract: {contract_name} to block {index}'}
    return jsonify(response), 201
# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201



# Adding a new transaction to the Blockchain
@app.route('/add_contract', methods = ['POST'])
def add_contract():
    json = request.get_json()
    """if user.identity!="admin" or user.identity!="owner":
        return 'unauthorized party',400"""
    contract=Contract()
    penalty=0
    contract_keys = ['contract_no','contract_name','project','amount', 'date', 'type','parties','status','penalty']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    contract_name=json['contract_name']
    project_name=json['project']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into contract([contract_name],[project],[amount],[date],[type],[parties],[penalty],[status]) VALUES(?,?,?,?,?,?,?,?)",(contract_name,json['project'],json['amount'],json['date'] , json['type'],json['parties'],penalty,"active"))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Contract_name:{contract_name} is added to project: {project_name}.',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from contract where contract_name=?",contract_name)
    for row in cursor.fetchall():
        contract.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
    cursor.close()
    conn.close()
    index=blockchain.add_contract(contract.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'contract:{contract_name} is added to project: {project_name}'})
    response = {'message': f'contract:{contract_name} is added to project: {project_name} to block {index}'}
    return jsonify(response), 201
#updating contract
@app.route('/update_contract', methods = ['POST'])
def update_contract():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    if not json['contract_name']:
        return 'Project name is missing', 400
    contract=Contract()
    contract_name=json['contract_name']
    s=""  
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    if json['amount']:
        cursor.execute("update contract  set amount=? where contract_name=?",(json['amount'],contract_name))
        conn.commit()
        s+="amount"
        change=str(json['amount'])
    if json['date']:
        cursor.execute("update contract  set [date]=? where contract_name=?",(json['date'],contract_name))
        conn.commit()
        s+=str(',')+" date"
        change+=str(', ')+json['date']
    if json['Type']:
        cursor.execute("update contract  set type=? where contract_name=?",(json['Type'],contract_name))
        conn.commit()
        s+=str(',')+" Type"
        change+=str(', ')+str(json['Type'])
    if json['parties']:
        cursor.execute("update contract  set parties=? where contract_name=?",(json['parties'],contract_name))
        conn.commit()
        s+=str(',')+" parties"
        change+=str(',')+str(json['parties'])
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Contract_name:{contract_name} ({s}) is changed to ({change}).',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from contract where contract_name=?",contract_name)
    for row in cursor.fetchall():
        contract.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
    cursor.close()
    conn.close()
    index=blockchain.add_contract(contract.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Contract:contract_name ({s}) is changed to block to ({change})'})
    response = {'message': f'Contract:contract_name ({s}) is changed to block to ({change}) to block {index}.'}
    return jsonify(response), 201

#adding penalty
@app.route('/update_penalty', methods = ['POST'])
def update_penalty():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    contract_keys = ['contract_name','penalty']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    contract=Contract()
    contract_name=json['contract_name']
    penalty=json['penalty']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    if json['penalty']:
        cursor.execute("update contract  set penalty=? where contract_name=?",(json['penalty'],contract_name))
        conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'{penalty} penalty is added to contract:{contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from contract where contract_name=?",contract_name)
    for row in cursor.fetchall():
        contract.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
    cursor.close()
    conn.close()
    index=blockchain.add_contract(contract.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'{penalty} penalty is added to contract:{contract_name}'})
    response = {'message': f'{penalty} penalty  is added to contract:{contract_name} to block {index}'}
    return jsonify(response), 201
#adding delays
@app.route('/add_delay', methods = ['POST'])
def add_delay():
    t=Timer()
    t.start()
    json = request.get_json()
    if user.identity!="consultant":
        return 'unauthorized party',400
    transaction_keys = ['contract_name','activity_name','delays']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing ', 400
    activity=Activity()
    contract_name=json['contract_name']
    activity_name=json['activity_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("update activity  set delays=? where contract_name=?",(json['delays'],contract_name,activity_name))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Consultant has added delays to activity:{activity_name} and penalty to contract:{contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]) 
    cursor.close()
    conn.close()
    blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Consultant has added delays to activity:{activity_name} and penalty to contract:{contract_name}'})
    response = {'message': f'Consultant has added delays to activity:{activity_name} and penalty to contract:{contract_name}'}
    return jsonify(response), 201
#removing contract
@app.route('/remove_contract', methods = ['POST'])
def remove_contract():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    contract_keys = ['contract_name']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    contract=Contract()
    contract_name=json['contract_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("select * from contract where contract_name=?",contract_name)
    for row in cursor.fetchall():
        contract.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
    cursor.execute("delete from contract where contract_name=?",contract_name)
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'contract:{contract_name} is removed .',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.close()
    conn.close()
    index=blockchain.add_contract(contract.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'contract:{contract_name} is removed.'})
    response = {'message': f'contract:{contract_name} is removed to block {index}'}
    return jsonify(response), 201

# adding activity to contract
@app.route('/add_activity', methods = ['POST'])
def add_activity():
    t=Timer()
    t.start()
    json = request.get_json()
    act_keys = ['project', 'activity_name', 'duration','price','start_date','finish_date','status','approved','delays','contract_name']
    if not all(key in json for key in act_keys):
        return 'Some elements of the transaction are missing', 400
    contract_name=json['contract_name']
    activity_name=json['activity_name']
    activity=Activity()
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into activity([project],[activity_name],[duration],[price],[start_date],[finish_date],[status],[approved],[delays],[contract_name]) VALUES(?,?,?,?,?,?,?,?,?,?)",(json['project'],json['activity_name'] ,json['duration'],json['price'],json['start_date'],json['finish_date'],json['status'],json['approved'],json['delays'],contract_name))
    conn.commit()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",(f'Activity:{activity_name} is added to contract:{contract_name}',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
    cursor.close()
    conn.close()
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Activity: {activity_name} is added to contract: {contract_name}'})
    response = {'message': f'Activity: {activity_name} is added to contract: {contract_name} in block {index}'}
    time=t.stop("Time elapsed for query:")
    with open('Query.txt', 'a', encoding='utf-8') as f:
               f.write(str(time)+'\n')
    return jsonify(response), 201
#updating activity terms
@app.route('/update_activity', methods = ['POST'])
def update_activity():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    if not json['activity_name']:
        return 'Contract name is missing', 400
    if not json['contract_name']:
        return 'activity name is missing', 400
    contract_name=json['contract_name']
    activity_name=json['activity_name']
    activity=Activity()
    s=""
    change=''
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    if json['duration']:
        cursor.execute("update activity  set duration=? where contract_name=? and activity_name=?",(json['duration'],contract_name,activity_name))
        conn.commit()
        s+=" duration"
        change=str(json['duration'])
    if json['price']:
        cursor.execute("update activity  set price=? where contract_name=? and activity_name=?",(json['price'],contract_name,activity_name))
        conn.commit()
        s+=str(',')+" price"
        change=str(',')+str(json['price'])
    if json['start_date']:
        cursor.execute("update activity  set [start_date]=? where contract_name=? and activity_name=?",(json['start_date'],contract_name,activity_name))
        conn.commit()
        s+=str(',')+" start_date"
        change+=str(',')+json['start_date']
    if json['finish_date']:
        cursor.execute("update activity  set [finish_date]=? where contract_name=? and activity_name=?",(json['finish_date'],contract_name,activity_name))
        conn.commit()
        s+=str(',')+" finish_date"
        change+=str(',')+json['finish_date']
    
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",( f'Activity: {activity_name} in Contract:{contract_name}  ({s}) is changed to ({change}).',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
    cursor.close()
    conn.close()
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Activity: {activity_name} in Contract:{contract_name}  ({s}) is changed to ({change})'})
    response = {'message': f'Activity: {activity_name} in Contract:{contract_name}  ({s}) is changed to ({change}) to block {index}.'}
    return jsonify(response), 201  
#removing act
@app.route('/remove_activity', methods = ['POST'])
def remove_activity():
    json = request.get_json()
    if user.identity!="admin":
        return 'unauthorized party',400
    contract_keys = ['activity_name','contract_name']
    if not all(key in json for key in contract_keys):
        return 'Some elements of the transaction are missing', 400
    activity=Activity()
    contract_name=json['contract_name']
    activity_name=json['activity_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    
    cursor.execute("select * from activity where activity_name=? and contract_name=?",(activity_name,contract_name))
    for row in cursor.fetchall():
        activity.set(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
    cursor.execute("delete from activity where contract_name=? and activity_name=?",contract_name,activity_name)
    conn.commit()
    cursor.close()
    conn.close()
    index=blockchain.add_activity(activity.get())
    blockchain.add_user(user.username)
    blockchain.add_description({'message': f'Activity: {activity_name} is removed from contract: {contract_name}'})
    response = {'message': f'Activity:{activity_name} is removed from contract: {contract_name} to block {index}.'}
    return jsonify(response), 201
# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Unicoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201
# claim request
@app.route('/claim', methods = ['POST'])
def claim():
    json = request.get_json()
    if not json['claim']:
         return 'Claim is missing', 400
    contract_name=json['contract_name']
    conn = pyodbc.connect(connection_string)
    conn.autocommit=True
    cursor = conn.cursor()
    cursor.execute("insert into notification([notification],[contract_name],[timestamp],[identity],[username]) VALUES(?,?,?,?,?)",( f'Claim has been sent by contractor:{user.username} for contract:{contract_name}).',contract_name,datetime.datetime.now(),user.identity,user.username))
    conn.commit()
    cursor.execute("insert into claim([claim],[status],[username],[timestamp]) VALUES(?,?,?,?)",(json['claim'],"sent",user.username,datetime.datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    blockchain.add_user(user.username)
    index=blockchain.add_description({'message': f'Claim has been sent by contractor:{user.username}'})
    response = {'message': f'Claim has been added by contractor:{user.username} to block {index}.'}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    response=None
    network = blockchain.nodes
    longest_chain = None
    max_length = len(blockchain.chain)
    is_chain_replaced=None
    for node in network:
            response0 = requests.get(f'http://{node}/get_chain')
            if response0.status_code == 200:
                length = response0.json()['length']
                chain = response0.json()['chain']
                if length >max_length and blockchain.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
    if longest_chain:
     is_chain_replaced=blockchain.replace_chain( longest_chain)
           
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
        
        
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5001)

