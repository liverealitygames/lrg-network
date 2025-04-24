# lrg-network
## Installation

### Prerequisites

#### 1. Install Python
Install ```python-3.12.3```. Follow the steps from the below reference document based on your Operating System.
Reference: [https://docs.python-guide.org/starting/installation/](https://docs.python-guide.org/starting/installation/)

#### 2. Clone git repository
Clone this repo:
```bash
git clone ssh://git@github.com:liverealitygames/lrg-network.git
```

If you aren't already set up to use SSH, follow these instructions:
1. [Generating SSH Keys](https://help.github.com/articles/generating-ssh-keys) and add your generated key in Account Settings -> SSH Keys
2. [Cloning with SSH](https://help.github.com/articles/which-remote-url-should-i-use#cloning-with-ssh)


#### 3. Setup virtual environment
Set up a virtual environment for this project. The following command will create a virtual environment named `lrgenv`. You can name your virtual environment whatever you'd like, but the rest of this readme will use `lrgvenv`. A distinct name helps make sure you're running this project out of the correct virtual environment.
```bash
cd lrg-network
python3 -m venv lrgvenv
```

Start your virtual environment by running:
```bash
source lrgvenv/bin/activate
```

#### 4. Install requirements
Make sure you have the latest version of pip and then install the project's dependencies, including Django, as well as dependencies for development and testing:
```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

#### 5. Run the server
```bash
# Make migrationsp
python manage.py makemigrations
python manage.py migrate

# Run the server
python manage.py runserver 0:8001

# your server is up on port 8001
```
Try opening [http://localhost:8001](http://localhost:8001) in the browser.
Now you are good to go.
