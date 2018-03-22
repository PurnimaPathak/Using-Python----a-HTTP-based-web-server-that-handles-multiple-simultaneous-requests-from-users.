#open a new file to write logs
import os
import socket
import time
staticGlobalCnt=0
def pandwrite(message,fh):
    print(message)
    fh.write(message+"\n")

def t1(fh):
    while True:
        try:
            name = input("Enter name of ws.conf file correctly: ")
            os.rename(name, "replaced.txt")
            pandwrite("Renamed the file with replaced.txt",fh)
            pandwrite ("--> RUN the server",fh)
            while True:
                result=input("Any errors? yes/no : ")
                if result.lower()=="no":
                    pandwrite("Test passed",fh)
                    pandwrite("Renaming file back to name",fh)
                    os.replace("replaced.txt",name)
                    return 5,name
                elif result.lower()=="yes":
                    pandwrite("test failed",fh)
                    comment=input("Additional comments?")
                    pandwrite("comments: "+str(comment),fh)
                    pandwrite("Renaming file back to name", fh)
                    os.replace("replaced.txt", name)
                    return 0,name
                else:
                    print("please enter 'yes' or 'no' ")
                    continue
        except:
            print ("Incorrect file, Try again")
            continue
        break
def writer(name,message,all):
    fh2 = open(name, 'w')
    for ele in all:
        if "DirectoryIndex" in ele:
            fh2.write(message+"\n")
        else:
            fh2.write(ele)
    fh2.close()
def sender(host,port):
    k=input("Start the server! type yes to continue: ")
    data=""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    request = "GET / HTTP/1.1\nHost: localhost\nConnection: keep-alive\n"
    sock.send(request.encode())
    data = sock.recv(65535)
    sock.close()
    data = data.decode()
    return data
def finish_t2(name):
    fh3=open("temp.conf.txt",'r')
    datas=fh3.readlines()
    fh3.close()
    fh3=open(name,'w')
    for ele in datas:
        fh3.write(ele)
    fh3.close()

def t2(fh,name):
    pandwrite("\n\n Testcase 2 :Checking if default index.html is served incase files are moved ! ",fh)
    print("start the server")
    host=input("Enter ip/host: ")
    port=input("Enter port: ")
    pandwrite("Creating three files d1_i.html",fh)
    folder=input("Enter folder to store the index files in: ")
    for ele in range(1,2):
        fh2=open(folder+"\d1_"+str(ele)+".html",'w')
        fh2.write("This is "+str(ele))
        fh2.close()
    g=input("Stop the server! Done? provide input to continue")
    fh2 = open(name, 'r')#OPEN WS.conf
    all = fh2.readlines()
    fh2.close()
    fh2=open("temp.conf.txt","w")
    for ele in all:
        fh2.write(ele)
    fh2.close()
    writer(name,"DirectoryIndex d1_1.html d1_2.html",all)
    data=sender(host,int(port))
    if data:
        if "This is 1" in data:
            pandwrite("Part one success! Closing the server")
            inputs=input("Press key to continue: Close the server")
            writer(name, "DirectoryIndex d1_2.html ",all)
            data=sender(host,port)
            if data:
                if "This is 2" in data:
                    pandwrite("Part two success! Closing the server",fh)
                    inputs = input("Press key to continue: Close the server")
                    pandwrite("TEST CASE PASSED: Grade 6/6",fh)
                    finish_t2(name)
                    return 6
                else:
                    pandwrite("\nOUTPUT: \n",fh)
                    pandwrite(data,fh)
                    pandwrite("TEST CASE FAILED in calling dl_2.html: Grade 3/6", fh)
                    finish_t2(name)
                    return 3

        else:
            pandwrite("TEST CASE FAILED in first attempt: Grade 0/2",fh)
            pandwrite("\nOUTPUT: \n", fh)
            pandwrite(data,fh)
            print("Try using browser. Call for http://127.0.0.1:port/ ")
            k=input("Additional comments? : ")
            pandwrite("Comments: "+str(k),fh)
            finish_t2(name)
            return 0

