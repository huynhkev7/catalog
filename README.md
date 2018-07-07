# Project 3: App Catalog
This python program runs an item catalog application that provides the user the ability to view a list
of items within a variety of categories. The application provides an authentication system allowing users
to register in the application. Once registered, users can add, edit, and delete their own items.

This project is an assignment for the [Udacity Full Stack Web Developer Nanodegree course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004). 
## Prequisites
In order to run project, the following steps will need to be done.
### Installing Python
Python 2.x is required to be installed. Link to download Python can be found [here](https://www.python.org/downloads/).
### Installing the Virtual Machine
VirtualBox is the software that actually runs the virtual machine. You can download it [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.
### Installing Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. You can download it [here](https://www.vagrantup.com/downloads.html). Install the version for your operating system.
### Download the VM configuration
Download the VM configuration by forking or cloning the Udacity [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm)
## How to Use
1. Clone this repository and place the project inside the ```fullstack-nanodegree-vm/vagrant/catalog``` directory.
2. Launch the terminal and ```cd``` into the ```fullstack-nanodegree-vm/vagrant``` directory.
3. Run the command ```vagrant up```. This will download the Linux operating system and install it.
4. When completed, run ```vagrant ssh``` to login into the VM.
5. ```cd``` into ```/vagrant/catalog```
6. Run the command ```python setup_database.py```
7. Run the command ```python populate_database.py```
8. Run the app with the following command ```python app.py```
9. Launch your web browser and navigate to [http://localhost:5000/](http://localhost:5000/)
## Authors
Created by Kevin Huynh