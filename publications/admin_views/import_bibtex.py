__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.bibtex import parse
from publications.models import Type
from publications.utils import populate_from_bib

def import_bibtex(request):
	if request.method == 'POST':
		# try to parse BibTex
		bib = parse(request.POST['bibliography'])

		# container for error messages
		errors = {}

		# check for errors
		if not bib:
			if not request.POST['bibliography']:
				errors['bibliography'] = 'This field is required.'

		if not errors:
			publications, errors = populate_from_bib(bib)

		if not errors and not publications:
			errors['bibliography'] = 'No valid BibTex entries found.'

		if errors:
			# some error occurred
			return render(
				request,
				'admin/publications/import_bibtex.html', {
					'errors': errors,
					'title': 'Import BibTex',
					'types': Type.objects.all(),
					'request': request})
		else:
			try:
				# save publications
				for publication in publications:
					publication.save()
			except:
				msg = 'Some error occured during saving of publications.'
			else:
				if len(publications) > 1:
					msg = 'Successfully added ' + str(len(publications)) + ' publications.'
				else:
					msg = 'Successfully added ' + str(len(publications)) + ' publication.'

			# show message
			messages.info(request, msg)

			# redirect to publication listing
			if len(publications) == 1:
				return HttpResponseRedirect('../%s/change/' % publications[0].id)
			else:
				return HttpResponseRedirect('../')
	else:
		return render(
			request,
			'admin/publications/import_bibtex.html', {
				'title': 'Import BibTex',
				'types': Type.objects.all(),
				'request': request})

import_bibtex = staff_member_required(import_bibtex)
