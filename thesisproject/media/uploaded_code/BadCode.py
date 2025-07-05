def fact(n):
 result=1
 for i in range(2,n+1):
  result*=i
 return result

def main():
    x = input("Enter number:")
    x=int(x)
    print("Factorial is",fact(x))

main()
