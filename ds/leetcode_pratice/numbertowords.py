
class solution:
    def __init__(self):
        pass

    def convertnumtoword(self, num):
        one = ["","one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        ten = ["ten","eleven","twelve", "thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
        jump = ["","","twenty", "thirty","forty","fifty","sixty","seventy","eighty","ninety"]
        dinomination = ["hundred", "thousand" , "lakh", "crore"]
        numbers =[]
        word = ""
        strnum = str(num)
        # capture numbers to numbsers array in a reverse order, 100 ,thousands , lakhs ..
        if len(strnum)<=3:
            numbers.append(strnum)
        else:
            numbers.append(strnum[len(strnum)-3:])
            catche = ""
            # in indian number systems number digits are 3 digit : hundred, 2 digit : thousand ...
            for i in reversed(range(len(strnum)-3)):
                catche = strnum[i]+catche
                if len(catche) == 2:
                    numbers.append(catche)
                    catche = ""
            if len(catche) > 0:
                numbers.append(catche)
            print(numbers)
        for i in range(len(numbers)):
            temp = numbers[i]
            # for 3 digit denomination comes after 3rd digit and then 2 digit numbers only
            if i == 0 and len(temp) == 3:
                if temp[1] == "1":
                    word = one[int(temp[0])] + " " + dinomination[i] + " " + ten[int(temp[2])] + " ," + word
                else:
                    word = one[int(temp[0])] + " " + dinomination[i] + " " + jump[int(temp[1])] + " " + one[int(temp[2])] + " ," + word
            elif i == 0 and len(temp) < 3:
                if temp[1] == "1":
                    word = ten[int(temp[1])] + " ," + word
                else:
                    word = jump[int(temp[0])] + " " + one[int(temp[1])] + " ," + word
            # for 2 digit denomination comes after entire word only.
            elif len(temp) == 2:
                if temp[1] == '1':
                    word = ten[int(temp[0])] + " " + dinomination[i] + " ," + word
                else:
                    word = jump[int(temp[0])] + " " + one[int(temp[1])] + " " + dinomination[i] + " ," + word
            else:
                word = one[int(temp[0])] + " " + dinomination[i] + " ," + word

        print(word)



obj = solution()
obj.convertnumtoword(11)