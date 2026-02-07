# withenv

`withenv` is a wrapper program designed to provide a file containing environment variables, like an `.env` file, to a 'wrapped' program. Such as:

```shell
withenv .env.staging some_program
```

## Approach

This project is a **specification-only definition** inspired by [whenwords](https://github.com/dbreunig/whenwords). Rather than providing an implementation, it defines:

- **SPEC.md** — Detailed behavioral specification
- **tests.yaml** — Language-agnostic input/output test cases

Implementations can be created in any language by satisfying the specification and passing the test cases.

## Structure

```
./
├── README.md
├── SPEC.md           # behavioral specification
└── tests.yaml        # test cases (inputs/outputs)
```
