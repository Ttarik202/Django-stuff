def factorial(n: int) -> int:
    """Return the factorial of a non-negative integer n."""
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main():
    try:
        number = int(input("Enter a non-negative integer: "))
        print(f"Factorial of {number} is {factorial(number)}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
