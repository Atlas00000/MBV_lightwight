//+------------------------------------------------------------------+
//|                                                          MBV.mq5 |
//|  BB + RSI + ATR risk. v4.32: defaults = Profiles/Tester/           |
//|  "MBV v4.31 PF.set" (validated wide backtest).                   |
//+------------------------------------------------------------------+
#property strict
#property version   "4.32"

#include <Trade/Trade.mqh>

enum ENUM_TOUCH
  {
   TOUCH_CLOSE=0,
   TOUCH_WICK=1
  };

input ENUM_TIMEFRAMES InpTF=PERIOD_M5;
input int      InpMagic=26050901;
input bool     InpNewBarOnly=true;

input int      InpBBPeriod=20;
input double   InpBBDev=2.0;
input int      InpRSIPeriod=14;
input double   InpRsiBuyBelow=38.0;
input double   InpRsiSellAbove=63.0;
input bool     InpRequireRsi=true;

input bool     InpLongStricterRsi=false;
input double   InpRsiBuyLongMax=33.0;
input bool     InpLongRequireRsiUp=false;
input bool     InpLongRequireBullBar=false;
input bool     InpLongRequireDiPlus=false;

input ENUM_TOUCH InpTouch=TOUCH_WICK;
input double   InpNearBandATR=0.03;

input bool     InpUseTrendFilter=true;
input ENUM_TIMEFRAMES InpTrendTF=PERIOD_M10;
input int      InpTrendEMA=20;

input bool     InpUseAdxFilter=true;
input int      InpAdxPeriod=14;
input double   InpMaxAdx=24.0;

input int      InpMaxSpreadPoints=40;
input int      InpMinBarsSinceEntry=3;
input int      InpMaxPos=2;

input int      InpATRPeriod=14;
input double   InpSLAtrMult=1.2;
input double   InpRR=1.5;

input double   InpLots=0.01;
input int      InpSlippage=30;

CTrade g_trade;
int      g_bb=-1;
int      g_rsi=-1;
int      g_atr=-1;
int      g_ma=-1;
int      g_adx=-1;
datetime g_bar=0;
int      g_lastTradeBars=0;

double Clamp(const double v,const double lo,const double hi)
  {
   if(v<lo) return lo;
   if(v>hi) return hi;
   return v;
  }

void FillMode()
  {
   long f=SymbolInfoInteger(_Symbol,SYMBOL_FILLING_MODE);
   if((f&SYMBOL_FILLING_FOK)==SYMBOL_FILLING_FOK) g_trade.SetTypeFilling(ORDER_FILLING_FOK);
   else if((f&SYMBOL_FILLING_IOC)==SYMBOL_FILLING_IOC) g_trade.SetTypeFilling(ORDER_FILLING_IOC);
   else g_trade.SetTypeFilling(ORDER_FILLING_RETURN);
  }

bool Stops(const bool buy,const double entry,const double slIn,const double tpIn,double &sl,double &tp)
  {
   int st=(int)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL);
   int fr=(int)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_FREEZE_LEVEL);
   double d=(st+fr)*_Point;
   if(d<_Point*5.0) d=_Point*10.0;
   sl=NormalizeDouble(slIn,_Digits);
   tp=NormalizeDouble(tpIn,_Digits);
   if(buy)
     {
      if(entry-sl<d) sl=NormalizeDouble(entry-d,_Digits);
      if(tp-entry<d) tp=NormalizeDouble(entry+d,_Digits);
     }
   else
     {
      if(sl-entry<d) sl=NormalizeDouble(entry+d,_Digits);
      if(entry-tp<d) tp=NormalizeDouble(entry-d,_Digits);
     }
   return true;
  }

int OpenCount()
  {
   int n=0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      if(!PositionSelectByTicket(PositionGetTicket(i))) continue;
      if((int)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      if(PositionGetString(POSITION_SYMBOL)==_Symbol) n++;
     }
   return n;
  }

bool NewBar()
  {
   if(!InpNewBarOnly) return true;
   datetime t=iTime(_Symbol,InpTF,0);
   if(t<=0) return false;
   if(t==g_bar) return false;
   g_bar=t;
   return true;
  }

bool Buf(const int h,const int b,const int sh,double &v)
  {
   double d[];
   ArraySetAsSeries(d,true);
   if(CopyBuffer(h,b,sh,1,d)!=1) return false;
   v=d[0];
   return true;
  }

double LotNorm(double x)
  {
   double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   double mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   x=MathFloor(x/st)*st;
   return Clamp(x,mn,mx);
  }

bool TrendAllowsBuy(const double emaTrend,const double closeTrend)
  {
   return(closeTrend>emaTrend);
  }

bool TrendAllowsSell(const double emaTrend,const double closeTrend)
  {
   return(closeTrend<emaTrend);
  }

bool LongDiPlusDominant()
  {
   if(g_adx<0) return true;
   double pdi=0.0,mdi=0.0;
   if(!Buf(g_adx,1,1,pdi) || !Buf(g_adx,2,1,mdi)) return false;
   return(pdi>mdi);
  }

bool LongRsiTurningUp()
  {
   double rv[];
   ArraySetAsSeries(rv,true);
   if(CopyBuffer(g_rsi,0,1,2,rv)!=2) return false;
   return(rv[0]>rv[1]);
  }

