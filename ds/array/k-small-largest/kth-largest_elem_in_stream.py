"""
https://leetcode.com/problems/kth-largest-element-in-a-stream/solutions/5624760/python-heap/

Steps:
We use a min-heap data structure. The idea is to maintain a heap of size k such that the smallest element in the heap is always the kth largest element in the stream. When a new element is added, we compare it to the smallest element in the heap:

If the heap has less than k elements, simply add the new element.
If the heap already has k elements, only add the new element if it is larger than the smallest element in the heap (since we want to maintain the largest k elements).
Explanation:
Initialization (__init__ method):
We initialize the object with k and nums.
We convert nums into a min-heap using heapq.heapify.
If the length of nums is greater than k, we pop elements from the heap until its size is k.
Adding a new element (add method):
If the heap has fewer than k elements, we simply add the new element to the heap.
If the heap has k elements and the new element is larger than the smallest element in the heap (which is the root of the heap), we replace the smallest element with the new element using heapq.heapreplace.
After adding the element, the smallest element in the heap (self.min_heap[0]) is the kth largest element in the stream, so we return it.
Explanation of the iteration:
Initially, the heap is [4, 5, 8] (3 largest elements).
Adding 3 doesn’t change the heap since 3 is smaller than 4.
Adding 5 keeps the heap as [5, 5, 8], so the kth largest element is 5.
Adding 10 changes the heap to [5, 8, 10].
Adding 9 changes the heap to [8, 9, 10].
Adding 4 doesn’t change the heap since 4 is smaller than 8.

"""

class KthLargest:
    import heapq
    def __init__(self, k: int, nums: List[int]):
        self.nums = nums
        self.k = k
        heapq.heapify(self.nums)
        while len(nums)> k:
            heapq.heappop(self.nums)

    def add(self, val: int) -> int:
        heapq.heappush(self.nums, val)
        if len(self.nums)>self.k:
            heapq.heappop(self.nums)
        return self.nums[0]
        


# Your KthLargest object will be instantiated and called as such:
# obj = KthLargest(k, nums)
# param_1 = obj.add(val)
