/*
 * Prints the result of applying a function over a range of integers
 */

square = \(n) {
  return n*n
}

cube = \(n) {
  return n*n*n
}

print_f_range = \(f, lo, hi) {
  inner = \(n) {
    if n == hi {
      return 0
    } else {
      // Print and recurse on rest
      print(f(n))
      return inner(n + 1)
    }
  }

  return inner(lo)
}

// Prints 0, 1, 4, 9, ..., 81
print_f_range(square, 0, 10)

// Prints 0, 1, 8, ... 729
print_f_range(cube, 0, 10)
