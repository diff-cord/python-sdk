from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='diffcord',
    version='0.0.7',
    description="A Python wrapper for the Diffcord API written in Python.",
    packages=find_packages(),
    author='jadelasmar4@gmail.com',
    zip_safe=False,
    install_requires=requirements,
    python_requires='>=3.7.0',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    keywords=['diffcord', 'diffcord-api', 'diffcord-api-wrapper', 'diffcord-api-python-wrapper', 'diffcord-api-python'],
    project_urls={
        "Github": "https://github.com/diff-cord/python-sdk"
    }
)
