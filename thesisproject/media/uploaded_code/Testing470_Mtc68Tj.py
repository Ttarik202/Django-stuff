def foo(x,y):
  if x>y:
   result = x -y
  else:
    result= y - x
 
  print ("Difference is",result)
  return result

class Bar:
    def __init__(self,items):
         self.items = items
    def process(self):
      for i in self.items:
        if i % 2 ==0:
         self.items.remove(i)
    return self.items

def main():
    numbers=[1,2,3,4,5]
    foo(10,2)
    b=Bar(numbers)
    processed=b.process()
    print("Processed list:", processed)

main()
