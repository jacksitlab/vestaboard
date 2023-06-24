# Vestaboard local API client

This repo is for a set of python scripts to access the vestaboard with its local API.

Reference is the [Vestaboard localAPI](https://docs.vestaboard.com/local). Be aware: There is also another API which uses the cloud functionality from vestaboard. Not what these scripts here do.

## How to start

 * create your own config.py with your access data

```python
config ={
    "host":"1.2.3.4",
    "localApiKey":"ABCdEFGhightsadAFsfakjMLSJFOS4123NKFSINz"
}
```


## Usage

Read example
```python
from vestaboard import Vestaboard
from alignment import *
from config import *

vestaboard = Vestaboard(config['host'],config['localApiKey'] ,autocorrectLang=True)

lines = vestaboard.read().decode()
for line in lines:
    print(line)

print("================")
print(vestaboard.read().decode(inline=True))
```

Write example
```python
from vestaboard import Vestaboard
from alignment import *
from config import *

vestaboard = Vestaboard(config['host'],config['localApiKey'] ,autocorrectLang=True)
vestaboard.write("Hier könnte Ihre Werbung stehen!",valign=VerticalAlign.CENTER, halign= HorizontalAlign.CENTER)

```




