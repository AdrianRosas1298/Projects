import requests as req
import pandas as pd
import re
import time
import winsound
from twilio.rest import Client
from bs4 import BeautifulSoup

account_sid = "ACa0a8a3379ce9502d4e36578d0b89d220"
auth_token = "8bf2dd98b936edd099071a91081cc564"
client = Client(account_sid, auth_token)

def StockMarketHealth_Bot():
    global MarketHealth
    global Magnitude
    global MarketStatus
    global SMPC_ResultFloat
    SM_Website = req.get("https://finance.yahoo.com/quote/QQQ?p=QQQ") #QQQ Stock
    SM_soup = BeautifulSoup(SM_Website.content,"html.parser")
    SM_Header = SM_soup.find(id="quote-header-info")
    SM_PercChange = SM_Header.find(class_="Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)")
    if (type(SM_PercChange).__name__ == "NoneType"):
        SM_PercChange = SM_Header.find(class_="Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)")
    SM_PercChangeText = (SM_PercChange).get_text()
    BeginSMPC = (SM_PercChangeText).find("(") + 1
    EndSMPC = (SM_PercChangeText).find(")")
    SMPC_ResultString = SM_PercChangeText[BeginSMPC:EndSMPC]
    SMPC_ResultFloat = float(((SMPC_ResultString.replace("-","")).replace("+","")).replace("%",""))
    if SMPC_ResultString[0] == "-":
        MarketHealth = "unhealthy"
    else:
        MarketHealth = "healthy"
    if SMPC_ResultFloat == 0.00:
        Magnitude = "neutral"
    elif SMPC_ResultFloat <= 0.5:
        Magnitude = "slightly"
    elif SMPC_ResultFloat <= 2.5:
        Magnitude = "moderately"
    elif SMPC_ResultFloat <= 5:
        Magnitude = "significantly"
    else:
        Magnitude = "extremely"
    if Magnitude == "neutral":
        MarketStatus = f"As of today, the stock market is {Magnitude}."
    else:
        MarketStatus = f"As of today, the stock market is {Magnitude} {MarketHealth} at {SMPC_ResultString}."
    print(MarketStatus+ " Have a good trading day.")

df = pd.read_excel("My_Stocks.xlsx", engine="openpyxl")

TickArray = []
UpperLimitArray = []
LowerLimitArray = []
CoinArray = []
CoinUpperLimitArray = []
CoinLowerLimitArray = []

i = 0
while i <= len(df)-1:
    TickArray.append(df["Ticker Symbol"][i])
    UpperLimitArray.append(df["High Limit"][i])
    LowerLimitArray.append(df["Low Limit"][i])
    CoinArray.append(df["Coin Name"][i])
    CoinUpperLimitArray.append(df["Coin High Limit"][i])
    CoinLowerLimitArray.append(df["Coin Low Limit"][i])
    i += 1

