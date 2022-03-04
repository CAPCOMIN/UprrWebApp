# -*- coding: utf-8 -*-
# @Time    : 2022/3/1
# @Author  : zxy
# @Version : 1.0
# @Software: PyCharm

import sys
from configs import *
import pandas as pd
import ijson
import csv
import time

sys.path.append(PROJECT_PATH)

data = pd.read_csv(DATA_PATH, usecols=['courseID'])
data.drop_duplicates(subset=None, keep='first', inplace=True)
courses = data['courseID'].values.tolist()
options = []

for c in courses:
    opt = '<option >' + c + '</option>'
    options.append(opt)

f = open("coursesOption.txt", "w")
for opt in options:
    f.write(opt + '\n')
f.close()

print("Successfully update the course options in coursesOption.txt file.")
