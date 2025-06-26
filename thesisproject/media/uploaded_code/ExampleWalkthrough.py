import math


def calcCircleArea(R):
  area = math.pi * R**2
  return area

def sayHello(name): print("Hello " +name)


def doStuff():
    x = 3
    y=5
    result = calcCircleArea(x)
    sayHello("Alice")
    z = x+y
    print("Sum is",z)


doStuff()
