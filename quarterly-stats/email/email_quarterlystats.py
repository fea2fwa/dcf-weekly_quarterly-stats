import re

filename='Q1FY26.txt'

def domain_count(domdic):
    for k, v in sorted(domdic.items(), key=lambda x: -x[1]):
        print(k+';'+str(v))

    print('\n\n\n')

questionNo = {}
userNo = {}
userNoFinal = {}
necpattern = 'jp.nec.com'

with open(filename, encoding='utf-8') as f:
    for row in f:
        columns = row.rstrip().split('@')
        domain = columns[1]

        matchNEC = re.search(necpattern, domain)
        if matchNEC:
            domain = necpattern

        if domain in questionNo.keys():
            questionNo[domain] += 1
        else:
            questionNo[domain] = 1
        
    domain_count(questionNo)


with open(filename, encoding='utf-8') as f2:
    for row in f2:
        address = row.rstrip()

        matchNEC = re.search(necpattern, address)
        if matchNEC:
            emailsplit = address.split('@')
            emailname = emailsplit[0]
            address = emailname+'@'+necpattern

        if address in userNo.keys():
            userNo[address] += 1
        else:
            userNo[address] = 1

    for k, v in userNo.items():
        columns = k.split('@')
        userdomain = columns[1]
        if userdomain in userNoFinal.keys():
            userNoFinal[userdomain] += 1
        else:
            userNoFinal[userdomain] = 1

    domain_count(userNoFinal)       
