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
             |  name <CallsArgs>
             |  num
             |  string
             |  <LambDef>

<CallsArgs>  ::= ( <Args> ) <CallsArgs>
             |   $

<Args>      ::= <Expr> <MoreArgs>
             | $

<MoreArgs>  ::= , <Expr> <MoreArgs>
             | $

<LambDef>   ::= \ <ArgsDef> { <Stmts> }

<Return>    ::= return <Expr>

<ArgsDef>   ::= ( <ArgsNames> )

<ArgsNames>  ::= name <MoreNames>
             |  $

<MoreNames> ::= , name <MoreNames>
             |  $


```
