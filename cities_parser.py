import pandas as pd
import random

#!!!!! USE git lfs pull 
#thx to: https://github.com/x88/i18nGeoNamesDB
class CitiesParser: 
    def __init__(self):
        self.countries = pd.read_csv('countries.csv')
        self.cities = pd.read_csv('cities.csv')

    def get_question_hard(self):
        rand_index = random.randrange(0, len(self.cities))
        city = self.cities.loc[rand_index]
        ids = set()
        ids.add(city.country_id)
        while len(ids) != 4:
            ids.add(random.randrange(0, len(self.countries)))
        return (city.title_ru, self.countries.loc[city.country_id].title_ru), [self.countries.loc[x].title_ru for x in ids]

    def get_question_easy(self):
        rand_index = random.randrange(0, len(self.cities))
        city = self.cities.loc[rand_index]
        ids = set()
        ids.add(city.country_id)
        while len(ids) != 3:
            ids.add(random.randrange(0, len(self.countries)))
        return (city.title_ru, self.countries.loc[city.country_id].title_ru), [self.countries.loc[x].title_ru for x in ids]


if __name__ == '__main__':
    c = CitiesParser()
    print(c.get_question_hard())