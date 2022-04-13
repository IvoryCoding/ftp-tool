#   Date:        2022/04/04
#   Author:      Emma Gillespie
#   Description: Connects to an FTP server and uploads files to the server
#   Resources:   https://docs.python.org/3/library/ftplib.html
#                

#!/usr/bin/python3

import ftplib
import sys
import os
import re

# Take the file to upload files from

#Function for add
def addSSH(conName, username, password, ip):
    #Write/append to sshconnections.txt file
    file_object = open('ftp_connections.txt', 'a')
    file_object.write(f'{conName}:{username}:{password}:{ip}\n')
    file_object.close()
    print('*'*80)
    print(f"\nConnection was added. You can now connect to {conName}, using the -con argument\n")
    print('*'*80)

#Function for reading the connection file. Returns a dictionary of all lines found
def readConnections():
    connectDict = {}
    fileOBJ = open('ftp_connections.txt', 'r')
    for line in fileOBJ:
        temp = line.split(":")
        connectDict[temp[0]] = [temp[1], temp[2], temp[3].rstrip("\n")]
    fileOBJ.close()
    return connectDict

#Function for removing saved ssh connections and saves/overwrites file
def removeSSH(conName):
    #Displays the connection data to remove and asks if they are sure they want to remove it
    connections = readConnections()
    del connections[conName]
    
    file_object = open('ftp_connections.txt', 'w')
    for key in connections:
        file_object.write(f'{key}:{connections[key][0]}:{connections[key][1]}:{connections[key][2]}\n')
    file_object.close()

    print('*'*80)
    print(f"\n{conName} connection was removed. You can list connections using -list argument.\n")
    print('*'*80)

#Function for listing the ftp connections
def listSSH():
    connections = readConnections()

    print('*'*80, '\n')
    for key in connections:
        print(f'\t{key}:{connections[key][0]}:{connections[key][1]}:{connections[key][2]}\n')
    print('*'*80)

# Parses chosen folder and gets all files and paths
def folderParse(folder):
    filePaths = []

    for r, d, f in os.walk(folder):
        for file in f:
            filePaths.append(os.path.join(r, file))

    return filePaths

#Function for connect
def connectFTP(conName, folder):
    connections = readConnections()
    files = folderParse(folder)

    ftp = ftplib.FTP()

    host = connections[conName][2] #Ip address
    port = 21
    ftp.connect(host, port)
    print('*'*80, '\n\n', ftp.getwelcome())

    try:
        print(" Logging in\n")
        ftp.login(connections[conName][0], connections[conName][1]) # username and password
    except:
        print("Login failed. Please make sure the connection is correct with -list")

    ftp.cwd('code')
    ftp.retrlines('LIST')

    print('\n', '*'*80, '\n')
    uploadFTP(ftp, files)

def uploadFTP(ftp, files):
    fileInfoDict = {}
    uploadSuccess = 0
    uploadFailed = 0

    # The function to upload the files
    print("\tUpload process beginng:\n")

    print("\tParsing files to upload...\n")
    # For loop to parse file information. Take language folder name, file name, other folders inside
    for path in files:
        info = path.split("/")[5]

        if os.path.dirname(info) not in fileInfoDict.keys():
            fileInfoDict[os.path.dirname(info)] = [[os.path.basename(info), path.replace('\\', '/')]]
        else:
            fileInfoDict[os.path.dirname(info)].append([os.path.basename(info), path.replace('\\', '/')])

    print("\tParsing of files completed.\n")

    print("\tCreating folders and uploading files...\n")

    for key in fileInfoDict:
    # for each key create folder then upload files. If another folder inside then create that as well
        try: # Create directory if it does not already exist
            ftp.mkd(key.replace('\\', '/')) #Folder name starting at python
            print(f"\t{key} directory created sucessfully: [*]")
        except ftplib.error_perm:
            print(f"\t{key} directory created: [ ] (already exists)")

        for item in fileInfoDict[key]:
            # upload the files with ftp.storebinary
            try:
                repKey = key.replace('\\', '/')
                ftp.storbinary(f'STOR {repKey}/{item[0]}', open(item[1], 'rb'))
                print(f"\t\tUploaded {item[0]}: [*]")
                uploadSuccess += 1
            except ftplib.error_perm:
                print(f"\t\tFailed to upload {item[0]}: [ ]")
                uploadFailed += 1

    print(f"\n\tUploaded {uploadSuccess} files. Failed to upload {uploadFailed} files.")
    print('\n', '*'*80, '\n')
    # upload all the respective files
    # go back to main file (language file)

if __name__ == "__main__":
    # Debug: print(f"Arguments count: {len(sys.argv)}")
    if len(sys.argv) <= 1:
        print("\nusage: \"python3 ftp-tool.py -help\"\n")
    else:
        #Running the program with -help will list all commands and give a little description of the tool
        if sys.argv[1] == '-help' or sys.argv[1] == '-h':
            print('*'*80, '\n', '\tftp-tool is used to save and easily connect to a ftp server\n\tto upload files only, from a specified folder.')
            print("\n-add will add new ftp connection \n\t(usage: \"python3 ftp-tool.py -add conName username password ip-address\")")
            print("\n-rem will remove a ftp connection \n\t(usage: \"python3 ftp-tool.py -rem conName\")")
            print("\n-list will list all ftp connections \n\t(usage: \"python3 ftp-tool.py -list\")")
            print("\n-con will connect to the given ftp name and upload files from folder name \n\t(usage: \"python3 ssh-tool.py -con conName folder\")")
            print('*'*80)

        #Running the program with -add will add a new connection
        elif sys.argv[1] == "-add" or sys.argv[1] == '-a':
            if len(sys.argv) == 6:
                addSSH(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            else:
                print('*'*80, "\n\nusage: \"python3 ftp-tool.py -add name-connection username password ip-address\"\n")
                print('*'*80)
            
        #Running the program with -rem will remove a ftp connection
        elif sys.argv[1] == "-rem" or sys.argv[1] == '-r':
            if len(sys.argv) == 3:
                removeSSH(sys.argv[2])
            else:
                print('*'*80, "\n\nusage: \"python3 ftp-tool.py -rem conName\"\n")
                print('*'*80)

        #Running the program with -list will list all the ftp connections
        elif sys.argv[1] == "-list" or sys.argv[1] == '-l':
            if len(sys.argv) == 2:
                listSSH()
            else:
                print('*'*80, "\n\nusage: \"python3 ftp-tool.py -list\"\n")
                print('*'*80)

        #Running the program with -con will connect to chosen ftp connection
        elif sys.argv[1] == "-con" or sys.argv[1] == '-c':
            if len(sys.argv) == 4:
                connectFTP(sys.argv[2], sys.argv[3])
            else:
                print('*'*80,"\n\nusage: \"python3 ftp-tool.py -con conName filename\"\n")
                print('*'*80)