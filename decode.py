import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet.task import deferLater

class GithubSpider(scrapy.Spider):
    name = 'decode_b64_github_spider'
    start_urls = [
        "https://github.com/smenaaliaga/encode_b64/blob/main/sqltoolsservice/sqltoolsservice_b64_aa.md?plain=1",
        # Agrega más URLs aquí
    ]

    def parse(self, response):
        # Espera 2 segundos antes de procesar la respuesta
        return deferLater(reactor, 2, self.extract_content, response)

    def extract_content(self, response):
        # Espera 2 segundos antes de extraer el contenido
        return deferLater(reactor, 2, self.print_content, response)

    def print_content(self, response):
        # Extrae el contenido de cada línea dentro de los divs con el atributo data-key
        for line in response.css('div[data-key] div.react-file-line::text').getall():
            print(line)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(GithubSpider)
    process.start()