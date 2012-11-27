# Tranporter 0.1.0 alpha

**Transporter** is a Python library that provides a consistent API for 
navigating FTP, SSH, local file systems, and more.

### Initialization

Transporter instances are easily created from URI string or an object 
compatible with the urlparse.ParseResult interface.

```python
from transporter import Transporter
ftp = Transporter('ftp://user:pword@example.com/initial/path/')
```

### Interface

The basic interface for Transporter objects should be familiar to anyone with 
basic experience navigating the *nix command line.

Transporter.**cd**(path)
    change directory to *path*

Transporter.**pwd**()
    print current working directory

Transporter.**mv**(source, destination)
    move a file or folder from *source* to *destination*

Transporter.**mkdir**(path)
    create a new directory

Transporter.**rmdir**(path)
    delete directory at *path*

Transporter.**rm**(path)
    delete file at *path*

```python
from transporter import
local = Transporter('file:///Users/josh')
local.cd('Desktop')
print local.pwd()  # /Users/josh/Desktop
local.mkdir('new_folder')
local.rmdir('new_folder')
```

Additionally, Transporter objects provide the following methods for creating and accessing file data:

Transporter.**get**(path)
    Retrieve a file object located at *path*

Transporter.**put**(data, path)
    Creates a new file located at *path* that contains *data*

