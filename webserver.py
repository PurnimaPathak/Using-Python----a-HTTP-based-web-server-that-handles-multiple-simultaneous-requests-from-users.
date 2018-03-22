#!/usr/bin/python

import socket  # Networking support
import signal  # Signal support (server shutdown on signal receive)
import time  # Current time
import os.path
import sys
import threading
import logging

logging.basicConfig(filename='example.log', level=logging.INFO)


def _gen_headers(code):
    """ Generates HTTP response Headers. Ommits the first line! """

    # determine response code
    h = ''
    if (code == 200):
        h = 'HTTP/1.1 200 OK\n'
    elif (code == 404):
        h = 'HTTP/1.1 404 Not Found\n'
    elif (code == 400):
        h = 'HTTP/1.1 400 Bad Request\n'
    elif (code == 500):
        h = 'HTTP/1.1 500 Internal Server Error\n'
    elif (code == 501):
        h = 'HTTP/1.1 501 Not Implemented\n'

    # write further headers
    current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    h += 'Date: ' + current_date + '\n'
    h += 'Server: Simple-Python-HTTP-Server\n'
    h += 'Connection: Keep-Alive\n\n'  # signal that the conection wil be closed after complting the request

    return h


class Server:
    """ Class describing a simple HTTP server objects."""

    def __init__(self, port=80):
        """ Constructor """
        self.host = ''  # <-- works on all available network interfaces
        self.threads = []
        if os.path.exists("/Users/purnima/Downloads/PA2/ws.conf"):
            configuration = open("/Users/purnima/Downloads/PA2/ws.conf")
            config_lists = configuration.readlines()
        else:
            sys.exit("Expected ws.conf not found")
        self.document_root_directory = None
        self.port = None
        self.default_page = None
        self.content_extension_list = []
        self.content_type_info = {}
        self.connection_timeout = None
        if os.path.exists("/Users/purnima/PycharmProjects/ITP/Final_PA2"):
            configuration = open("/Users/purnima/PycharmProjects/ITP/Final_PA2/ws.conf")
            self.read_conf(configuration)
        else:
            sys.exit("Expected ws.conf not found")

    def read_conf(self, configuration):
        config_lists = configuration.readlines()
        for line in config_lists:
            if "ListenPort" in line.split():
                self.port = line.split()[1]
                if 1024 >= int(self.port) > 65536:
                    sys.exit("Port number must be greater than 1024 and less than 65536")
            if "DocumentRoot" in line.split():
                self.document_root_directory = line.split()[1]
                if self.document_root_directory == "":
                    sys.exit("Document Root Directory not set")
            if "DirectoryIndex" in line.split():
                self.default_page = line.split()[1]
                if self.default_page == "":
                    sys.exit("Default page not set")
            if "ContentType" in line.split():
                self.content_extension_list.append(line.split()[1])
            if "ContentType" in line.split():
                self.content_type_info[line.split()[1]] = line.split()[2]
            if "KeepaliveTime" in line.split():
                self.connection_timeout = line.split()[1]

    def activate_server(self):
        """ Attempts to aquire the socket and launch the server """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:  # user provided in the __init__() port may be unavaivable
            logging.info("Launching HTTP server on %s" % self.host)
            self.socket.bind((self.host, self.port))

        except Exception as e:
            logging.info("Warning: Could not aquire port:%s" % self.port)
            logging.info("I will try a higher port")
            # store to user provided port locally for later (in case 8080 fails)
            user_port = self.port
            self.port = 8080

            try:
                logging.info("Launching HTTP server on %s" % self.host)
                self.socket.bind((self.host, self.port))

            except Exception as e:
                logging.info("ERROR: Failed to acquire sockets for ports %s" % user_port)
                logging.info("Try running the Server in a privileged user mode.")
                self.shutdown()
                import sys
                sys.exit(1)

        logging.info("Server successfully acquired the socket with port: %s" % self.port)
        logging.info("Press Ctrl+C to shut down the server and exit.")
        self._wait_for_connections()


    def shutdown(self):
        """ Shut down the server """
        try:
            logging.info("Shutting down the server")
            s.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            logging.info("Warning: could not shut down the socket. Maybe it was already closed?%s" % e)


    def _wait_for_connections(self):
        """ Main loop awaiting connections """
        while True:
            logging.info("Awaiting New connection")
            self.socket.listen(3)  # maximum number of queued connections

            conn, addr = self.socket.accept()
            if conn:
                thr_multiple = Multiple(conn, addr, self.document_root_directory, self.content_extension_list)
                thr_multiple.start()

                self.threads.append(thr_multiple)
            for elements in self.threads:
                elements.join()


def graceful_shutdown(sig, dummy):
    """ This function shuts down the server. It's triggered
    by SIGINT signal """
    s.shutdown()  # shut down the server
    import sys
    sys.exit(1)


class Multiple(threading.Thread):
    def __init__(self, conn, addr, document_root_directory, content_extension_list):
        self.conn = conn
        self.addr = addr
        self.document_root_directory = document_root_directory
        self.content_extension_list = content_extension_list
        threading.Thread.__init__(self)
        print("new thread created")

    def run(self):
        data = self.conn.recv(1024)  # receive data from client
        string = bytes.decode(data)  # decode it to string

        # determine request method  (HEAD and GET are supported)
        request_method = string.split(' ')[0]
        logging.info("Method: %s" % request_method)
        logging.info("Request body:%s" % string)

        # if string[0:3] == 'GET':
        if request_method == 'GET':
            # file_requested = string[4:]

            # split on space "GET /file.html" -into-> ('GET','file.html',...)
            file_requested = string.split(' ')
            file_requested = file_requested[1]  # get 2nd element

            # File extension check
            ext = file_requested.split(".")[-1]
            if ext == "download":
                ext = file_requested.split(".")[-2:-1]
                ext = ".".join(ext)
            else:
                ext = "." + ext
            if ext not in self.content_extension_list:
                response_headers = _gen_headers(501)
                server_response = response_headers.encode()
                self.conn.send(server_response)
                self.conn.close()

            else:
                # Check for URL arguments. Disregard them
                file_requested = file_requested.split('?')[0]  # disregard anything after '?'

                if file_requested == '/':  # in case no file is specified by the browser
                    file_requested = '/index.html'  # load index.html by default

                file_requested = self.document_root_directory + file_requested
                logging.info("Serving web page %s" % file_requested)

                ## Load file content
                try:
                    file_handler = open(file_requested, 'rb')
                    if request_method == 'GET':  # only read the file when GET
                        response_content = file_handler.read()  # read file content
                    file_handler.close()

                    response_headers = _gen_headers(200)

                except Exception as e:  # in case file was not found, generate 404 page
                    logging.info("Warning, file not found. Serving response code 404\n %s" % e)
                    response_headers = _gen_headers(404)

                    if request_method == 'GET':
                        response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                server_response = response_headers.encode()  # return headers for GET and HEAD
                if request_method == 'GET':
                    server_response += response_content  # return additional content for GET only

                self.conn.send(server_response)
                logging.info("Closing connection with client")
                self.conn.close()

        else:
            response_headers = _gen_headers(400)
            server_response = response_headers.encode()
            self.conn.send(server_response)
            logging.info("Closing connection with client")
            self.conn.close()


###########################################################
# shut down server on ctrl+c
signal.signal(signal.SIGINT, graceful_shutdown)

logging.info("Starting web server")
s = Server(80)  # construct server object
s.activate_server()  # aquire the socket
