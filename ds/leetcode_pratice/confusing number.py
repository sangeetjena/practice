"""A confusing number is a number that when rotated 180 degrees becomes a different number with each digit valid.

We can rotate digits of a number by 180 degrees to form new digits.

When 0, 1, 6, 8, and 9 are rotated 180 degrees, they become 0, 1, 9, 8, and 6 respectively.
When 2, 3, 4, 5, and 7 are rotated 180 degrees, they become invalid.
Note that after rotating a number, we can ignore leading zeros.

For example, after rotating 8000, we have 0008 which is considered as just 8.
Given an integer n, return true if it is a confusing number, or false otherwise.



Example 1:


Input: n = 6
Output: true
Explanation: We get 9 after rotating 6, 9 is a valid number, and 9 != 6."""

def find_confusing_number(num):
    # map all rotatable integer
    rotate_num = {1:1, 0:0, 6:9, 9:6, 8:8}
    confusenum = ""
    # check decode value of the integer and rotate it is reverse order
    for x in str(num):
        if int(x) in rotate_num.keys():
            confusenum = str(rotate_num[int(x)]) + confusenum
        else:
            return False
    print(int(confusenum))
    if (num != int(confusenum)):
        return True
    else:
        return False

print(find_confusing_number(600))

