from django.db import models
from django.conf import settings
from datetime import datetime
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

class NewsItem(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(help_text= _('A slug is used as part of the URL for this article. It is recommended to use the default value if possible.'))
    pub_date = models.DateField(blank=True, null=True, help_text= _('YYYY-MM-DD -- Leave blank if you don\'t want the article to appear on the site yet.' ))
    snippet = models.TextField(blank=True, help_text= _('Snippets are used as a preview for this article (in sidebars, etc).'))
    body = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ['-pub_date']
        unique_together = (('slug', 'pub_date'), )


