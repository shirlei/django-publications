from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    url =  models.URLField(null=True, blank=True)
    # see DOI prefix at https://www.doi.org/doi_handbook/2_Numbering.html
    doi = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.short_name if self.short_name else self.name
