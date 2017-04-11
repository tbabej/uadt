from faker import Faker


class DataGenerator(object):

    def __init__(self, seed=None):
        self.faker = Faker(seed=seed)

    def text(self):
        return self.faker.text()
