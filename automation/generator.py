import random

from faker import Faker


class DataGenerator(object):

    def __init__(self, seed=None):
        self.faker = Faker(seed=seed)

    def text(self):
        return self.faker.text(max_nb_chars=random.randint(5, 70))
