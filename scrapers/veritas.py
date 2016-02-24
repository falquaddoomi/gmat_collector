import scrapy
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest

from dateutil.parser import parse as parse_datetime

class PracticeSession(scrapy.Item):
    student = scrapy.Field()
    taken_on = scrapy.Field()
    question_count = scrapy.Field()
    percent_correct = scrapy.Field()
    duration = scrapy.Field()


class VeritasScraper(scrapy.Spider):
    name = 'veritas'
    allowed_domains = ['veritasprep.com', 'gmat.veritasprep.com']
    start_urls = ['https://www.veritasprep.com/login/']

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def parse(self, response):
        return [FormRequest.from_response(
            response,
            formdata={'username': self.username, 'password': self.password},
            callback=self.after_login
        )]

    def after_login(self, response):
        # check login succeed before going on
        if "Your username or password does not exist." in response.body:
            self.log("Login failed")
            return

        return Request(url="http://gmat.veritasprep.com/question-bank/practices", callback=self.parse_practices)

    def parse_practices(self, response):
        # body > div.container > div.page-body > table > tbody
        practices = response.xpath('/html/body/div[2]/div[3]/table/tbody/tr')

        for row in practices:
            cells = [x.strip() for x in row.css('td::text').extract() if x.strip() != '']

            r = PracticeSession()
            r['student'] = self.username
            r['taken_on'] = parse_datetime(cells[0])
            r['question_count'] = int(cells[1])
            r['percent_correct'] = cells[2]
            r['duration'] = cells[3]
            yield r

