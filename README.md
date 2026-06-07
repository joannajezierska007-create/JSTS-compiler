# JSTS compiler
a javascript/typescript compiler

JSVM - Mini JavaScript/TypeScript VM (Python)

USAGE:
  python jsvm.py run <file1.js> <file2.ts> ...

  python jsvm.py run-folder <folder>

  python jsvm.py help

DESCRIPTION:
  JSVM is a lightweight JavaScript/TypeScript-like interpreter written in Python.

SUPPORTED FEATURES:
  - let variables
  - basic math (+ - * /)
  - print(x)
  - multiple files (shared memory)
  - simple function calls (add(a,b))

EXAMPLES:

  Run one file:
    python jsvm.py run test.js

  Run multiple files:
    python jsvm.py run a.js b.ts c.js

  Run all JS/TS files in a folder:
    python jsvm.py run-folder ./project

NOTES:
  - This is NOT real JavaScript
  - This is a custom interpreter (toy language)
  - TypeScript types are ignored (no type checking)

© 2026 Wojciech Jezierski. All rights reserved.