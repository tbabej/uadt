from setuptools import setup, find_packages

install_requirements = [
    'pebble', 'sklearn', 'docopt', 'pandas',
    'Appium-Python-Client', 'pyshark'
]

version = '0.1.0'

setup(
    name='uadt',
    version=version,
    description='User Activity Detection Toolkit',
    long_description=open('README.md').read(),
    author='Tomas Babej',
    author_email='tomasbabej@gmail.com',
    license='AGPLv3',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
)