void TryTrade()
  {
   if(Bars(_Symbol,InpTF)<InpBBPeriod+5) return;

   const int sp=(int)SymbolInfoInteger(_Symbol,SYMBOL_SPREAD);
   if(InpMaxSpreadPoints>0 && sp>InpMaxSpreadPoints) return;

   if(InpMinBarsSinceEntry>0 && g_lastTradeBars>0)
     {
      const int b=Bars(_Symbol,InpTF);
      if(b>0 && (b-g_lastTradeBars)<InpMinBarsSinceEntry) return;
     }

   double up=0,lo=0,rsi=0,atr=0;
   if(!Buf(g_bb,1,1,up) || !Buf(g_bb,2,1,lo)) return;
   if(!Buf(g_rsi,0,1,rsi) || !Buf(g_atr,0,1,atr) || atr<=0.0) return;

   if(InpUseAdxFilter && g_adx>=0)
     {
      double adx=0.0;
      if(!Buf(g_adx,0,1,adx)) return;
      if(adx>InpMaxAdx) return;
     }

   double emaTr=0.0;
   double clsTr=0.0;
   if(InpUseTrendFilter && g_ma>=0)
     {
      if(!Buf(g_ma,0,1,emaTr)) return;
      double ct[];
      ArraySetAsSeries(ct,true);
      if(CopyClose(_Symbol,InpTrendTF,1,1,ct)!=1) return;
      clsTr=ct[0];
     }

   const double k=MathMax(0.0,InpNearBandATR);
   const double loTrig=lo+k*atr;
   const double upTrig=up-k*atr;

   const double c=iClose(_Symbol,InpTF,1);
   const double hi=iHigh(_Symbol,InpTF,1);
   const double lw=iLow(_Symbol,InpTF,1);
   if(c<=0.0) return;

   bool touchBuy=(InpTouch==TOUCH_WICK) ? (lw<=loTrig) : (c<=loTrig);
   bool touchSell=(InpTouch==TOUCH_WICK) ? (hi>=upTrig) : (c>=upTrig);

   const double buyRsiMax=(InpRequireRsi && InpLongStricterRsi) ? InpRsiBuyLongMax : InpRsiBuyBelow;
   const bool rsiBuy=!InpRequireRsi || (rsi<buyRsiMax);
   const bool rsiSell=!InpRequireRsi || (rsi>InpRsiSellAbove);

   bool buy=touchBuy && rsiBuy;
   bool sell=touchSell && rsiSell;

   if(buy && InpLongRequireRsiUp && !LongRsiTurningUp()) buy=false;
   if(buy && InpLongRequireBullBar)
     {
      const double o1=iOpen(_Symbol,InpTF,1);
      if(c<=o1) buy=false;
     }
   if(buy && InpLongRequireDiPlus && !LongDiPlusDominant()) buy=false;

   if(InpUseTrendFilter && g_ma>=0)
     {
      if(buy && !TrendAllowsBuy(emaTr,clsTr)) buy=false;
      if(sell && !TrendAllowsSell(emaTr,clsTr)) sell=false;
     }

   if(buy && sell) return;
   if(!buy && !sell) return;
   if(OpenCount()>=InpMaxPos) return;

   const double lots=LotNorm(InpLots);
   if(lots<=0.0) return;

   const double slDist=InpSLAtrMult*atr;
   const double tpDist=slDist*InpRR;
   const double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   const double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   const bool isBuy=buy;

   const double e=isBuy?ask:bid;
   const double s0=isBuy?e-slDist:e+slDist;
   const double t0=isBuy?e+tpDist:e-tpDist;
   double sl,tp;
   Stops(isBuy,e,s0,t0,sl,tp);

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpSlippage);
   const bool ok=isBuy?g_trade.Buy(lots,_Symbol,0.0,sl,tp,"MBV")
                 :g_trade.Sell(lots,_Symbol,0.0,sl,tp,"MBV");
   if(!ok) Print("MBV fail ",g_trade.ResultRetcode());
   else
     {
      g_lastTradeBars=Bars(_Symbol,InpTF);
      Print("MBV ",isBuy?"BUY":"SELL"," RSI=",DoubleToString(rsi,1)," spread=",sp);
     }
  }

int OnInit()
  {
   g_bb=iBands(_Symbol,InpTF,InpBBPeriod,0,InpBBDev,PRICE_CLOSE);
   g_rsi=iRSI(_Symbol,InpTF,InpRSIPeriod,PRICE_CLOSE);
   g_atr=iATR(_Symbol,InpTF,InpATRPeriod);
   if(InpUseTrendFilter)
      g_ma=iMA(_Symbol,InpTrendTF,InpTrendEMA,0,MODE_EMA,PRICE_CLOSE);
   if(InpUseAdxFilter || InpLongRequireDiPlus)
      g_adx=iADX(_Symbol,InpTF,InpAdxPeriod);
   if(g_bb<0||g_rsi<0||g_atr<0) return(INIT_FAILED);
   if(InpUseTrendFilter && g_ma<0) return(INIT_FAILED);
   if((InpUseAdxFilter || InpLongRequireDiPlus) && g_adx<0) return(INIT_FAILED);
   FillMode();
   Print("MBV v4.32 locked | MR ",EnumToString(InpTF)," trend=",EnumToString(InpTrendTF)," EMA",InpTrendEMA,
         " ADX<",InpMaxAdx," SLxATR=",InpSLAtrMult," RSI<",InpRsiBuyBelow,"/>",InpRsiSellAbove);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int r)
  {
   if(g_bb>=0) IndicatorRelease(g_bb);
   if(g_rsi>=0) IndicatorRelease(g_rsi);
   if(g_atr>=0) IndicatorRelease(g_atr);
   if(g_ma>=0) IndicatorRelease(g_ma);
   if(g_adx>=0) IndicatorRelease(g_adx);
  }

void OnTick()
  {
   if(!NewBar()) return;
   TryTrade();
  }
