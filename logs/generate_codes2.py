# run script with command python3 manage.py shell < logs/generate_codes2.py

from random import choice
from game.models import Codes
from django.db import transaction
import sys

choices = 'abcdefghijklmnopqrstuvwxyz1234567890'
counts = 0
needs = 500

for s1 in choices:
    c1 = s1
    for s2 in choices:
        c2 = c1 + s2
        for s3 in choices:
            c3 = c2 + s3
            print(counts)
            if counts > needs:
                sys.exit("Done")
            with transaction.atomic():
                for s4 in choices:
                    c4 = c3 + s4
                    for s5 in choices:
                        c5 = c4 + s5
                        obj, created = Codes.objects.update_or_create(code=c5, attempts=1)
                        if created:
                            counts += 1

