import setuptools
import mijiaAPI

with open("README.md", "r", encoding='utf-8') as fp:
    long_description = fp.read()
with open("requirements.txt", "r", encoding='utf-8') as fp:
    requirements = fp.read().splitlines()

setuptools.setup(
    name = mijiaAPI.__title__,
    version = mijiaAPI.__version__,
    author = mijiaAPI.__author__,
    author_email = mijiaAPI.__author_email__,
    description = mijiaAPI.__description__,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = mijiaAPI.__url__,
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires = requirements,
    python_requires = '>=3.7'
)
