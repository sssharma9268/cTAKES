import os, shutil, subprocess, random, datetime, string, json, csv
from distutils.dir_util import copy_tree
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient

dirName = 'temp'
fakeFolder = 'random'
inputFolder = 'cTakesExample'
configFolder = 'ctakes-config'
configFolder2 = 'ctakes-config2'
cData = 'cData'
granularDir = 'granular'
overviewDir = 'overview'

#configuration for upload file to datalake
storage_account_name = "datalake182238"
storage_account_key = "pdldwgtm38iQ96GldBK9NUkgTzjbtO/Z2F9qQHtREPwS0sXiAlF1MlJC82jzDs/Q1FhK6wcQzlqa+AStb4ykLg=="
storage_account_URL = "https://datalake182238.dfs.core.windows.net"
container_name = "datalakecontainer"
directory_name = "datalakedir"

# Source resource path
sourceResourcefile = '/usr/app/cTAKES/resources'
 
# Destination resource path
destinationResourcefile = '/usr/app/temp/ctakes-config'

#connection string to downlod data from container 
connection_string="DefaultEndpointsProtocol=https;AccountName=storageacct182238;AccountKey=yGHxZd59WJeUSZaTzAyM4JutvRqzbo4LyWpTF5G9Db4nMIMyIXDeGkdzeCv08Dk/NS+X9C+vV5Wa+AStq8rHeA==;EndpointSuffix=core.windows.net"

def executeCtakes():
    print('Inside cTakes api')
    os.chdir('/usr/app/')
    # checking of directory already exists or not
    if os.path.isdir(dirName):
        # remove the directory
        shutil.rmtree(dirName)
    # Create temp Directory   
    os.mkdir(dirName) # create the directory
    print('Directory ', dirName, ' is created successfully')
    # Change the directory into tmp
    os.chdir(dirName)
    # Create fakeFolder Directory
    os.mkdir(fakeFolder)
    # Create inputFolder Directory
    os.mkdir(inputFolder)
    # create cData folder
    os.chdir(inputFolder)
    os.mkdir(cData)
    # Create configFolder Directory
    os.chdir('../')
    os.mkdir(configFolder)
    # Create configFolder2 Directory
    os.mkdir(configFolder2)
    
    print('Input/Output/Config Folders created successfully')
      
    #  Copy the content of Resource source to destination
    copy_tree(sourceResourcefile, destinationResourcefile)
    print('Configuration files copied successfully ') 
    
    #environment variable 
    #message = str(os.environ['blobDownload']) 
    message = str('container182238/11111.txt/True') 
    print(message) 

    #get tha container name, blob name and jobpipline value
    container_name = message.split('/')[0]
    print(container_name)
    blob_name = message.split('/')[1]
    print(blob_name)
    jobType = message.split('/')[2]
    print(jobType)
    
    if jobType == 'True':
        jobType == 'daily'
    else:
        jobType == 'research'
    
    #download blob from container
    source_blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    source_container_client = source_blob_service_client.get_container_client(container_name)
    source_blob_client = source_container_client.get_blob_client(blob_name)
    blob_data = source_blob_client.download_blob()
    print(blob_data)

    jsonDatas = json.loads(blob_data.readall())
    print(jsonDatas)
    
    for jsonData in jsonDatas:
        #get rawText from json data
        rawText = bytes(jsonData['rawText'], 'utf-8')
        
        #get pat_enc_csn_id from json data
        pat_enc_csn_id = bytes(jsonData['pat_enc_csn_id'], 'utf-8')
        
        #get note_id from json data
        note_id = bytes(jsonData['note_id'], 'utf-8')

        #write file into input folder
        os.chdir('/usr/app/temp/cTakesExample/cData')
        filename = pat_enc_csn_id + b'_' + note_id + b'.json'
        with open(filename, "wb") as datafile:
            datafile.write(rawText)
    
    print('file writen in cData folder')
    # Change the directory to cTakes/cTAKES
    os.chdir('../')
    os.chdir('/usr/app/cTAKES') # move it to usr/app
    print(os.getcwd())
    print('Navigated to cTakes folder and calling RushNiFiPipeline')
    if jobType == 'True': 
        subprocess.run('mvn exec:java -Dexec.mainClass="org.apache.ctakes.pipelines.RushNiFiPipeline" -Dexec.args="--input-dir /usr/app/temp/cTakesExample/cData --masterFolder /usr/app/temp/ctakes-config/ --output-dir /usr/app/temp/cTakesExample/ --tempMasterFolder /usr/app/temp/ctakes-config2/ --jobPipline daily"', shell=True, check=True)
    else:
        subprocess.run('mvn exec:java -Dexec.mainClass="org.apache.ctakes.pipelines.RushNiFiPipeline" -Dexec.args="--input-dir /usr/app/temp/cTakesExample/cData --masterFolder /usr/app/temp/ctakes-config/ --output-dir /usr/app/temp/cTakesExample/ --tempMasterFolder /usr/app/temp/ctakes-config2/ --jobPipline research"', shell=True, check=True)

    
    os.chdir('/usr/app/')
    os.chdir(dirName)
    os.chdir(inputFolder) 
    
    print('Navigated to the processed output folder')
    if os.path.isdir(granularDir)or os.path.isdir(overviewDir):
        print('ctakes process has been completed successfully')
    else:
        return 'granular and overview files are not processed'
    
    #upload file to datalake
    service_client = DataLakeServiceClient(account_url=storage_account_URL.format(
            "https", storage_account_name), credential=storage_account_key)

    #read input files
    if os.path.isdir(overviewDir):
        os.chdir(overviewDir) 
        listfiles = os.listdir()
        for filename in listfiles:
            f = open(filename,encoding='utf-8', errors='ignore')
            data = json.load(f)
            data["fname"] = filename
            date = datetime.date.today()
            data['loadTimestamp'] = date.strftime('%Y-%m-%d')
            
            outputfile = open(filename, "w")
            json.dump(data, outputfile)
            outputfile.close()
            
            file_system_client = service_client.get_file_system_client(file_system=container_name)
            directory_client = file_system_client.get_directory_client(directory_name)
            file_client = directory_client.create_file(filename)
            
            local_file = open(filename,'r')
            #read the file content
            file_contents = local_file.read()
            #push data into datalake
            file_client.append_data(data=file_contents, offset=0, length=len(file_contents))
            file_client.flush_data(len(file_contents))
            
    if os.path.isdir(granularDir):
        os.chdir(granularDir) 
        listfiles = os.listdir()
        for filename in listfiles:
        #print(i)
            with open(filename) as file:
                #print(file)
                outputdata = json.load(file)
                #print(outputdata)
                for index in range(len(outputdata)):
                    #print(outputdata)
                    outputdata[index]["fname"] = filename
                    date = datetime.date.today()
                    outputdata[index]["loadTimestamp"] = date.strftime('%Y-%m-%d')
                    #print(outputdata)
                    outputfile = open(filename, "w")
                    json.dump(outputdata, outputfile)
                    outputfile.close()
                    
                    file_system_client = service_client.get_file_system_client(file_system=container_name)
                    directory_client = file_system_client.get_directory_client(directory_name)
                    file_client = directory_client.create_file(filename)
                    
                    local_file = open(filename,'r')
                    #read the file content
                    file_contents = local_file.read()
                    #push data into datalake
                    file_client.append_data(data=file_contents, offset=0, length=len(file_contents))
                    file_client.flush_data(len(file_contents))
    
    return "ctakes process has been completed successfully " 

if __name__ == '__main__':
    executeCtakes()
   
