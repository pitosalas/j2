# Coding Principles

These principles apply to all code written in this project.

## LLM
- To save tokens dont be verbose. Dont waste words. Dont use noise words. Dont flatter.

## Testing
- Each feature must have at least one test.

## Python
- Use version 3.10 or later
- Use type annotations sparingly
- Dont use relative imports
- Keep all imports at the top of the file
- Give variables, modules, functions intention revealing names
- Use f" strings whenever possible

## Exception and error handling
- No need to test every exception
- It's ok for unusual situations to have the program just crash

## Documentation
- all functions and methods should have no more than 1-2 lines of comment at the top

## Naming
- Better have a good name for a function so it doesnt require any block comment
- the app generated will have the same name as the top directory

## Code Review
- there shall be a minimum of code duplication
- there shall be a minimum of contnet duplication
- program files shall not be more than 500 lines long
- functions and methods shall not be more than 30 lines long
- functions shall be relatively self contained and have meaningful names
- functions should not have more than 4 parameters
- use classes and objects to save shared state
- ifs should not be nested more than two times
- 
  
## Packaging
- use uv for all packaging, virtual environments etc
- all code goes into a subfolder with the same name as the overall package name
- Dont put on PyPi

