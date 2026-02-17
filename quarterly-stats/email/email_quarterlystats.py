import pandas as pd
import re

filename = 'addresses.txt'
necpattern = 'jp.nec.com'
output_excel_filename = 'email_stats.xlsx'

# Read addresses and extract domains
emails = []
with open(filename, encoding='utf-8') as f:
    for row in f:
        emails.append(row.strip())

df = pd.DataFrame(emails, columns=['Email'])

def get_domain(email):
    domain = email.split('@')[1]
    if re.search(necpattern, domain):
        return necpattern
    return domain

df['Domain'] = df['Email'].apply(get_domain)

# Calculate question counts
question_counts = df['Domain'].value_counts().reset_index()
question_counts.columns = ['Domain', 'Question Count']

# Calculate user counts
user_counts = df.drop_duplicates(subset=['Email'])['Domain'].value_counts().reset_index()
user_counts.columns = ['Domain', 'User Count']

# Merge question and user counts
merged_df = pd.merge(question_counts, user_counts, on='Domain', how='outer').fillna(0)

# Sort by domain in descending order
sorted_df = merged_df.sort_values(by='Question Count', ascending=False)

# Write to Excel
sorted_df.to_excel(output_excel_filename, index=False)

print(f"Output successfully written to {output_excel_filename}")