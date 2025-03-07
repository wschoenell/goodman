from distutils.core import setup

setup(
    name='goodman',
    version='1.0b2',
    packages=['goodman_ccd', 'goodman_spec'],
    package_dir={'goodman_ccd': 'goodman_ccd',
                 'goodman_spec': 'goodman_spec'},
    package_data={'goodman_ccd': ['files/dcr.par'],
                  'goodman_spec': ['refdata/*fits']},
    scripts=['bin/redccd', 'bin/redspec'],
    url='https://github.com/soar-telescope/goodman',
    license='BSD 3-Clause',
    author='Simon Torres R.',
    author_email='storres@ctio.noao.edu',
    description='Pipelines for CCD and Spectroscopic Reduction of Goodman Data'
)
