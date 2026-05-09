//+------------------------------------------------------------------+
//| MBV_Log.mqh — Milestone 1 structured CSV logging                  |
//+------------------------------------------------------------------+
#ifndef MBV_LOG_MQH
#define MBV_LOG_MQH

#define MBV_LOG_SCHEMA "0.1"
#define MBV_TRK_MAX    16

enum ENUM_MBV_LOG_MODE
  {
   MBV_LOG_ALL_BARS=0,
   MBV_LOG_RAW_OR_EXEC=1,
   MBV_LOG_EXEC_ONLY=2
  };

struct MbvSnap
  {
   datetime bar_time;
   double   o,h,l,c;
   double   bb_u,bb_m,bb_l;
   double   rsi,atr,adx,pdi,mdi;
   double   trend_c,trend_ema;
   int      spread_pts;
   int      touch_b,touch_s;
   int      raw_b,raw_s;
   int      fin_b,fin_s;
  };

struct MbvPosTrk
  {
   bool     used;
   ulong    pos_ticket;
   ulong    pos_id;
   string   signal_id;
   double   peak;
   double   trough;
   datetime t_open;
  };

bool              g_mbv_log_en=false;
bool              g_mbv_log_common=false;
ENUM_MBV_LOG_MODE g_mbv_log_mode=MBV_LOG_RAW_OR_EXEC;
string            g_mbv_log_prefix="MBV_sig_";
string            g_mbv_ea_ver="0";
string            g_mbv_sym="";
int               g_mbv_magic=0;
ENUM_TIMEFRAMES   g_mbv_tf=(ENUM_TIMEFRAMES)0;

int               g_mbv_log_h=-1;
datetime          g_mbv_log_day=0;
ulong             g_mbv_sig_seq=0;

MbvPosTrk         g_mbv_trk[MBV_TRK_MAX];

//+------------------------------------------------------------------+
string MbvNextSignalId()
  {
   g_mbv_sig_seq++;
   return(g_mbv_sym+"_"+IntegerToString((long)TimeCurrent())+"_"+IntegerToString((long)g_mbv_sig_seq));
  }

//+------------------------------------------------------------------+
string MbvSanitizeSym(const string s)
  {
   string r=s;
   StringReplace(r,".","");
   StringReplace(r,"#","");
   StringReplace(r,"/","");
   StringReplace(r,"\\","");
   StringReplace(r,":","");
   StringReplace(r," ","");
   return r;
  }

//+------------------------------------------------------------------+
void MbvLogCloseHandle()
  {
   if(g_mbv_log_h>=0)
     {
      FileClose(g_mbv_log_h);
      g_mbv_log_h=-1;
     }
  }

