from setuptools import setup, find_packages

install_requirements = [
    'pebble', 'sklearn', 'docopt', 'pandas',
    'Appium-Python-Client', 'pyshark',
    'cached_property', 'pyudev', 'faker',
    'editdistance'
]

version = '0.8.0'

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
    entry_points={
        'console_scripts': [
            'uadt-theater = uadt.automation.theater:main',
            'uadt-usb-reset = uadt.automation.usbreset:main',
            'uadt-splitter = uadt.analysis.splitter:main',
            'uadt-dataset = uadt.analysis.dataset:main',
            'uadt-timeline = uadt.analysis.timeline:main',
            'uadt-live = uadt.analysis.live:main',
            'uadt-model-svm = uadt.analysis.svm:main',
            'uadt-model-tree = uadt.analysis.tree:main',
            'uadt-model-forest = uadt.analysis.randomforest:main',
        ]
    },
)
