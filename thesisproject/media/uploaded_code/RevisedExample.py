import math

def calc_circle_area(radius: float) -> float:
    """Calculates the area of a circle given its radius.

    Args:
        radius: The radius of the circle.

    Returns:
        The area of the circle.
    Raises: ValueError if radius is negative.

    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    area = math.pi * radius**2
    return area

def say_hello(name: str) -> str:
    """Greets the given name.
    Args:
        name: The name to greet.

    Returns:
        A greeting string
    """
    return f"Hello {name}"


def do_stuff(x: int, y: int, greeter_func) -> None:
    """Performs a series of operations with no return value.
    Args:
        x: First number
        y: Second number
        greeter_func: Function to use for greeting

    Side effects:
        Prints to the console
    """
    result = calc_circle_area(x)
    greeting = greeter_func("Alice")
    print(greeting)
    print(f"The area is: {result}")
    print(f"Sum is {x + y}")


if __name__ == "__main__":
    do_stuff(3, 5, say_hello)