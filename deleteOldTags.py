import requests
import sys

registryURL="http://registry.com"
registryPort=5000
username=""
password=""

headers = {'accept':'application/vnd.docker.distribution.manifest.v2+json'}

if len(sys.argv) < 2:
	print("Invalid Arguments! (python deleteOldTags.py IMAGE_NAME)")

imageName=sys.argv[1]

regResponse = requests.get(registryURL+':'+str(registryPort)+'/v2/'+imageName+'/tags/list', auth=(username, password))

if regResponse.status_code == 200:
	tagList=sorted(regResponse.text.split("[")[1].split("]")[0].replace("\"","").split(","))[:-1]

	for tag in tagList:
		print("Removing tag: " + tag)
		manifestHash = requests.get(registryURL+':'+str(registryPort)+'/v2/'+imageName+'/manifests/'+tag, auth=(username, password), headers=headers).headers['Docker-Content-Digest']
		deleteResponse = requests.delete(registryURL+':'+str(registryPort)+'/v2/'+imageName+'/manifests/'+manifestHash, auth=(username, password), headers=headers) 
		print(deleteResponse)

elif regResponse.status_code == 404:
	print("Image not found !") 

elif regResponse.status_code == 401:
	print("Incorrect Credentials !")

else:
	print("Received Error Code " + regResponse.status_code)
