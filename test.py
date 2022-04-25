with open('countries.csv', 'r') as r:
    with open('countries(changed).csv', 'w') as w:
        im = r.readlines()
        for i in im:
            w.write(i.replace(';', ','))
