# run script with command python3 manage.py shell < logs/generate_codes3.py

from random import choice
from game.models import Codes
from django.db import transaction
import sys

choices = 'abcdefghijklmnopqrstuvwxyz1234567890'
counts = 0
needs = 10000500
insert_list = []
for s1 in choices:
    c1 = s1
    for s2 in choices:
        c2 = c1 + s2
        for s3 in choices:
            c3 = c2 + s3
            for s4 in choices:
                if counts > needs:
                    print(counts)
                    if len(insert_list) > 0:
                        Codes.objects.bulk_create(insert_list, batch_size=500)
                    sys.exit("Done")
                c4 = c3 + s4
                for s5 in choices:
                    c5 = c4 + s5
                    record = Codes(code=c5, attempts=1)
                    insert_list.append(record)
                    counts += 1

