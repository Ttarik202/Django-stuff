def ProcessList(items=[]): 
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    
    unique_items.sort()
    print("Processed items:", unique_items)


ProcessList([3, 2, 3, 1])
