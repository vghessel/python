#!/usr/bin/env  python3
import os
import requests
import json
import re

accessToken = os.getenv("SYNC_MR_TOKEN")
headers = {"PRIVATE-TOKEN": accessToken,
           'Content-Type': 'application/json', 'Accept': 'application/json'}
ciCommitTag = os.getenv("CI_COMMIT_TAG")
projetcId = os.getenv("CI_PROJECT_ID")
previousBuild = "0"
previousVersion = "0"

gitUrlTag = 'https://github.com/aoliveira94/api/v4/projects/{}/repository/tags'
gitTagsVersion = requests.get(gitUrlTag.format(projetcId), headers=headers)

tagName = json.loads(gitTagsVersion.content)
listTag = []

for i in tagName:
    listTag.append(i['name'])

print('Available versions in repo =>', listTag, '\n')

regEx = re.compile('[a-z]?[0-9][-]?[a-z]?')
filterRegEx = regEx.search(ciCommitTag).string

commitMajor = filterRegEx[0:2]
commitMinor = filterRegEx[3]
commitBuild = filterRegEx[5:20]

for T in listTag:
    major = T[0:2]
    minor = T[3]
    build = T[5]

    if ((major == commitMajor)
        and (minor == commitMinor)
        and (build < commitBuild)
            and (build > previousBuild)):
        previousBuild = build
        previousVersion = T

if previousVersion == "0":
    previousVersion = ciCommitTag

print("Previous version is", previousVersion +
      ";", "New version is", ciCommitTag, '\n')

urlGit = 'https://github.com/aoliveira94/api/v4/projects/{}/repository/compare?from={}&to={}'
getLog = requests.get(urlGit.format(projetcId,previousVersion,ciCommitTag), headers=headers)

try:
    tagCommits = json.loads(getLog.content)
    outputCommits = tagCommits['commits']
except:
    print('Tag not exists')
    exit()

for i in outputCommits:
    with open('synLogs.txt', 'a',) as file:
        file.write('\n'+('<tr>'+'<td>'+i['id'][0:10]+'</td>'+'<td>'+i['committer_email'] +
                ' ('+i['author_name']+')'+'</td>'+'<td>'+i['title']+'</td>'+'<tr>'))
        file.close()

try:
    insert = {'id': (projetcId), 'tag_name': (ciCommitTag), 'name': (ciCommitTag)}
    openfile = open('synLogs.txt', 'r')
    insert['description'] = openfile.read()
    regexInsert = re.findall(r'[A-Z]+-\d', insert['description'])
    regexInsert = set(regexInsert)
    insert['description'] = '<table><tr><td colspan=3><strong>DetailedInformation</strong></td></tr><tr><th>Commit ID</th><th>Committer</th><th>Description</th></tr>{0}</table>'.format(
    insert['description'])
    fileopen = open('./tagdata.json', 'w')
    fileopen.write(json.dumps(insert))
    fileopen.close()
except:
     print('[!] Release tag not exists')
     exit()

# POST THE RELEASE
urlGitPost = 'https://github.com/aoliveira94/api/v4/projects/{}/releases/'
uploadPost = open('./tagdata.json', 'r')
fileJson = uploadPost.read()
postTagRelease = requests.post(
    urlGitPost.format(projetcId), headers=headers, json=json.loads(fileJson))
print(postTagRelease.content)

# # CHANGE TAG RELEASE IN PUT
# urlGitPut = 'https://github.com/aoliveira94/api/v4/projects/{}/releases/{}'
# putTagRelease = requests.put(
#     urlGitPut.format(projetcId, ciCommitTag), headers=headers, json=json.loads(fileJson))
# print(putTagRelease.content)