#!/usr/bin/python
#Import libraries
import socket
import sys
import re
from bs4 import BeautifulSoup

#Global variable declaration
index = 0
sys.setrecursionlimit(50000)
visitedlist = ['/fakebook/']
linktobevisited = []
z = []
url = "cs5700sp16.ccs.neu.edu/fakebook/"
port = 80
username = sys.argv[1]
password = sys.argv[2]

#Create TCP socket and connect the client to the server
mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "cs5700sp16.ccs.neu.edu"
mysock.connect((host, port))

# Send GET request with the given URL and receive its response
mysock.send('GET /accounts/login/?next=/fakebook/ HTTP/1.0\r\n\r\n')
data1 = mysock.recv(1000000)

status = data1.split()

#Collect the crsftoken and session-id token 
x = status[27] + ' '+ status[35].replace(';','')

#Create header for POST request
header = '''\
POST /accounts/login/ HTTP/1.1\r
Host: cs5700sp16.ccs.neu.edu\r'''
Cook = 'Cookie: ' + x
middletoken = status[27].replace(';','')
middlewaretoken = middletoken.replace('csrftoken=','')
headerpart2 = '''\
Content-Type: application/x-www-form-urlencoded\r
Content-Length: 109\r
Connection: keep-alive\r\r\n'''

body = 'username='+username+'&password='+password+'&csrfmiddlewaretoken=' + middlewaretoken + '&next=%2Ffakebook%2F'
originalpost = "\n".join([header, Cook, headerpart2, body])

#Created new socket to send POST request and receive its response
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect((host, 80))
s1.send(originalpost)
data2 = s1.recv(1000000)

if("HTTP/1.1 302 FOUND" not in data2):
  print "Login failed. Please enter the right credentials"
  sys.exit()

notfound = data2.split()

# Send GET headers to fetch fakebook page
getheader1 = '''\
GET /fakebook/ HTTP/1.1\r
Host: cs5700sp16.ccs.neu.edu\r
Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r
'''

# Extracted csrftoken and session-id from the POST response header 
Cook2 = 'Cookie: ' + status[27] + ' '+ notfound[27].replace(';','')
getheader2 = 'Connection: keep-alive\r\n\r\n'
getheader = getheader1 + Cook2 + '\r' + getheader2

#Send the GET request and receive the homepage of fakebook
s1.send(getheader)
fakebookdata = s1.recv(1000000)

#Function will print the secret flags when encountered in the receive data 
def secretflagsearch(recvdata):
  global z

  if 'secret_flag' in recvdata:
    for index in range(0,1):
      print re.findall(r'[0-9a-z]{64}', recvdata)[0]
      secretdata = re.findall(r'[0-9a-z]{64}', recvdata)[0]
      if secretdata not in z:
        z.append(secretdata)
      if len(z) == 5:
        sys.exit(1)


#Function will create a GET request header for all the links to be traversed
def GET(data):
  headersoup1 = 'GET ' + data + ' HTTP/1.1\r\n'
  headersoup2 = 'Host: cs5700sp16.ccs.neu.edu\r\n'
  headersoup3 = 'Referer: http://cs5700sp16.ccs.neu.edu/fakebook/\r\n'
  headersoup = headersoup1 + headersoup2 + Cook2 + '\r\n\r\n'
  return headersoup


#The function will send and receive the GET requests and responses over newly created TCP sockets and check the status code in the response header and handle errors
def send_GET(data, url):
  global visitedlist
  s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s1.connect((host, 80))
  s1.send(data)
  recvdata = s1.recv(10000)
  if "HTTP/1.1 200 OK" in recvdata and "Connection: close" not in recvdata:
    visitedlist.append(url)
    return recvdata
  if "HTTP/1.1 302 FOUND" in recvdata and "Connection: close" not in recvdata:
    visitedlist.append(url)
    return recvdata
  elif "HTTP/1.1 500 INTERNAL SERVER ERROR" in recvdata:
    send_GET(GET(url), url)
  elif "HTTP/1.1 403 Forbidden" in recvdata or "HTTP/1.1 404 Not Found" in recvdata:
    visitedlist.append(url)
    recvdata = ""
  else:
    send_GET(data, url)
  return recvdata


#The function will parse the html page using BeautifulSoup library and extract the necessary links from the page for traversal
def collect_links(data):
  links = []
  soup = BeautifulSoup(data, 'html.parser')
  for link in soup.find_all("a", href = True):
    if(link.get('href') not in visitedlist and '/fakebook/' in link.get('href')):
      links.append(link.get('href'))
  return links


#The function will apply GET requests on links which are not traversed and check their responses for secret flags 
def processor(links):
  for link in links:
    headers = GET(link)
    html = send_GET(headers, link)
    secretflagsearch(html)
    processor(collect_links(html))
  

#Call function to collect links from the homepage and begin the process of crawling
processor(collect_links(fakebookdata))