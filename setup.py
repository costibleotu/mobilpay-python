from setuptools import setup, find_packages

setup(
    name='mobilpay',
    version='0.1.0',
    author='Mobilpay',
    author_email='your.email@example.com',
    description='A Python implementation for MobilPay integration.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/costibleotu/mobilpay-python',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
    install_requires=[
        'pycrypto',
        'pyopenssl',
    ],
)
