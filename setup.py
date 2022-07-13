from setuptools import setup, find_packages


with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

NAME = "flight-distance"

setup(
    name=NAME,
    version="0.1",
    description="Calculate flight distance (using Vincenty's formulae) and classify flight (according to EU classification)",
    packages=find_packages(),
    python_requires=">=3.9.13",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    install_requires=install_requires,
    entry_points={"console_scripts": [f"{NAME} = main:app"]},
)
