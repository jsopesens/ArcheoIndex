from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .views import thesaurus


class KeywordSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return thesaurus.get_all_keyword_ids()

    def location(self, item):
        return reverse('single_keyword', args=[item])


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['home', 'browse']

    def location(self, item):
        return reverse(item)
