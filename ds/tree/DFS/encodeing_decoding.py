"""
https://leetcode.com/problems/encode-and-decode-strings/

Note: not a tree problem. its simple string problem

"""
class Codec:
    def encode(self, strs: List[str]) -> str:
        """Encodes a list of strings to a single string.
        """
        output = ""
        for word in strs:
            # keep length of string. length could be very large and after converting to string we cn't idnetify what is the index rage we need to look to extract length value. so having a delimeter help us to identify that upto the delimeter we have store integer value, which is length of the string
            output+=str(len(word))+"#"+word
        print(output)
        return output
        

    def decode(self, s: str) -> List[str]:
        """Decodes a single string to a list of strings.
        """
        out = []
        i=0
        while i< len(s):
            print(i, s[i])
            ln=""
            # extract lenght of the string we have store, i.e upto the delimeter value
            while s[i]!='#':
                ln+=s[i]
                i+=1
            ln = int(ln)
            i=i+1
            out.append(s[i:i+ln])
            i=i+ln
        print(out)
        return out
            

# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.decode(codec.encode(strs))