//+------------------------------------------------------------------+
bool MbvLogOpenForToday()
  {
   const datetime day=iTime(g_mbv_sym,g_mbv_tf,0);
   datetime d0=day;
   if(d0==0) d0=TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(d0,dt);
   const datetime daykey=StringToTime(StringFormat("%04d.%02d.%02d",dt.year,dt.mon,dt.day));
   if(g_mbv_log_h>=0 && daykey==g_mbv_log_day) return true;

   MbvLogCloseHandle();
   g_mbv_log_day=daykey;

   const string fn=g_mbv_log_prefix+MbvSanitizeSym(g_mbv_sym)+"_"+TimeToString(daykey,TIME_DATE)+".csv";
   const int common_flag=g_mbv_log_common?FILE_COMMON:0;
   const bool exists=FileIsExist(fn,common_flag);

   g_mbv_log_h=FileOpen(fn,FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|common_flag,',');
   if(g_mbv_log_h<0)
     {
      Print("MBV_Log: FileOpen failed ",fn," err=",GetLastError());
      return false;
     }
   FileSeek(g_mbv_log_h,0,SEEK_END);
   if(!exists || FileSize(g_mbv_log_h)==0)
     {
      const string hdr="event,signal_id,ea_version,bar_time,symbol,chart_tf,o,h,l,c,bb_u,bb_m,bb_l,rsi,atr,adx,pdi,mdi,trend_c,trend_ema,spread,touch_b,touch_s,raw_b,raw_s,fin_b,fin_s,executed,skip,ord_ret,side,pnl,dur_s,mfe,mae,pos_id,xdeal,schema";
      FileWriteString(g_mbv_log_h,hdr+"\r\n");
      FileWriteString(g_mbv_log_h,"BOOT,INIT,"+g_mbv_ea_ver+",0,"+g_mbv_sym+","+EnumToString(g_mbv_tf)+
                      ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,NONE,0,0,0,0,0,0,"+MBV_LOG_SCHEMA+"\r\n");
     }
   FileFlush(g_mbv_log_h);
   return true;
  }

//+------------------------------------------------------------------+
void MbvLogInit(const bool en,const bool common,const ENUM_MBV_LOG_MODE mode,
                const string prefix,const string ea_ver,const int magic,
                const string sym,const ENUM_TIMEFRAMES tf)
  {
   g_mbv_log_en=en;
   g_mbv_log_common=common;
   g_mbv_log_mode=mode;
   if(StringLen(prefix)>0) g_mbv_log_prefix=prefix;
   g_mbv_ea_ver=ea_ver;
   g_mbv_magic=magic;
   g_mbv_sym=sym;
   g_mbv_tf=tf;
   for(int i=0;i<MBV_TRK_MAX;i++) g_mbv_trk[i].used=false;
   if(g_mbv_log_en) MbvLogOpenForToday();
  }

//+------------------------------------------------------------------+
void MbvLogDeinit()
  {
   MbvLogCloseHandle();
  }

//+------------------------------------------------------------------+
bool MbvLogShouldRow(const MbvSnap &s,const bool executed)
  {
   if(!g_mbv_log_en) return false;
   if(g_mbv_log_mode==MBV_LOG_ALL_BARS) return true;
   if(g_mbv_log_mode==MBV_LOG_EXEC_ONLY) return executed;
   return executed || (s.raw_b!=0) || (s.raw_s!=0);
  }

//+------------------------------------------------------------------+
bool MbvLogShouldRowEx(const MbvSnap &s,const bool executed,const int skip)
  {
   if(!g_mbv_log_en) return false;
   if(g_mbv_log_mode==MBV_LOG_ALL_BARS) return true;
   if(g_mbv_log_mode==MBV_LOG_EXEC_ONLY) return executed;
   if(executed || (s.raw_b!=0) || (s.raw_s!=0)) return true;
   if(skip!=0 && skip!=10) return true;
   return false;
  }

//+------------------------------------------------------------------+
void MbvLogSignalRow(const MbvSnap &s,const bool executed,const int skip,
                     const int ord_ret,const string side,
                     const string signal_id)
  {
   if(!MbvLogShouldRowEx(s,executed,skip)) return;
   if(!MbvLogOpenForToday()) return;
   const string sid=(StringLen(signal_id)==0)?"":signal_id;
   FileWrite(g_mbv_log_h,
             "SIGNAL",
             sid,
             g_mbv_ea_ver,
             (long)s.bar_time,
             g_mbv_sym,
             EnumToString(g_mbv_tf),
             s.o,s.h,s.l,s.c,
             s.bb_u,s.bb_m,s.bb_l,
             s.rsi,s.atr,s.adx,s.pdi,s.mdi,
             s.trend_c,s.trend_ema,
             s.spread_pts,
             s.touch_b,s.touch_s,
             s.raw_b,s.raw_s,
             s.fin_b,s.fin_s,
             executed?1:0,
             skip,
             ord_ret,
             side,
             0.0,0,0.0,0.0,0,0,
             MBV_LOG_SCHEMA);
   FileFlush(g_mbv_log_h);
  }

//+------------------------------------------------------------------+
void MbvLogOutcomeRow(const string signal_id,const ulong pos_id,const double pnl,
                      const int dur_s,const double mfe,const double mae,
                      const ulong xdeal)
  {
   if(!g_mbv_log_en) return;
   if(!MbvLogOpenForToday()) return;
   FileWrite(g_mbv_log_h,
             "OUTCOME",
             signal_id,
             g_mbv_ea_ver,
             (long)0,
             g_mbv_sym,
             EnumToString(g_mbv_tf),
             0.0,0.0,0.0,0.0,
             0.0,0.0,0.0,
             0.0,0.0,0.0,0.0,0.0,
             0.0,0.0,
             0,
             0,0,0,0,0,0,
             0,0,0,
             "NONE",
             pnl,(long)dur_s,mfe,mae,pos_id,xdeal,
             MBV_LOG_SCHEMA);
   FileFlush(g_mbv_log_h);
  }

//+------------------------------------------------------------------+
int MbvTrkFindFree()
  {
   for(int i=0;i<MBV_TRK_MAX;i++)
      if(!g_mbv_trk[i].used) return i;
   return -1;
  }

//+------------------------------------------------------------------+
int MbvTrkFindByPosId(const ulong pid)
  {
   for(int i=0;i<MBV_TRK_MAX;i++)
      if(g_mbv_trk[i].used && g_mbv_trk[i].pos_id==pid) return i;
   return -1;
  }

//+------------------------------------------------------------------+
ulong MbvPosTicketFromPosId(const ulong pid)
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      const ulong t=PositionGetTicket(i);
      if(!PositionSelectByTicket(t)) continue;
      if(PositionGetString(POSITION_SYMBOL)!=g_mbv_sym) continue;
      if((int)PositionGetInteger(POSITION_MAGIC)!=g_mbv_magic) continue;
      if((ulong)PositionGetInteger(POSITION_IDENTIFIER)==pid) return t;
     }
   return 0;
  }

