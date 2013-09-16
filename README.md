# Tranporter 0.1

**Transporter** is a Python library that provides a consistent API for 
navigating FTP, SSH, local file systems, and more.

## Helper functions

Tranporter comes with three helper functions for uploading or downloading files: get, put, transport

```python
from transporter import get, put, transport

# Example use
data = get('http://example.com/path/to/file.txt')
put('ftp://josh:password@example.com/path/to/new_file.txt', 'file contents')
transport('http://josh:password@www.example.com/path/to/file.txt',
        '/Users/josh/Desktop/file.txt')
```

## Initializing Transporter objects

Transporter instances are easily created from URI string or an object 
compatible with the urlparse.ParseResult interface.

```python
from transporter import Transporter
ftp = Transporter('ftp://user:pword@example.com/initial/path/')
```

## Transporter object interface

The basic interface for Transporter objects should be familiar to anyone with 
basic experience navigating the *nix command line.

Transporter.<b>cd</b>(<i>path</i>)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;change directory to *path*

Transporter.<b>pwd</b>()<br/>
&nbsp;&nbsp;&nbsp;&nbsp;print current working directory

Transporter.<b>mv</b>(<i>source</i>, <i>destination</i>)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;move a file or folder from *source* to *destination*

Transporter.<b>mkdir</b>(<i>path</i>)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;create a new directory

Transporter.<b>rmdir</b>(path)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;delete directory at *path*

Transporter.<b>rm</b>(path)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;delete file at *path*


```python
from transporter import Transporter
t = Transporter('file:/Users/josh')
t.mkdir('new_folder')
t.cd('new_folder')
t.mkdir('sub_folder')
print t.pwd()  # /Users/josh/new_folder
print t.ls()  # ['sub_folder']
t.mv('sub_folder', 'new_name')
t.rmdir('new_name')

t2 = Transporter('ftp://joshmaker:pa$sw0rd@example.com/folder/')
t2.mkdir('new_folder')
t2.mkdir('new_folder/sub_folder')
t2.ls('new_folder')  # ['sub_folder']
```

Additionally, Transporter objects provide the following methods for creating and accessing file data:

Transporter.<b>get</b>(<i>path</i>)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;Retrieve a file object located at *path*

Transporter.<b>put</b>(<i>data</i>, <i>path</i>)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;Creates a new file located at *path* that contains *data*


```python
from transporter import Transporter
t1 = Transporter('file:/Users/josh')
data = t1.get('local_file.txt')

t2 = Transporter('ftp://joshmaker:pa$sw0rd@example.com/folder/')
t2.put('remote_file.txt', data)
```

**Note:** Transporters for HTTP and HTTPS only support pwd, cd, get, and put
