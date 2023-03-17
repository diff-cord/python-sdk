from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='diffcord',
    version='0.1',
    description="A Python wrapper for the Diffcord API written in Python.",
    packages=['diffcord'],
    author='tech@diffcord.com',
    zip_safe=False,
    install_requires=requirements,
    python_requires='>=3.8.0',
)
