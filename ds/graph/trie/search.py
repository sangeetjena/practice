"""
https://leetcode.com/problems/search-suggestions-system/?envType=problem-list-v2&envId=trie

Note: create inverted index and search


"""
class Solution:
    def suggestedProducts(self, products: List[str], searchWord: str) -> List[List[str]]:
        inverted_index = {}
        results = []
        for product in products:
            for i in range(len(product)):
                if product[:i+1] in inverted_index.keys():
                    inverted_index[product[:i+1]].append(product)
                else:
                    inverted_index[product[:i+1]] = [product]
        for i in range(len(searchWord)):
            if searchWord[:i+1] in inverted_index.keys():
                results.append(sorted(inverted_index[searchWord[:i+1]])[:3])
            else:
                results.append([])
        print(results)
        return results




        