def StockAndCryptoScraper():
    global NameComponent
    global CurrentComponent
    global ClosingComponent
    global MarketCapComponent
    global AvgVolumeComponent
    global VolumeComponent
    global RSIComponent
    a = 0
    while a == 0:
        NameComponent = []
        CurrentComponent = []
        ClosingComponent = []
        MarketCapComponent = []
        AvgVolumeComponent = []
        VolumeComponent = []
        RSIComponent = []

        for Tick in TickArray:
            Website = req.get(f"https://finance.yahoo.com/quote/{Tick}?p={Tick}")
            soup = BeautifulSoup(Website.content,"html.parser")
            Current_PriceHeader = soup.find(id="quote-header-info")
            Current_PriceString = (Current_PriceHeader.find(class_="Trsdu(0.3s)")).get_text()
            CurrentPrice = float(Current_PriceString.replace(",",""))

            LeftInfo = soup.find(id="quote-summary")
            LeftString1 = LeftInfo.find(class_="D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b) smartphone_W(100%) smartphone_Pend(0px) smartphone_BdY smartphone_Bdc($seperatorColor)")
            LeftString2 = LeftString1.find_all(class_="Ta(end) Fw(600) Lh(14px)")
            ClosingPrice = float(((LeftString2[0]).get_text()).replace(",",""))
            AvgVolume = float(((LeftString2[7]).get_text()).replace(",",""))
            Volume = float(((LeftString2[6]).get_text()).replace(",",""))

            RightInfo = soup.find(id="quote-summary")
            RightString1 = RightInfo.find(class_="D(ib) W(1/2) Bxz(bb) Pstart(12px) Va(t) ie-7_D(i) ie-7_Pos(a) smartphone_D(b) smartphone_W(100%) smartphone_Pstart(0px) smartphone_BdB smartphone_Bdc($seperatorColor)")
            RightString2 = RightString1.find_all(class_="Ta(end) Fw(600) Lh(14px)")
            MarketCap= float(re.sub("[A-Z]+","",(RightString2[0]).get_text()))

            RSIwebsite = req.get(f"http://www.stockta.com/cgi-bin/analysis.pl?symb={Tick}&table=rsi&mode=table")
            RSIsoup = BeautifulSoup(RSIwebsite.content,"html.parser")
            RSI  = float((RSIsoup.find(class_="borderTd")).get_text())
            
            NameComponent.append(Tick)
            CurrentComponent.append(CurrentPrice)
            ClosingComponent.append(ClosingPrice)
            MarketCapComponent.append(MarketCap)
            AvgVolumeComponent.append(AvgVolume)
            VolumeComponent.append(Volume)
            RSIComponent.append(RSI)

        for Coin in CoinArray:
            CoinSite = req.get(f"https://coinmarketcap.com/currencies/{Coin}/")
            CoinSoup = BeautifulSoup(CoinSite.content,"html.parser")
            ID = CoinSoup.find(id="__next")
            CoinPrice = ID.find(class_="priceValue___11gHJ").get_text()
            CoinFloat = float((CoinPrice.replace("$","")).replace(",",""))
            
            SupportingInfo = ID.find(class_="sc-AxhCb gWdkQy").get_text()
            CoinBeginClosingPrice = (SupportingInfo).find("24h") + 3
            CoinEndClosingPrice = (SupportingInfo).find("%") - 4
            CoinClosingPriceString = SupportingInfo[CoinBeginClosingPrice:CoinEndClosingPrice]
            CoinPlusMinusFloat = float((((CoinClosingPriceString.replace("$","")).replace(",","")).replace("-","")).replace("+",""))
            if CoinClosingPriceString[1] == "-":
                CoinClosingPrice = CoinFloat - CoinPlusMinusFloat
            elif CoinPlusMinusFloat == 0.00:
                CoinClosingPrice = CoinFloat
            else:
                CoinClosingPrice = CoinFloat + CoinPlusMinusFloat
            CoinBeginMC = (SupportingInfo).find("Cap") + 3
            CoinEndMC = (SupportingInfo).find("Market Dominance")
            CoinMCString = SupportingInfo[CoinBeginMC:CoinEndMC]
            CoinMCFloat = float((((CoinMCString.replace("$","")).replace(",","")).replace("-","")).replace("+",""))
            ColorInfo = ID.find(class_="icon-Caret-down")
            if (type(ColorInfo).__name__ == "NoneType"):
                Direction = "Up"
            else:
                Direction = "Down"
            CoinBeginVol = (SupportingInfo).find("Trading Volume") + 18
            CoinEndVol = (SupportingInfo).find("Volume /")
            CoinVolString = SupportingInfo[CoinBeginVol:CoinEndVol]
            CoinVolStringReduced = (CoinVolString).find(".")
            ReducedCoinVolString = CoinVolString[0:CoinVolStringReduced+3]
            CoinVolFloat = float((((ReducedCoinVolString.replace("$","")).replace(",","")).replace("-","")).replace("+",""))
            CoinAVFind = CoinVolString[CoinVolStringReduced+3:-1]
            CoinAVFloat = float((((CoinAVFind.replace("$","")).replace(",","")).replace("-","")).replace("+",""))
            if Direction == "Up":
                CoinAV = CoinVolFloat * ( 1 + (CoinAVFloat/100))
            else:
                CoinAV = CoinVolFloat * (1 - (CoinAVFloat/100))
            DominanceBegin = SupportingInfo.find("Dominance")
            DominanceEnd = SupportingInfo.find("Market Rank")
            DominanceString = SupportingInfo[DominanceBegin+9:DominanceEnd-1]
            RSIequivalent = float(DominanceString)

            NameComponent.append(Coin)
            CurrentComponent.append(CoinFloat)
            ClosingComponent.append(CoinClosingPrice)
            MarketCapComponent.append(CoinMCFloat)
            AvgVolumeComponent.append(CoinAV)
            VolumeComponent.append(CoinVolFloat)
            RSIComponent.append(RSIequivalent)    
            
        df = pd.DataFrame(list(zip(NameComponent, CurrentComponent, ClosingComponent, MarketCapComponent, AvgVolumeComponent, VolumeComponent, RSIComponent)),
                          columns = ["Ticker", "Current Price", "Closing Price", "Market Cap", "Avg. Volume", "Volume","RSI"])


        print(df)
        print("") #Blank Line

        for Tick in TickArray:
            Stock_Indexed_Upper = UpperLimitArray[TickArray.index(Tick)]
            Stock_Indexed_Lower = LowerLimitArray[TickArray.index(Tick)]
            CP = CurrentComponent[TickArray.index(Tick)]
            if CP >= Stock_Indexed_Upper:
                message = client.messages.create( 
                                  from_="+12312726560", 
                                  body =f"Your {Tick} stock is currently ${str(CP)}, which is above your upper limit price of ${Stock_Indexed_Upper}",
                                  to = "+18327053363"
                              )
                winsound.PlaySound("Up.wav", winsound.SND_ASYNC)
                UpperLimitArray[TickArray.index(Tick)] = Stock_Indexed_Upper + (Stock_Indexed_Upper*0.01) #increased the High Limit by 1%
                time.sleep(5)
            if CP <= Stock_Indexed_Lower:
                message = client.messages.create( 
                                  from_="+12312726560", 
                                  body =f"Your {Tick} stock is currently ${str(CP)}, which is below your lower limit price of ${Stock_Indexed_Lower}",
                                  to = "+18327053363"
                              )
                winsound.PlaySound("Down.wav", winsound.SND_ASYNC)
                LowerLimitArray[TickArray.index(Tick)] = Stock_Indexed_Lower - (Stock_Indexed_Lower*0.01) #decreased the Low Limit by 1%
                time.sleep(5)
            time.sleep(1)

            for Coin in CoinArray:
                Coin_Indexed_Upper = CoinUpperLimitArray[CoinArray.index(Coin)]
                Coin_Indexed_Lower = CoinLowerLimitArray[CoinArray.index(Coin)]
                CoinCP = CurrentComponent[CoinArray.index(Coin) + len(TickArray)]
                if CoinCP >= Coin_Indexed_Upper:
                    message = client.messages.create( 
                                      from_="+12312726560", 
                                      body =f"Your {Coin} crypto is currently ${str(CoinCP)}, which is above your upper limit price of ${Coin_Indexed_Upper}",
                                      to = "+18327053363"
                                  )
                    winsound.PlaySound("Up.wav", winsound.SND_ASYNC)
                    CoinUpperLimitArray[CoinArray.index(Coin)] = Coin_Indexed_Upper + (Coin_Indexed_Upper*0.01) #increased the High Limit by 1%
                    time.sleep(5)
                if CoinCP <= Coin_Indexed_Lower:
                    message = client.messages.create( 
                                      from_="+12312726560", 
                                      body =f"Your {Coin} crypto is currently ${str(CoinCP)}, which is below your lower limit price of ${Coin_Indexed_Lower}",
                                      to = "+18327053363"
                                  )
                    winsound.PlaySound("Down.wav", winsound.SND_ASYNC)
                    CoinLowerLimitArray[CoinArray.index(Coin)] = Coin_Indexed_Lower - (Coin_Indexed_Lower*0.01) #decreased the Low Limit by 1%
                    time.sleep(5)
                time.sleep(1)               

        #Clear Arrays
        NameComponent.clear()
        CurrentComponent.clear()
        ClosingComponent.clear()
        MarketCapComponent.clear()
        AvgVolumeComponent.clear()
        VolumeComponent.clear()
        RSIComponent.clear()
            
StockMarketHealth_Bot()
StockAndCryptoScraper()
