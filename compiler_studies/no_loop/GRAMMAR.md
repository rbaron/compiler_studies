# Grammar for the No-Loop language

```
<Goal>      ::= <Stmts>

<Stmts>     ::= <Stmt> <MoreStmts>

<MoreStmts> ::= <Stmt> <MoreStmts>
             |  $

<Stmt>      ::= <IfElse>
             |  <Return>
             |  <Asgn>
             |  <Comment>

<IfElse>    ::= if <Comp> { <Stmts> } else { <Stmts> }

<Return>    ::= return <Expr>

<ArgNames>  ::= name <MoreNames>
             |  $

<MoreNames> ::= , name <MoreAtoms>
             |  $

<Comment>   ::= comment

# Run time check?
<Asgn>      ::= <Comp> <Asng'>

<Asgn'>     ::= = <Comp>
             |  $

<Comp>      ::= <Expr> <Comp'>

<Comp'>     ::= == <Expr>
             |  >= <Expr>
             |  <= <Expr>
             |  $

<Expr>      ::= <Term> <Expr'>

<Expr'>     ::= + <Term> <Expr'>
             |  - <Term> <Expr'>
             |  $

<Term>      ::= <Factor> <Term'>

<Term'>     ::= * <Factor> <Term'>
             |  / <Factor> <Term'>
             |  $

<Factor>    ::= ( <Comp> )
             |  <AtomCalls>

<AtomCalls>  ::= <Atom> <CallsArgs>

<CallsArgs>  ::= ( <Args> ) <CallsArgs>
             |   $

<Atom>      ::= name
             |  num
             |  string
             |  <LambDef>

<Args>      ::= <Expr> <MoreArgs>
             | $

<MoreArgs>  ::= , <Expr> <MoreArgs>
             | $

<LambDef>   ::= \ <ArgsDef> { <Stmts> }

<ArgsDef>   ::= ( <ArgNames> )
```
