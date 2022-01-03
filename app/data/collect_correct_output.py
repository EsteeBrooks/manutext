''' Collect correct output for each file based on XML file:'''
from bs4 import BeautifulSoup
import os
import re

directories = ['./BiblIA_dataset/Sephardi/',
               './BiblIA_dataset/Ashkenazy/',
               './BiblIA_dataset/Italian/']

for directory in directories:
    # iterate over files in that directory
    for filename in os.listdir(directory):

        # Skipp .jpg files:
        if re.match('.*?(\.jpg)', filename):
            continue

        f = os.path.join(directory, filename)

        # checking if it is a file
        if os.path.isfile(f):
            # Create a list of all lines for this file:
            lines = []
            print(f)
            # Open with BeautifulSoup:
            with open(f) as f:
                soup = BeautifulSoup(f, 'xml')
                string_data = soup.find_all("String")
                for i in string_data:
                    lines += [str(i.get('CONTENT'))]

            # Create a file to store the correct text:
            with open("./text_data/" + filename[:-4] + ".txt", "w") as file:
                file.write(('\n'.join(lines)))

