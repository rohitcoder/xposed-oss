VERSION = "0.3.21"

from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requires = f.read().splitlines()

setup(
    name='xposed_oss',
    version=VERSION,   
    description='A tool to map all IAM in google cloud project',
    long_description='A tool to map all IAM in google cloud project',
    long_description_content_type="text/markdown",
    url='https://github.com/rohitcoder/xposed-oss',
    author='Rohit Kumar',
    author_email='',
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'tests.*', 'release']),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'xposed_oss = xposed_oss.__main__:main',
        ],
    },
    license='Apache License 2.0',
    install_requires=requires,
    extras_require={
        "dev": ["twine>=4.0.2"],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='pii secrets sensitive-data cybersecurity scanner',
)