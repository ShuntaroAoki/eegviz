from setuptools import setup


VERSION = '0.1'


if __name__ == '__main__':

    # Long description
    with open('./README.md') as f:
        long_description = f.read()

    # Setup
    setup(name='eegviz',
          version=VERSION,
          description='EEG data visualizer',
          long_description=long_description,
          long_description_content_type='text/markdown',
          author='Shuntaro C. Aoki',
          author_email='shuntaro.aoki@gmail.com',
          maintainer='Shuntaro C. Aoki',
          maintainer_email='shuntaro.aoki@gmail.com',
          url='',
          license='MIT',
          keywords='neuroscience,electroencephalogram',
          packages=[
              'eegviz',
          ],
          install_requires=[
              'mne',
              'numpy',
              'pandas',
          ])
