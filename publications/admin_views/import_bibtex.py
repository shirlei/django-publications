__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.models import List
from publications.utils import populate_from_bib
from .forms import ImportBibitexForm

def import_bibtex(request):
	bib_form = ImportBibitexForm()
	if request.method == 'POST':
		# try to parse BibTex
		bib_form = ImportBibitexForm(request.POST)
		#bib = parse(request.POST['bibliography'])
		if bib_form.is_valid():
			bib_form.save()
			return HttpResponseRedirect('../')
	return render(
		request,
		'admin/publications/import_bibtex.html', {
		'title': 'Import BibTex',
		'lists': List.objects.all(),
		'form': bib_form,
		'request': request})

import_bibtex = staff_member_required(import_bibtex)
