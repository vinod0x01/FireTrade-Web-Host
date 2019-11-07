# Flask-ML-Application
A deployable Flask based ML application

### needs
> * create a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) in python.
> * or if you have conda base it's ok to work directly.
> * activate the virtual environment.
> * _clone or download the project_
```bash
git clone https://github.com/pranjalchaubey/Flask-ML-Application.git 
```
> * change directory to project directory

### installing the required libraries
```bash
pip install -r requirements.txt
```

### Running Flask App
Linux
```bash
export FLASK_APP=app.py
flask run
```
Windows 
```bash
set FLASK_APP=app.py
flask run
```

### usage
* initially user needs to signup for the app or login if already signed-up
![login image](/images/s1.png)
![signup image](/images/scrn2.png)
* then user selects 5 stocks from the list.
![select image](/images/s3.png)
* then based on the user's selection, the _Fire Trade AI_ makes the predictions
![predict image](/images/s5.png)

## Contributors

* [Pranjal Chaubey](https://github.com/pranjalchaubey)
* [Vinod](https://github.com/raita0100)
* [Koushik](https://github.com/koushikkolli)
* [Jorge Angles](https://github.com/anglesjo)
* [Abhishek](https://github.com/yossi94)
