import scrapy
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest

from dateutil.parser import parse as parse_datetime
from dateparser.date import DateDataParser


class VeritasAccountCreator(scrapy.Spider):
    name = 'veritas_acct_create'
    allowed_domains = ['veritasprep.com', 'gmat.veritasprep.com']
    start_urls = ['https://www.veritasprep.com/checkout/log-in.php']

    def __init__(self, username, password, **kwargs):
        super(VeritasAccountCreator, self).__init__(**kwargs)
        self.username = username
        self.password = password
        self.email = "n/a"

    def parse(self, response):
        self.email = '%s_gmat@gmail.com' % self.username

        fr = FormRequest.from_response(
            response=response,
            formxpath='//*[@id="registerForm"]',
            formdata={
                'action': 'register',
                'redirect': 'ajax',
                'source': 'Checkout',
                'SFproductID': '',
                'first_name': self.username,
                'last_name': self.username,
                'username': self.email,
                'password': self.password,
            },
            callback=self.account_created
        )
        fr = fr.replace(url="https://www.veritasprep.com/checkout/LIBRARY/auth/AEntry.php")

        yield fr

    def account_created(self, response):
        return {'email': self.email, 'password': self.password}
