import re
import csv

filename='addresses.txt'

def write_and_print_counts(domdic, output_csv_filename):
    """Prints counts to console and writes them to a CSV file."""
    with open(output_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Domain', 'Count'])
        for k, v in sorted(domdic.items(), key=lambda x: -x[1]):
            print(k + ';' + str(v))
            writer.writerow([k, v])
    
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
        
    write_and_print_counts(questionNo, 'question_counts.csv')


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

    write_and_print_counts(userNoFinal, 'user_counts.csv')       
