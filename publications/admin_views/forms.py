from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext as _
from django import forms
from publications.models import List, Publication
from publications.bibtex import parse
from publications.utils import populate_from_bib

class ImportBibitexForm(forms.Form):
    bibliography = forms.CharField(widget=forms.Textarea(
        attrs={'cols': 80, 'rows': 20}))
    lists = forms.ModelMultipleChoiceField(queryset=List.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    publications = forms.ModelMultipleChoiceField(queryset=Publication.objects.none(),
        required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        bibtex = parse(cleaned_data['bibliography'])
        if not bibtex:
            self.add_error('bibliography',_("This field is required."))

        publications, errors = populate_from_bib(bibtex)
        if errors:
            raise ValidationError(errors)
        if not errors and not publications:
            self.add_error('bibliography',(_("No valid BibTex entries found.")))
        if publications:
            cleaned_data['publications'] = publications
        return cleaned_data

    def save(self, *args, **kwargs):
        lists = self.cleaned_data['lists']
        publications = self.cleaned_data['publications']
        for publication in publications:
            publication.save()
            if lists:
                publication.lists.set(lists)
            publication.save()
