import requests
import sys

REGISTRY_URL="registryurl.com"
REGISTRY_PORT=5000
USERNAME="username"
PASSWORD="password"

imageList = []

headers = {'accept':'application/vnd.docker.distribution.manifest.v2+json'}

def httpError(errorCode):
	if errorCode == 404:
		print("Image not found !") 

	elif errorCode == 401:
		print("Incorrect Credentials !")

	else:
		print("Received Error Code " + errorCode)
	exit(-1)

if len(sys.argv) > 2:
	print("Invalid Arguments! (python deleteOldTags.py IMAGE_NAME)")

if len(sys.argv) == 2:
	imageList.append(sys.argv[1])
else:
	catalogResponse = requests.get('http://'+REGISTRY_URL+':'+str(REGISTRY_PORT)+'/v2/_catalog', auth=(USERNAME, PASSWORD))
	if catalogResponse.status_code == 200:
		catalogList=sorted(catalogResponse.text.split("[")[1].split("]")[0].replace("\"","").split(","))[:-1]
		for catalogEntry in catalogList:
			imageList.append(catalogEntry)
	else:
		httpError(regResponse.status_code)

for imageName in imageList:
	print("Cleaning up tags for image: " + imageName)
	regResponse = requests.get('http://'+REGISTRY_URL+':'+str(REGISTRY_PORT)+'/v2/'+imageName+'/tags/list', auth=(USERNAME, PASSWORD))

	if regResponse.status_code == 200:
		tagList=sorted(regResponse.text.split("[")[1].split("]")[0].replace("\"","").split(","))[:-1]

		for tag in tagList:
			print("Removing tag: " + tag)
			manifestHash = requests.get('http://'+REGISTRY_URL+':'+str(REGISTRY_PORT)+'/v2/'+imageName+'/manifests/'+tag, auth=(USERNAME, PASSWORD), headers=headers).headers['Docker-Content-Digest']
			deleteResponse = requests.delete('http://'+REGISTRY_URL+':'+str(REGISTRY_PORT)+'/v2/'+imageName+'/manifests/'+manifestHash, auth=(USERNAME, PASSWORD), headers=headers) 
			print(deleteResponse)
	else:
		httpError(regResponse.status_code)