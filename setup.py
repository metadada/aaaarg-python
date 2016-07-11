from setuptools import setup

setup(name='aaaarg-python',
      version='0.1',
      description='Python interface for aaaarg',
      url='http://github.com/metadada/aaaarg-python',
      author='metadada',
      author_email='metadadametadada@gmail.com',
      license='GPL3',
      packages=['aaaarg'],
      install_requires=[
          'requests',
          'lxml'
      ],
      zip_safe=False)