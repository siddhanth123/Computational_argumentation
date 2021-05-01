# Setup Anaconda Environment

This directory contains a conda environment file which contains a list of all the libraries that are required to work on assignments.

# How to setup Anaconda Environment from an environment.yml file to local machine?

* Download the [Anaconda Individual Edition](https://www.anaconda.com/products/individual).
* Check Operating System and 32 or 64 bit version software for your PC. It will take some time to download the installer file.
* Double click on .exe file and follow the prompt window and don’t change the default settings. (https://www.youtube.com/watch?v=C4OPn58BLaU)
* Open project terminal (..\\Computational_argumentation>) and type below command to create the Anaconda environment in local from the environment.yml file.
    >conda env create -f .conda/environment.yml

# How to update or install library in Local Anaconda Environment?

<!-- Follow the step mentioned in link to [update or add library](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#updating-an-environment) in local Anaconda Environment. -->

# How to export the environment.yml file?

<!-- After adding or updating any new packages to environment, export the updated environment.yml file. -->
<!-- >conda env export --from-history >environment.yml -->

# How to push updated environment.yml file to GitLab repository?

<!-- Copy updated environment.yml file from user directory (Computational_argumentation\\.conda\\) to code repository (Computational_argumentation\\.conda\\) and push it to GitHub. -->
