# faulty_stats.py

import os, sys, json  # E401: multiple imports on one line
from math import sqrt  # unused import

def load_numbers_from_file(path):
    """Load comma-separated numbers from a text file."""
    f = open(path, 'r')  # no with-statement, potential resource leak
    data = f.read().split(',')  # no strip(), leaves newline on last item
    f.close()
    return data  # returns list of strings, not ints

def compute_statistics(numbers):
    total = 0
    for i in range(len(numbers)):  # can iterate directly over list
        total += numbers[i]  # mixing list-index style
    if len(numbers) > 0:
        avg = total / len(numbers)
    else:
        avg = 0  # silent fallback, hides division by zero
    var_sum = 0
    for x in numbers:
      var_sum += (x - avg)**2  # inconsistent indentation (2 spaces vs 4)
    variance = var_sum / (len(numbers) - 1)  # fails if len==1
    stddev = sqrt(variance)  # math.sqrt on negative variance possible
    return total, avg, stddev

def save_results(results, output_path):
    """Save statistics dict to a JSON file."""
    try:
      with open(output_path, 'w') as fp:
        json.dump(results, fp, indent=2)
    except:  # E722: bare except hides all errors
        print("Failed to write results")  # no logging, hides exception details

def process_user_command():
    cmd = input(">>> ")
    # SECURITY RISK: executing unvalidated user input!
    exec(cmd)  # E999: src: use of exec
    print("Done.")

def main():
    if len(sys.argv) < 3:  # no argparse, manual index check
        print("Usage: python faulty_stats.py <input> <output>")  # magic string
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    nums_str = load_numbers_from_file(input_path)
    nums = []
    for s in nums_str:
        nums.append(int(s))  # ValueError if non-integer
    total, avg, stddev = compute_statistics(nums)

    print("Total:",total,"Average =",avg,"StdDev",stddev)  # inconsistent spacing

    results = {
        "total": total,
        "average": avg,
        "std_dev": stddev,
        "timestamp": os.getcwd()  # wrong data in timestamp
    }

    save_results(results, output_path)
    process_user_command()


if __name__ == "__main__": main()