def connectSocket():
    k=input("-->Run the server! Press key to continue: ")
    host="127.0.0.1"
    port=input("Enter port number: ")
    port=int(port)

    sockFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockFd.setblocking(0)
    sockFd.settimeout(10)
    sockFd.connect((host, port))
    return sockFd

def prepareMsg(firstWord, reqWord, thirdWord, keepAlive,two = False):
    msgToSend = firstWord + " " + reqWord + " " + thirdWord + "\r\n"
    if keepAlive == True:
        msgToSend += "Connection: keep-alive" + "\r\n"
    elif keepAlive=="None":
        msgToSend=msgToSend+"\r\n"
    else:
        msgToSend += "Connection: close" + "\r\n"
    msgToSend += "\r\n"
    if two == True:
        msgToSend += msgToSend
    msgToSend = msgToSend.encode()
    return msgToSend

def sendandget(p2sSockFd,msgToSend,two = False):
    global staticGlobalCnt
    staticGlobalCnt += 1
    print ("Iter: " + str(staticGlobalCnt))
    print (msgToSend)
    p2sSockFd.sendall(msgToSend)
    totalDataToReply = bytearray()
    if two == False:
        while True:
            try:
                dataRead = p2sSockFd.recv(1024000)
                if not dataRead:
                    print("No data received from actual server")
                    break
                else:
                    totalDataToReply += dataRead
            except:
                break

        pandwrite ("Reply: " + str(staticGlobalCnt),fh)
        totalDataToReply = totalDataToReply.decode()
        pandwrite(totalDataToReply[:250],fh)
        return totalDataToReply
    else:
        try:
            print("Two:")
            dataRead = p2sSockFd.recv(1024000)
            dataRead=dataRead.decode()
            
            cnt = dataRead.split("HTTP/1.1 200 OK")

            pandwrite("Count: " + str(len(cnt)),fh)
            pandwrite(dataRead[:250],fh)
            return dataRead,cnt
        except:
            pass
    print ("\n")

def t3(fh):
    sock1=connectSocket()
    msg1 = prepareMsg("GET", "/", "HTTP/1.2", True)
    pandwrite("\n REQUEST: \n"+str(msg1)+"\n",fh)
    totaldata=sendandget(sock1,msg1)
    sock1.close()
    if "400" in totaldata:
        pandwrite("Test case passed: 4/4",fh)
        return 4
    else:
        pandwrite("Test case failed: 0/4",fh)
        k=input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0
