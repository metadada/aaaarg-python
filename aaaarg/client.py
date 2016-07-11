# -*- coding: UTF-8 -*-
import sys
import os
import requests
import json
import hashlib
from lxml import html


# Computes md5 hash of a file
def compute_md5(file_location):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    try:
        with open(file_location, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()
    except:
        return False


'''
Client can be anonymous (for searching) or use credentials (to add collections, texts)
'''
class Client:
    base_url = 'http://aaaaarg.fail'
    auth_path = '/auth/login'
    search_path = '/api/search'
    text_path = '/thing/<id>'
    author_path = '/maker/<id>'
    collection_path = '/collection/<id>'
    check_md5_path = '/upload/check/<id>'
    add_collection_path = '/collection/add'
    collect_path = '/collection/add/thing/<id>'
    collection_list_for_thing_path = '/collection/for/thing/<id>'
    add_file_path = '/upload/thing/<id>'
    add_text_path = '/thing/add'
    edit_text_path = '/thing/<id>/edit'
    
    def __init__(self, base_url=False, username=False, password=False):
        self.session = requests.session()
        if base_url:
            self.base_url = base_url
        self.base_url = self.base_url.strip("/")
        if username and password:
            self.authenticate(username, password)

    def get_csrf_token(self, url):
        result = self.session.get(url)
        tree = html.fromstring(result.text)
        return list(set(tree.xpath("//input[@name='csrf_token']/@value")))[0]

    def build_url(self, path, id=False):
        if id:
            return self.base_url + path.replace('<id>', id)
        else:
            return self.base_url + path 

    def authenticate(self, username, password):
        data = {
            'email' : username,
            'password' : password,
            'csrf_token' :  self.get_csrf_token(self.build_url(self.auth_path))
        }
        result = self.session.post(
            self.build_url(self.auth_path), 
            data = data 
        )

    def search(self, query, type, num):
        data = {
            'query' : query,
            'type' : type,
            'num' : num
        }
        result = self.session.post(
            self.build_url(self.search_path), 
            data = data 
        )
        try:
            doc = json.loads(result.text)
            return doc['data']
        except:
            return False

    def search_texts(self, query, num=10):
        return self.search(query, 'things', num)

    def search_authors(self, query, num=10):
        return self.search(query, 'makers', num)

    def search_collections(self, query, num=10):
        return self.search(query, 'collections', num)

    # Check a file. Returns text id
    def check_file(self, file_location):
        md5 = compute_md5(file_location)
        if md5:
            url = self.build_url(self.check_md5_path, md5)
            result = self.session.get(url)
            try:
                doc = json.loads(result.text)
                return doc['data']
            except:
                return False
        else:
            return False

    # Get text
    def get_text(self, id):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        result = self.session.get(
            self.build_url(self.text_path, id), 
            headers = headers
        )
        try:
            doc = json.loads(result.text)
            return doc['data']
        except:
            return []

    # Get author
    def get_author(self, id):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        result = self.session.get(
            self.build_url(self.author_path, id), 
            headers = headers
        )
        try:
            doc = json.loads(result.text)
            return doc['data']
        except:
            return []

    # Get collection
    def get_collection(self, id):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        result = self.session.get(
            self.build_url(self.collection_path, id), 
            headers = headers
        )
        try:
            doc = json.loads(result.text)
            return doc['data']
        except:
            return []

    # Downloads a file at a url to a specified directory
    def download(self, url, save_directory):
        file_name = url.split('/')[-1]
        if not os.path.exists(save_directory):
            os.make_dirs(save_directory)
        save_location = os.path.join(save_directory, file_name)
        r = self.session.get(url, stream=True)
        with open(save_location, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)

    # text id
    def download_all(self, id, save_directory):
        text = self.get_text(id)
        if text and 'files' in text:
            for url in text['files']:
                self.download(url, save_directory)

    # Returns id of the newly created collection
    def create_collection(self, title, short_description='', long_description='', accessibility='public'):
        data = {
            'title' : title,
            'short_description' : short_description,
            'description' : long_description,
            'accessibility' : accessibility,
            'csrf_token' :  self.get_csrf_token(self.build_url(self.add_collection_path)),
        }
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        result = self.session.post(
            self.build_url(self.add_collection_path), 
            data = data,
            headers = headers
        )
        try:
            doc = json.loads(result.text)
            return doc['data']
        except:
            return False

    # Adds a text to a collection
    def add_text_to_collection(self, text_id, collection_id):
        url = self.build_url(self.collect_path, text_id)
        data = {
            'collection' : collection_id,
            'csrf_token' : self.get_csrf_token(self.build_url(self.collection_list_for_thing_path, text_id))
        }
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        result = self.session.post(
            url, 
            data = data,
            headers = headers,
        )

    # Adds a file to a text.
    def add_file_to_text(self, file_location, text_id):
        if not self.check_file(file_location):
            files = {'file': open(file_location, 'rb')}
            data = {
                'short_description' : '..',
            }
            headers = {'X-Requested-With': 'XMLHttpRequest'}
            result = self.session.post(
                self.build_url(self.add_file_path, text_id), 
                data = data,
                headers = headers,
                files = files
            )

    # Only updates the fields that are passed in
    def update_text(self, id, title='', authors=[], short_description='', long_description=''):
        text = self.get_text(id)
        if text:
            if title:
                text['title'] = title
            if authors:
                text['makers_raw'] = ', '.join(authors)
            else:
                text['makers_raw'] = ', '.join([text['makers'][a] for a in text['makers']])
            if short_description:
                text['short_description'] = short_description
            if long_description:
                text['description'] = long_description
            url = self.build_url(self.edit_text_path, id)
            data = {
                'title' : text['title'],
                'makers_raw' : text['makers_raw'],
                'description' : text['description'],
                'short_description' : text['short_description'],
                'csrf_token' :  self.get_csrf_token(url)
            }
            headers = {'X-Requested-With': 'XMLHttpRequest'}
            result = self.session.post(
                url, 
                data = data,
                headers = headers
            )

    # Returns the id of the text, whether it is new or whether the file is associated with an already existing text
    def create_text(self, title='', authors=[], files=[], short_description='', long_description='', collection=False):
        '''
        This errs on the side of caution. If any of the files are already in the library, then creation 
        is aborted and files which are not there are added. If no files are in the library, then the 
        create operation is executed.
        
        Required arguments:
        title -- title of text
        authors -- list of authors (name should be in normal readable format: Firstname Lastname)
        files -- list of file locations
        Optional arguments:
        short_description -- Ideally about 150 characters
        long_description -- Markdown syntax 
        collection -- id of collection to add this text into
        '''
        add_files = []
        existing_text = False
        for f in files:
            tid = self.check_file(f)
            if tid:
                existing_text = tid
            else:
                add_files.append(f)
        if existing_text and add_files:
            for f in add_files:
                self.add_file_to_text(f, existing_text)
            if collection:
                self.add_text_to_collection(existing_text, collection)
            return {
                'status' : 'updated',
                'message' : 'Added %s files to existing text' % len(add_files)
            }
        elif not existing_text and add_files:
            url = self.build_url(self.add_text_path)
            count = 0
            for f in add_files:
                files = {'file_%s' % count: open(f, 'rb')}
                count = count + 1
            data = {
                'title' : title,
                'makers_raw' : ', '.join(authors),
                'description' : long_description,
                'short_description' : short_description,
                'csrf_token' :  self.get_csrf_token(url)
            }
            if collection:
                data['collection'] = collection
            headers = {'X-Requested-With': 'XMLHttpRequest'}
            result = self.session.post(
                url, 
                data = data,
                headers = headers,
                files = files
            )
            return {
                'status' : 'created',
                'message' : 'Created a new text'
            }
        else:
            if existing_text and collection:
                self.add_text_to_collection(existing_text, collection)
            return {
                'status' : 'none',
                'message' : 'There was nothing new to create or update'
            }


if __name__ == '__main__':
    print """
USAGE
=====
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
    """