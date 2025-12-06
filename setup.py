from setuptools import setup, find_packages

setup(
    name="suggestify",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers",
        "torch",
        "faiss-cpu",
        "rapidfuzz",
        "pandas",
        "sqlalchemy",
    ],
    author="MD Jubayer Khan",
    description="Domain-agnostic semantic query suggestion engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/MD-Jubayer-Khan/suggestify",
)