def t4(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GETTA", "/", "HTTP/1.1", True)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if "400" in totaldata:
        pandwrite("Test case passed: 2/2", fh)
        return 2
    else:
        pandwrite("Test case failed: 0/2", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0
def t5(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GET", "/fac ebo#ok.com", "HTTP/1.1", True)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if "400" in totaldata:
        pandwrite("Test case passed: 4/4", fh)
        return 4
    else:
        pandwrite("Test case failed: 0/4", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0

def t6(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GET", "/sadpa.html", "HTTP/1.1", True)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if "404" in totaldata:
        pandwrite("Test case passed: 4/4", fh)
        return 4
    else:
        pandwrite("Test case failed: 0/4", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0

def t7(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("UPDATE", "index.html", "HTTP/1.1", True)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if "501" in totaldata or "500" in totaldata:
        pandwrite("Test case passed: 4/4", fh)
        return 4
    else:
        pandwrite("Test case failed: 0/4", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0


def t8(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GET", "/index.html", "HTTP/1.1", False)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if "close" in totaldata or "Close" in totaldata or "CLOSE" in totaldata:
        pandwrite("Test case passed: 5/5", fh)
        return 5
    else:
        pandwrite("Test case failed: 0/5", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0

def t9(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GET", "/index.html", "HTTP/1.1", True, True)
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata,count = sendandget(sock1, msg1,True)
    sock1.close()
    points=0
    if totaldata:
        if count=="2":
            pandwrite("Test case passed (Pipelining): +8", fh)
            points=points+8
        if "keep" in totaldata or "Keep" in totaldata or "KEEP" in totaldata:
            pandwrite("Test case passed (Keep-Alive header): +4", fh)
            points=points+4
        else:
            pandwrite("Test case failed: 0/12", fh)
            k = input("Additional comments?: ")
            pandwrite("Comments: " + str(k), fh)
            return 0
        return points
    else:
        pandwrite("Test case failed: 0/12", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0

def t10(fh):
    pandwrite("Creating 3 new sockets...\n",fh)
    sock1 = connectSocket()
    sock2 = connectSocket()
    msg1 = prepareMsg("GET", "/index.html", "HTTP/1.1", True)
    pandwrite("sending request to sock1...\n ",fh)
    sendandget(sock1, msg1)
    pandwrite("waiting 3 seconds...",fh)
    time.sleep(3)
    print("sending sock2 req...")
    sendandget(sock2, msg1)
    pandwrite("ReSending request using socket 1",fh)
    sendandget(sock1, msg1)
    k=input("Check number of Threads: There should be two threads: one should serve one request and the second should server 2 requests: Press key to continue \n")
    score=input("Testcase passed? Enter grade out of 10: ")
    score=int(score)
    pandwrite("Closing socket 2 ",fh)
    sock2.close()
    pandwrite("sleeping 15 seconds...",fh)
    time.sleep(15)
    pandwrite("resending sock1 req...",fh)
    try:
        sendandget(sock1,msg1)
        k=0
    except:
        pandwrite("TEST CASE PASSED : 5/5",fh)
        k=5
    score=score+int(k)
    return score

def t11(fh):
    sock1 = connectSocket()
    msg1 = prepareMsg("GET", "/index.html", "HTTP/1.1", "None")
    pandwrite("\n REQUEST: \n" + str(msg1) + "\n", fh)
    totaldata = sendandget(sock1, msg1)
    sock1.close()
    if totaldata:
        if "close" in totaldata or "Close" in totaldata or "CLOSE" in totaldata:
            pandwrite("Test case passed: 5/5", fh)
            return 5
        else:
            pandwrite("Test case failed: 0/5", fh)
            k = input("Additional comments?: ")
            pandwrite("Comments: " + str(k), fh)
            return 0
    else:
        pandwrite("Test case failed: 0/5", fh)
        k = input("Additional comments?: ")
        pandwrite("Comments: " + str(k), fh)
        return 0




fh=open("logfiles.txt",'w')
pandwrite("Test case 1: Checking if server works without ws.conf",fh)
r1,name=t1(fh)
#r2=t2(fh,name)
pandwrite("\n\n Test case 3: Sending bad http version request\n Expected response: Error 400\n",fh)
r3=t3(fh)
pandwrite("\n\n Test case 4: Sending bad http method request\n Expected response: Error 400\n",fh)
r4=t4(fh)
pandwrite("\n\n Test case 5: Sending invalid url request\n Expected response: Error 400\n",fh)
r5=t5(fh)
pandwrite("\n\n Test case 6: Sending wrong page\n Expected response: Error 404 file not found\n",fh)
r6=t6(fh)
pandwrite("\n\n Test case 7: Improper Request\n Expected response: Error 501 or 500 \n",fh)
r7=t7(fh)
pandwrite("\n\n Test case 8: Sending connection close request\n Expected response: Header should have Connection:close \n",fh)
r8=t8(fh)
pandwrite("\n\n Test case 9: Pipelining (2 Requests) and Keepalive\n Expected response: Should have 4 responses and keep alive in header \n",fh)
r9=t9(fh)
pandwrite("\n\n Test case 10: Testing Multi-threading\n Expected response: There should be two threads \n",fh)
r10=t10(fh)

pandwrite("\n\n Test case 11: Sending request without Connection in header\n Expected response: There should Connection: close in header \n",fh)
r11=t11(fh)

pandwrite("TOTAL SCORE: ",fh)
sums=[r1,r3,r4,r5,r6,r6,r8,r9,r10,r11]
pandwrite(str(sums),fh)
total=sum(sums)
pandwrite("TOTAL: "+str(total),fh)



