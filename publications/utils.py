import re

import publications.six as six
from publications.models import CustomLink, CustomFile, Publication, Type
from publisher.models import Publisher

# mapping of months
MONTHS = {
	'jan': 1, 'january': 1,
	'feb': 2, 'february': 2,
	'mar': 3, 'march': 3,
	'apr': 4, 'april': 4,
	'may': 5,
	'jun': 6, 'june': 6,
	'jul': 7, 'july': 7,
	'aug': 8, 'august': 8,
	'sep': 9, 'september': 9,
	'oct': 10, 'october': 10,
	'nov': 11, 'november': 11,
	'dec': 12, 'december': 12}

def populate(publications):
	"""
	Load custom links and files from database and attach to publications.
	"""

	customlinks = CustomLink.objects.filter(publication__in=publications)
	customfiles = CustomFile.objects.filter(publication__in=publications)

	publications_ = {}
	for publication in publications:
		publication.links = []
		publication.files = []
		publications_[publication.id] = publication

	for link in customlinks:
		publications_[link.publication_id].links.append(link)
	for file in customfiles:
		publications_[file.publication_id].files.append(file)

def populate_from_bib(bib):
	publications = []
	errors = {}
	# publication types
	types = Type.objects.all()

	for entry in bib:
				if 'title' in entry and \
				   'author' in entry and \
				   'year' in entry:
					# parse authors
					authors = entry['author'].split(' and ')
					for i in range(len(authors)):
						author = authors[i].split(',')
						author = [author[-1]] + author[:-1]
						authors[i] = ' '.join(author)
					authors = ', '.join(authors)

					# add missing keys
					keys = [
						'journal',
						'booktitle',
						'institution',
						'url',
						'doi',
						'isbn',
						'keywords',
						'pages',
						'note',
						'abstract',
						'month']

					for key in keys:
						if not key in entry:
							entry[key] = ''

					# map integer fields to integers
					entry['month'] = MONTHS.get(entry['month'].lower(), 0)

					entry['volume'] = entry.get('volume', None)
					entry['number'] = entry.get('number', None)

					if isinstance(entry['volume'], six.text_type):
						entry['volume'] = int(re.sub('[^0-9]', '', entry['volume']))
					if isinstance(entry['number'], six.text_type):
						entry['number'] = int(re.sub('[^0-9]', '', entry['number']))

					# remove whitespace characters (likely due to line breaks)
					entry['url'] = re.sub(r'\s', '', entry['url'])

					# determine type
					type_id = None

					for t in types:
						if entry['type'] in t.bibtex_type_list:
							type_id = t.id
							break

					if type_id is None:
						errors['bibliography'] = 'Type "' + entry['type'] + '" unknown.'
						break

					publisher = None
					entry['publisher'] = entry.get('publisher', None)

					if entry['doi']:
						doi_prefix = extract_doi_prefix(entry['doi'])
						publisher = Publisher.objects.get(doi=doi_prefix)
					
					if publisher is None and entry['publisher']:
						#TODO shortname, maybe some sort of slug?
						publisher, created = Publisher.objects.get_or_create(name=entry['publisher'])
					
					entry['publisher'] = publisher

					# add publication
					publications.append(Publication(
						type_id=type_id,
						citekey=entry['key'],
						title=entry['title'],
						authors=authors,
						year=entry['year'],
						month=entry['month'],
						journal=entry['journal'],
						book_title=entry['booktitle'],
						publisher=entry['publisher'],
						institution=entry['institution'],
						volume=entry['volume'],
						number=entry['number'],
						pages=entry['pages'],
						note=entry['note'],
						url=entry['url'],
						doi=entry['doi'],
						isbn=entry['isbn'],
						external=False,
						abstract=entry['abstract'],
						keywords=entry['keywords']))
				else:
					errors['bibliography'] = 'Make sure that the keys title, author and year are present.'
					break
	return publications, errors


def extract_doi_prefix(doi):
	m = re.search(r'10[\.\d+]+/', doi)
	if m:
		return m.group(0)[:-1]