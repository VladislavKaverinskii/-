import json
import sys

test_dict_1 = {
'IsCurrent': 1,
'url': 2,
'availability': 3,
'dif': 4,
'price': 5
}

report = []

for i in range(20):
    report.append(test_dict_1)


m = '"IsCurrent": {0}, "url": {1}, "availability": {2}, "dif": {3}, "price": {4}'\
    .format(report[17]['IsCurrent'], report[17]['url'], report[17]['availability'],
            report[17]['dif'], report[17]['price'])
print(m)

n = json.loads(m)

print(n)

