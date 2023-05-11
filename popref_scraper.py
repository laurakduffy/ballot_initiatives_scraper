## Web Scraper for Popular Referenda
## Data Source: https://www.ncsl.org/research/elections-and-campaigns/ballot-measures-database.aspx
## Filtered for Popular Referendum, All Years, All States, related to Animal Rights/Hunting & Fishing, All Periods

import bs4
import regex as re
import urllib.request
import pandas as pd
import sqlite3

html = open("inputs\\popref_database.html", encoding="utf8").read()

soup = bs4.BeautifulSoup(html, features="html.parser")

# titles extraction
titles = []
titles_soup = soup.find_all("div", class_ = "divRepeaterTitle")
for element in titles_soup:
    title = element.getText()
    title = title.strip("\n")
    title = title.strip()
    titles.append(title)

# IDs extraction
ids = []
ids_soup = soup.find_all("div", class_ = "divRepeaterID")
for element in ids_soup:
    id = element.getText()
    id = id.strip("\n")
    id = id.strip()
    ids.append(id)

# Info about the initiative
internal = soup.find_all(
    'div', class_ = "divRepeaterInternal")

str_time = re.findall(r'(?is)<strong>\s*[^<]*?\s*<\/strong>\s*([^<]*?)\s*<', str(internal))
# finding primary/general/special election
election_type = re.findall(r'Primary|General|Special', str(str_time))

# finding the years   
years = re.findall(r'\d{4}', str(str_time))

# finding the results
strings = re.findall(r'(?is)<strong>\s*[^<]*?\s*<span style="color: [a-z]{3,5}">[a-zA-Z]{4}</span><\/strong>\s*([^<]*?)\s*<', str(internal))
yes_votes = re.findall(r'[0-9]+\.?[0-9]|Unknown', str(strings))

# summaries of referenda
sums = []
sum_soup = soup.find_all("div", class_ = "summary")
for element in sum_soup:
    sum = element.getText()
    sum = sum.strip("\n")
    sum = sum.strip()
    sums.append(sum)

# make the dataframe 
df = pd.DataFrame()

df["Title"] = titles
df["ID"] = ids
df["Year"] = years
df["Election_Type"] = election_type
df["Pct_Yes"] = yes_votes
df["Summary"] = sums

# make csv
df.to_csv("outputs\\popref_database.csv", index = False)

# make sql database
connection = sqlite3.connect('pop_ref_database')
c = connection.cursor()

c.execute('CREATE TABLE IF NOT EXISTS pop_ref \
        (title, id, year, election_type, pct_yes, sums)')

connection.commit()

df.to_sql('pop_ref', connection, if_exists='replace', index = False)
connection.commit()

connection.close()