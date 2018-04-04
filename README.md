# User Control Panel

This user panel was written in **Flask** entirely by myself. I've used [Bootstrap 4](https://getbootstrap.com/docs/4.0/getting-started/introduction/) for the styling.  
However, the [Avatar API](https://github.com/Times-0/Avatar/blob/master/Avatar.py) was written by Dote  that I simply implemented in this user control panel.  

I've left comments everywhere in **__ init __**.py  just in case you don't understand something. If you are facing any issues or if you don't understand something you can add me on discord **kevin#2572**  
  
This is free to use and edit but please keep the footer as it is, or if you change the design, include  
- 'Backend code by Kevin'.  
  
For the register, I would suggest using [Ben's](https://gist.github.com/ketnipz/048740d381b454e95afe910fb112ef53)  as it is more complete (activation by email, deletes unactivated accounts and more), and after all, it's  club penguin's create.swf :-). If you are fine with not having activation and such and if you prefer an HTML register then I guess you can use mine.  
  
Credits to Dote for the avatar API and to Ben for his help with SQLAlchemy's ORM.

# Instructions

First of all, you want to setup [houdini](https://github.com/Solero/Houdini) I guess if your intention isn't to modify this to match with your source.

Then you will need a bunch of Packages
- Flask
- Flask-ReCaptcha
- Flask-SQLAlchemy
- Flask-SQLAlchemy-Session
- Pillow
- WTForms
- validate-email
- bcrypt
- requests
- mysql-python
- re

You will then want to take a look at Config.py and edit it to match with your server's installation.

Once you've done all of the steps I listed above which are install the packages by doing
> pip install package-name

And edited the Config.py, you can now run the main file as such and have it run forever :-)
>python __init__.py