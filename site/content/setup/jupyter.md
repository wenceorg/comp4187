---
title: "Jupyter"
weight: 1
---
# Running the notebooks

To install the necessary software, I recommend doing so in a Python
virtual environment. We need Python3. Doing something like:

```shell
$ python3 -m venv sci-comp
$ . sci-comp/bin/activate # Or other script if you use a different shell
$ pip install numpy scipy pandas ipython jupyter
$ cd path/to/repo/material
$ jupyter notebook
```

Will pop up a browser window.

If this results in an `AssertionError` (see
https://github.com/jupyter/notebook/issues/4937), try installing an
older version of jupyter-client in the virtual environment:

```shell
$ pip install jupyter-client==5.3.1
```
