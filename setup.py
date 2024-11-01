from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Arun Kumar Redy Rayini',
	authour_email='rayini.a@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)