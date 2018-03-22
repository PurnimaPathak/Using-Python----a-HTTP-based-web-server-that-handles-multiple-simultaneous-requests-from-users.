import threading
import os
import datetime

'''
The class Server does the following:
1) Open the socket
2)binds the socket
3)listens, which tells the socket library that we want it to queue up as many as 5 connect requests
4) accept request
5)Start a thread for executing the request
6)Recv the request that the browser (client) sends
7) serves the Request
8) closes the connection


'''


class Client():
    def __init__(self):
        self.host = ''
        self.port = 8080
        self.threads = []
        self.send_req()

    def send_req(self):
        counter = 1
        while counter <= 100:
            thr_multiple = Multiple(counter, self.port)
            thr_multiple.start()
            thr_multiple.setName("thread" + str(counter))
            print(thr_multiple.getName())
            self.threads.append(thr_multiple)
            counter = counter + 1

            for elements in self.threads:
                elements.join()


class Multiple(threading.Thread):
    def __init__(self, count, port):
        threading.Thread.__init__(self)
        self.count = count
        self.port = port

    def run(self):
        # same file
        start_time = datetime.datetime.now()
        print("Thread started at " + str(start_time))
        command = "curl http://localhost:{0}/".format(self.port)
        os.system(command)
        end_time = datetime.datetime.now()
        print("Thread ended at " + str(end_time))
        print("Time taken by thread to execute " + str(end_time - start_time))

        # 100 req to different files
        os.system(("curl http://localhost:{0}/index{1}.html".format(self.port, self.count)))

        # 100 req to same files
        os.system(("curl http://localhost:{0}/index.html".format(self.port)))


'''
Things you might need to do in the PA:
1) Handle HTTP Error codes
2) Demonize threads to improve performance or implement timeout and return logic. 
3) Read the PA for more information
'''

if __name__ == '__main__':
    server = Client()
