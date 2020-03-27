# Python-Googlefit
Access Google Fit from Python

## Virtual environment

Create a Virtualenv with:

```shell script
python3 -m venv env
```

Python on Windows usually does not insert `python.exe` 
into the `PATH`. In this case you have to supply the
whole path to your `python.exe` in the command above.
The parameters stay the same.

Activate it on Windows with:

```shell script
env\Scripts\activate.bat
```

On Linux and MacOS use `source`:

```bash
source env/bin/activate
``` 

## Dependencies

It is always a good idea to update `pip` and `wheel`:

```shell script
pip install -U pip wheel
```

Install the dependencies using `requirements.txt`:

```shell script
pip install -r requirements.txt
```

## Run

Just execute:

```shell script
python fit.py
```
