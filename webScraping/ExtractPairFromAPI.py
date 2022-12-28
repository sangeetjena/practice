import requests, zipfile
from io import BytesIO
import wget
import pandas as pd
import os
import time

class ExtractPairFromAPI:
    def __init__(self):
        self.binanceBaseUrl="https://api.binance.com/api/v3/exchangeInfo"
        self.dataExtractDailyTradeBaseUrl="https://data.binance.vision/data/spot/daily/trades"
        self.extractDate="2022-04-26"
        self.extractFiles=[]
        self.storageFilePath="/Users/sajena/PycharmProjects/practice/resource/"

    def extractAllSymboles(self,venderType):
        if venderType=='BINANCE':
            resp=requests.get(self.binanceBaseUrl).json()
            count=0
            symbolList=[]
            for symbol in resp['symbols']:
                count+=1
                symbolList.append(symbol['symbol'])
                print(symbol['symbol'])
                self.extractFiles.append(self.dataExtractDailyTradeBaseUrl + "/" + symbol['symbol'] + "/" + symbol[
                    'symbol'] + "-trades-" + self.extractDate + ".zip")
            print("total symbols"+ count.__str__())
            print(symbolList)

    def downloadFiles(self):

        #to-do loop to extract all file and place it in single file
        # wget.download(self.extractFiles[0],"biance.zip")
        # cmd= "curl -s "+self.extractFiles[0]+ " -o " +self.storageFilePath+filename
        # print(cmd)
        # os.system(cmd)
        errorFiles=[]
        print(self.extractFiles)
        for file in self.extractFiles:
            print("extrating files - " + file)
            filename = file.split('/')[-1]
            req = requests.get(file)
            with open(self.storageFilePath+filename, 'wb') as output_file:
                if req.content.find("Error"):
                    print("unable to download - "+file)
                    errorFiles.append(file)
                else:
                    output_file.write(req.content)
        erFilePtr=open("errorFileDownload","w")
        for file in errorFiles:
            erFilePtr.write(file+ "\n")
        erFilePtr.close()

    def readZipFile(self):
        aggDf = pd.DataFrame()
        count=0
        errorFiles=[]
        for file in self.extractFiles:
            try:
                df=pd.read_csv(self.storageFilePath+file.split('/')[-1],compression='zip')
                df.columns=['trade Id','price','qty','quoteQty','time','isBuyerMaker','isBestMatch']
                count += 1
                # print(df)
                aggDf=pd.concat([aggDf,df], axis=0)
            except Exception as e:
                print("error reading "+self.storageFilePath+file.split('/')[-1])
                errorFiles.append(self.storageFilePath+file.split('/')[-1])
        print("total file read = "+ count.__str__())
        print(aggDf)
        print(errorFiles)
        aggDf['qty'].sum()
        aggDf.to_csv(self.storageFilePath+"aggregatedResults"+self.extractDate, sep='\t', encoding='utf-8')

binance=ExtractPairFromAPI()
binance.extractAllSymboles("BINANCE")
# binance.downloadFiles()
binance.readZipFile()