//+------------------------------------------------------------------+
bool MbvPosIdStillOpen(const ulong pid)
  {
   return(MbvPosTicketFromPosId(pid)!=0);
  }

//+------------------------------------------------------------------+
void MbvTrackRegister(const string signal_id,const ulong deal_ticket)
  {
   if(!HistoryDealSelect(deal_ticket)) return;
   if(HistoryDealGetString(deal_ticket,DEAL_SYMBOL)!=g_mbv_sym) return;
   if((int)HistoryDealGetInteger(deal_ticket,DEAL_MAGIC)!=g_mbv_magic) return;
   const ulong pid=(ulong)HistoryDealGetInteger(deal_ticket,DEAL_POSITION_ID);
   ulong pt=MbvPosTicketFromPosId(pid);
   const int ix=MbvTrkFindFree();
   if(ix<0) return;
   g_mbv_trk[ix].used=true;
   g_mbv_trk[ix].pos_ticket=pt;
   g_mbv_trk[ix].pos_id=pid;
   g_mbv_trk[ix].signal_id=signal_id;
   g_mbv_trk[ix].peak=0.0;
   g_mbv_trk[ix].trough=0.0;
   g_mbv_trk[ix].t_open=(datetime)HistoryDealGetInteger(deal_ticket,DEAL_TIME);
  }

//+------------------------------------------------------------------+
void MbvTrackOnTick()
  {
   if(!g_mbv_log_en) return;
   for(int k=0;k<MBV_TRK_MAX;k++)
     {
      if(!g_mbv_trk[k].used) continue;
      ulong t=g_mbv_trk[k].pos_ticket;
      if(t==0)
        {
         t=MbvPosTicketFromPosId(g_mbv_trk[k].pos_id);
         if(t>0) g_mbv_trk[k].pos_ticket=t;
        }
      if(t==0 || !PositionSelectByTicket(t))
         continue;
      const double pl=PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      if(pl>g_mbv_trk[k].peak) g_mbv_trk[k].peak=pl;
      if(pl<g_mbv_trk[k].trough) g_mbv_trk[k].trough=pl;
     }
  }

//+------------------------------------------------------------------+
void MbvOnTradeTransaction(const MqlTradeTransaction &trans,
                           const MqlTradeRequest &request,
                           const MqlTradeResult &result)
  {
   if(!g_mbv_log_en) return;
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD) return;
   const ulong dtk=trans.deal;
   if(!HistoryDealSelect(dtk)) return;
   if(HistoryDealGetString(dtk,DEAL_SYMBOL)!=g_mbv_sym) return;
   if((int)HistoryDealGetInteger(dtk,DEAL_MAGIC)!=g_mbv_magic) return;
   if((ENUM_DEAL_ENTRY)HistoryDealGetInteger(dtk,DEAL_ENTRY)!=DEAL_ENTRY_OUT) return;

   const ulong pid=(ulong)HistoryDealGetInteger(dtk,DEAL_POSITION_ID);
   const int ix=MbvTrkFindByPosId(pid);
   const double pnl=HistoryDealGetDouble(dtk,DEAL_PROFIT)+HistoryDealGetDouble(dtk,DEAL_SWAP)+HistoryDealGetDouble(dtk,DEAL_COMMISSION);
   const int dur=(ix>=0)?(int)(TimeCurrent()-g_mbv_trk[ix].t_open):0;
   double mfe=0,mae=0;
   string sid="";
   if(ix>=0)
     {
      mfe=g_mbv_trk[ix].peak;
      mae=g_mbv_trk[ix].trough;
      sid=g_mbv_trk[ix].signal_id;
     }
   MbvLogOutcomeRow(sid,pid,pnl,dur,mfe,mae,trans.deal);
   if(ix>=0 && !MbvPosIdStillOpen(pid))
      g_mbv_trk[ix].used=false;
  }

#endif // MBV_LOG_MQH
