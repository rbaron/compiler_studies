# Grammar for the Add-Mult language

## Original grammar

```
<Expr> ::= <Expr> <Op> <Expr>
        |  number
        |  ( <Expr> )

<Op>   ::= +
        |  *
```

## Grammar with precedence

```
<Expr>   ::= <Term> + <Term>
          |  <Term>

<Term>   ::= <Factor> * <Factor>
          |  <Factor>

<Factor> ::= number
          |  ( <Expr> )
```

## Grammar for LL(1) parsing (`$` represents the empty string)

```
<Expr>   ::= <Term> <Expr'>

<Expr'>  ::= + <Term> <Expr'>
          |  $

<Term>   ::= <Factor> <Term'>

<Term'>  ::= * <Factor> <Term'>
          |  $

<Factor> ::= number
          |  ( <Expr> )
```
