import os
import setuptools

project_dir = os.path.dirname(os.path.realpath(__file__))

setuptools.setup(
    name='jsonc',
    version='0.1',
    description='json for config files',
    long_description=open(os.path.join(project_dir, 'README.md'), 'r').read(),
    keywords=['json'],
    author='Minjun Li',
    url='https://github.com/minjunli/jsonc',
    py_modules=['jsonc'],
    license='MIT',
    license_files=['LICENSE'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
