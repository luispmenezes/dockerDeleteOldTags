import requests
import argparse
import sys

from requests.exceptions import ConnectionError

REGISTRY_URL="mswifimesh-register.c.ptin.corppt.com"
REGISTRY_PORT=5000
USERNAME=""
PASSWORD=""

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

parser = argparse.ArgumentParser()
parser.add_argument("--imagename", help="Purge only tags from specific image", default="all")
parser.add_argument("--registryurl", help="Set registry url", default=REGISTRY_URL)
parser.add_argument("--registryport", help="Set registry port", default=REGISTRY_PORT)
parser.add_argument("--registryuser", help="Set registry username", default=USERNAME)
parser.add_argument("--registrypwd", help="Set registry password", default=PASSWORD)
parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

if args.imagename != "all":
	imageList.append(args.imagename)
else:
	try:
		catalogResponse = requests.get('http://'+args.registryurl+':'+str(args.registryport)+'/v2/_catalog', auth=(USERNAME, PASSWORD))
	except ConnectionError as error:
		print("Failed to connect to registry!")
		print(error)
		exit(-1)

	if catalogResponse.status_code == 200:
		catalogList=sorted(catalogResponse.text.split("[")[1].split("]")[0].replace("\"","").split(","))[:-1]
		for catalogEntry in catalogList:
			imageList.append(catalogEntry)
	else:
		httpError(catalogResponse.status_code)

for imageName in imageList:
	print("Cleaning up tags for image: " + imageName)
	try: 
		regResponse = requests.get('http://'+args.registryurl+':'+str(args.registryport)+'/v2/'+imageName+'/tags/list', auth=(USERNAME, PASSWORD))
	except ConnectionError as error:
		print(error)
		exit(-1)

	if regResponse.status_code == 200:
		tagList=sorted(regResponse.text.split("[")[1].split("]")[0].replace("\"","").split(","))
		keepTag=""
		deleteTagList=[]
		print('\tImage tags: [%s]' % ', '.join(map(str, tagList)))

		if "latest" in tagList:
			keepTag = "latest"
		else:
			keepTag = tagList[-1]

		deleteTagList = tagList.copy()
		deleteTagList.remove(keepTag)	
		keepTagDigest=requests.get('http://'+args.registryurl+':'+str(args.registryport)+'/v2/'+imageName+'/manifests/'+keepTag, auth=(USERNAME, PASSWORD), headers=headers).headers['Docker-Content-Digest']
		
		print("\tKeeping tag: "+keepTag)

		if deleteTagList is not None:
			for tag in deleteTagList:	
				deleteDigest = requests.get('http://'+args.registryurl+':'+str(args.registryport)+'/v2/'+imageName+'/manifests/'+tag, auth=(USERNAME, PASSWORD), headers=headers).headers['Docker-Content-Digest']
				if deleteDigest != keepTagDigest:
					print("\tRemoving tag: " + tag)

					deleteResponse = requests.delete('http://'+args.registryurl+':'+str(args.registryport)+'/v2/'+imageName+'/manifests/'+deleteDigest, auth=(USERNAME, PASSWORD), headers=headers) 
					if deleteResponse.status_code == 202:
						print("\t\tOK!")
					elif deleteResponse.status_code == 405:
						print("\t\tReceived 405 (Method Not Allowed) : Delete is not enabled in the registry")
						exit(-1)
					else:
						httpError(regResponse.status_code)