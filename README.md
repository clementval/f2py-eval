# f2py-eval

Evaluation of f2py parsing abilities to perform transformation defined in the
CLAW language definition.

The directives that control the transformation flow are defined in this language
definition.

[CLAW language definition](https://github.com/C2SM-RCM/claw-language-definition)

We are currently evaluating the potential of such a translator. The current
development status is the following. Only limited cases have been tested.
- [x] loop-fusion
- [ ] loop-interchange
- [ ] loop-extract
- [ ] loop-vector
- [ ] scalar-replace
- [ ] data


Transformation flow is defined as follows:

*Fortran Code* -> **Preprocessor(1)** -> *Fortran Code* -> **f2py fortran parser
 (2)** -> Pseudo AST -> **claw_c.py (3)** -> *Fortran Code*

###### Transformation process
1. The Fortran code is passed into the preprocessor with the corresponding
flags.
2. The fortran without preprocessing macros is passed into the f2py Fortran
parser. A pseudo AST in memory representation is the output of this step
front-end and produce an intermediate file containing the XcodeML intermediate
representation of the Fortran code. The pseudo AST have some block information
linked with line of codes.
3. The pseudo AST is analyzed and transformation are applied by line of code
