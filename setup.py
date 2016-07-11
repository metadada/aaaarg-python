from setuptools import setup

setup(name='aaaarg-python',
      version='0.11',
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
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      zip_safe=False)
