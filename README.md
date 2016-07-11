pip install aaaarg-python

```
import aaaarg
# Client can be anonymous
c = aaaarg.Client()

# .. or an authenticated user
c = aaaarg.Client(username='email@address.com', password='abc123')

# .. or can use a different installation of aaarg platform
c = aaaarg.Client(base_url='http://localhost', username='email@address.com', password='abc123')

# searching
results = c.search_texts(query)
results = c.search_authors(query)
results = c.search_collections(query)
# Check if a file corresponds to a text
text_id = c.check_file(file_location)
# Getting 
data = c.get_text(id)
data = c.get_author(id)
data = c.get_collection(id)
# Downloading
c.download(url, download_directory)
c.download_all(text_id, download_directory)
# Create collection
c.create_collection(title, short_description='', long_description='', accessibility='public')
# Add text to collection (user must have permission)
c.add_text_to_collection(text_id, collection_id)
# Create a text (optional collection should be id)
c.create_text(title='', authors=[], files=[], short_description='', long_description='', collection=False)
# Update a text (only specified fields will be updated)
c.update_text(id, title='', authors=[], short_description='', long_description='')
# Add a file to a text
c.add_file_to_text(file_location, text_id)

```