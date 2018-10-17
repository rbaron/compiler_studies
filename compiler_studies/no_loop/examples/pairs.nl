/*
 * An examples of defining pairs (and sequences) using Chuch pairs
 * https://en.wikipedia.org/wiki/Church_encoding#Church_pairs
 */

// Let's start with simple pairs

// No-Loop's take on `cons`
make_pair = \(a, b) {
  return \(getter) {
    return getter(a, b)
  }
}

get_head = \(pair) {
  return pair(\(a, b) {
    return a
  })
}

get_tail = \(pair) {
  return pair(\(a, b) {
    return b
  })
}

// Define a pair
p1 = make_pair(1, 2)

// Prints 1
print(get_head(p1))

// Prints 2
print(get_tail(p1))

/*
 * Can we define lists based on our pairs?
 */

// Since we don't have a "null" value yet, we can improvise with a "sentinel". This represents the
// "end" of a list
end_of_list = \() {
  return 0
}

make_range = \(lo, hi) {
  inner = \(n) {
    if n == hi {
      return end_of_list
    } else {
      return make_pair(n, inner(n + 1))
    }
  }
  return inner(lo)
}

// Prints the first element of the list and recurses on the rest, until the list is `end_of_list`
print_list = \(lst) {
  if lst == end_of_list {
    return 0
  } else {
    print(get_head(lst))
    return print_list(get_tail(lst))
  }
}

// Let's create a range
range1 = make_range(0, 20)

print('Integers list:')

// Prints 0, 1, 2, ..., 19. Seriously, how cool is that?
print_list(range1)

/*
 * Mapping functions over ranges
 */

map = \(f, lst) {
  if lst == end_of_list {
    return end_of_list
  } else {
    return  make_pair(f(get_head(lst)), map(f, get_tail(lst)))
  }
}

print('Squared numbers:')
// Prints squared numbers: 0, 1, 4, 9, 16...
print_list(map(
  \(n) { return n*n },
  make_range(0, 20)))
