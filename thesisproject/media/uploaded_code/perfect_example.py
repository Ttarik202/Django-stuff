def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def main():
    name = "Alice"
    print(greet(name))

    result = add(5, 3)
    print(f"The sum is: {result}")


if __name__ == "__main__":
    main()
