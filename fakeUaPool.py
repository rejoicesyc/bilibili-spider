from fake_useragent import UserAgent
from random import choice 

class FakeUaPool:
    def __init__(self,ua_number):
        self.ua=UserAgent()
        self.ua_set=set()
        self.ua_list=[]

        for i in range(ua_number):
            self.ua_set.add(self.ua.random)

        self.ua_list=list(self.ua_set)

    def get_random_ua(self):
        return choice(self.ua_list)


# fakeUaPool=FakeUaPool(50)
# print(fakeUaPool.get_random_ua())