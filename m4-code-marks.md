# Code Quality and Design Marks.  6/15

# BCH Score: 9/10

# Comments

## Install
- use a  `requirements.txt` to collect dependencies
- don’t include your db in the git repo. Have scaffolding that can reproduce it
- Some of the migrations did not apply properly.

## Design 
- You followed the Django template. 
- While Django Admin is handy, it is not really in the spirit of the course.
- The use of Managers was not well explained. 

## Code quality and BCH 
- the code quality was in general adequate. A few comments:
    + you might want to offload db initialization to a CSV file. That way you separate test data from your code.
- there were a lot of Pylint errors. BCH only gets you so far. Try running a tool like that to see what standard you could be holding yourself too. For examples, see the Google style guide or PEP8. Things like putting variables in functions might be inapplicable in Django, but blank lines etc are relevant.

## Models 
There are only a few models. This seems different than the design docs said. So few domain models mean some of the application will be hard to change. For example, when BCH says you have a long parameter list, that to me suggests you need to refactor the design, or at least think about this.

## Tests
I didn't understand what you were doing here. These seem like integration tests? You didn't use the Django test framework so these will be hard to automate. There are no assertions being checked either.

## Docs
Documentation was little or non-existent.

## Overall
The code a little hard to follow, but organized, largely because Django enforces this. You did a reasonable job following Django's framework. Code quality was low, and the design - and the product - did not show evidence of a lot of thorough design and implementation effort.
