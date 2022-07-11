
from multiprocessing.spawn import import_main_path
from gns3fy import *
from tabulate import tabulate
from os import system
from time import sleep
import datetime
import argparse
import socket
import telnetlib























#FUNCTIONS
    #run command
def run(c,s):
    s.send(c.encode("ascii"))
    return s.recvmsg(10000)

    #ROUTER'S
def Router_s(_nodes):
    Router=[]
    for node in _nodes:
        if 'dynamips' in node.node_type:
            Router.append({"name":node.name,"id":node.node_id,"port":node.console})
            print(node.console)
    return Router

    #CONTAINER'S // alpine
def CONTAINER_s(_nodes):
    alpine=[]
    for node in _nodes:
        if 'docker' in node.node_type:
            alpine.append({"name":node.name,"id":node.node_id,"port":node.console})
    print(alpine)
    return alpine
    #create linke between alpine and router and router's 
def link_creator(_nodes,lab,server):
    Router=Router_s(_nodes)
    Container_s=CONTAINER_s(_nodes)
    nodes=[]
    for i in range(2):
        node=[dict(node_id=Router[i]["id"], adapter_number=0, port_number=0),dict(node_id=Container_s[i]["id"], adapter_number=0, port_number=0)]
        nodes.append(node)
    
    
    nodes.append([dict(node_id=Router[0]["id"], adapter_number=0, port_number=1),dict(node_id=Router[1]["id"], adapter_number=0, port_number=1)])
    links=[]
    for node in nodes:
        link = Link(project_id=lab.project_id, connector=server, nodes=node)
        link.create()
        link.get()
        links.append(link)
    return links


    #start all node's
def nodes_starter(nodes):
    for node in nodes:
        node.start()
    
    #this function config all router's with connection (socket) and run seved config file in path
def router_config(socket,path):#socket = opened telnet connection and path = the path of config file
    file=open(path)
    lines=file.readlines()
    i=0
    data=run("\n\r",socket)
    while ">" not in str(data) and "#" not in str(data):
        data=run("\n\r",socket)
    for line in lines:
        data=run(line+"\n\r",socket)
        sleep(3)
    run("\n\r",socket)


    
    data=run("show ip route\n\r",socket)
    print(str(data))

    return True


    #set ip
def set_ip(HOST,port,ips,getway,netmask):
        for i in range(len(ips)):
                s=socket.socket()
                s.connect((HOST,port[i]))
                while True:
                        #set ip
                        command="ifconfig eth0 "+ips[i]+" netmask "+netmask[i]+" \r\n"
                        data=run(command,s)
                        if str(data)!= "b''":
                            print("[ERROR] ip {} cann't set".format(ips[i]))
                           
                        
                        command="route add default gw "+getway[i]+" eth0 \r\n"
                        data=run(command,s)
                        if str(data)!= "b''":
                            print("[ERROR] ip {} cann't set".format(ips[i]))
                        command="ifconfig \r\n"
                        data=run(command,s)    
                        if ips[i] in str(data):
                            break
        return True    










#-------------------main-------------------#
#clear screen
#system("clear")



#if you wanna run script with own config uncomment next line
"""
parser = argparse.ArgumentParser(description="A program for Routing Information Protocol 'RIP' ")
parser.add_argument("-H","--host",required=True,help="IP of host U wanna to be connect")
parser.add_argument("-P","--port",required=True,help="port of host U wanna to be connect")
parser.add_argument("-pname","--project_name",required=False,default="New_project",help="The Name of the project on which you want the script to run")
parser.add_argument("-user","--username",required=False,help="Fill in this field if your server is authenticated 'username'")
parser.add_argument("-pass","--password",required=False,help="Fill in this field if your server is authenticated 'password'")
parser.add_argument("-V","--vpc",required=False,nargs=2,help="VPC IP")
parser.add_argument("-R","--router",required=False,nargs=2,help="Router IP")
args = parser.parse_args()
host="http://"+args.host
port=args.port
username=args.username
password=args.password
url=host+":"+port
selected_project_name=args.project_name
"""




#connection information 

host="http://192.168.50.13"
host="http://127.0.0.1"
port="3080"
username="rezaei_h"

password="gns3_sec_test"
url=host+":"+port
selected_project_name="test"


#Connection
try:
    server = Gns3Connector(url=url,user=username,cred=password)
    server_version=server.get_version()['version']
except:
    print("[ERROR]Connection error failed")
    exit()

print(
       tabulate(server.projects_summary(is_print=False)
       ,headers=[
           "Project Name",
           "Project ID",
           "Total Nodes",
           "Total Links",
           "Status"],
           )
           )
projects_name = tuple(str(pn[0]) for pn in server.projects_summary(is_print=False))
projects_id = tuple(str(pn[1]) for pn in server.projects_summary(is_print=False))

project_name=selected_project_name
i=0

#while(project_name in projects_name):
#        project_name=selected_project_name+str(i)
#        i+=1
if(project_name in projects_name):
    print("There is a project with same name...")
    choise=input("Delete project[Y/n]?")
    while(choise not in "YyNn" and choise!=""):
        choise=input("[WRONG]Wrong input\nDelete project[Y/n]?")
    if(choise in "Yy" or choise==""):
        server.delete_project(server.get_project(name=project_name)["project_id"])
        server.create_project(name=project_name)
else:
    server.create_project(name=project_name)



lab=server.get_project(name=project_name)
pid=lab["project_id"]
lab=Project(name=project_name,project_id=pid ,connector=server)
lab.open()
lab.get()
lab.update()






for i in range(2):
    #Add alpine node
    pc=Node(name="alpine-"+str(i+1),template="alpine",project_id=pid,connector=server,x=250*((-1)**i),y=200)
    pc.create()
    pc.get()
    #Add router node 
    router=Node(name="R"+str(i+1),template="c3600",project_id=pid,connector=server,x=150*((-1)**i),y=100,)
    router.create()
    router.get()


lab.close()
lab.open()
lab.get()

nodes=lab.nodes


nodes_starter(nodes)



link_creator(nodes,lab,server)
#set_ip(nodes)


lab.close()


#close all project's
exit()






























































































HOST="192.168.50.13"
ports=[2021,2024]#2021 R3 port and 2024 R1 port
paths=("./confR3.txt","./confR1.txt")
for i in range(len(ports)):
    s=socket.socket()
    s.connect((HOST,ports[i]))
    router_config(s,paths[i])




#MAIN



HOST = "192.168.50.13"
ports=[2009,2011]
ips=["192.168.100.30/24","192.168.1.40/16"]
getway=["192.168.100.3","192.168.1.1"]
print(set_ip(HOST,ports,ips,getway))