# Second Order Effects Trading Algorithm - QuantConnect
# This algorithm detects primary market events and trades second-order effects

from AlgorithmImports import *
from datetime import timedelta
import json

class SecondOrderEffectsAlgorithm(QCAlgorithm):
    
    def Initialize(self):
        """Initialize the algorithm with data feeds and parameters"""
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)
        
        # Core settings
        self.UniverseSettings.Resolution = Resolution.Minute
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)
        
        # Define supply chain relationships (simplified example)
        self.supply_chains = {
            "AAPL": {
                "suppliers": ["QCOM", "SWKS", "AVGO", "QRVO"],
                "competitors": ["GOOGL", "MSFT", "AMZN"],
                "related": ["FOXC", "LPL", "AAOI"]
            },
            "TSLA": {
                "suppliers": ["PANW", "ALB", "LAC", "LTHM"],
                "competitors": ["F", "GM", "RIVN", "LCID"],
                "related": ["QS", "CHPT", "BLNK"]
            },
            "NVDA": {
                "suppliers": ["TSM", "ASML", "AMAT", "LRCX"],
                "customers": ["MSFT", "GOOGL", "AMZN", "META"],
                "competitors": ["AMD", "INTC"]
            }
        }
        
        # Track primary movers
        self.primary_movers = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]
        
        # Add primary securities
        for ticker in self.primary_movers:
            self.AddEquity(ticker, Resolution.Minute)
        
        # Add all related securities
        all_related = set()
        for chain in self.supply_chains.values():
            for category in chain.values():
                all_related.update(category)
        
        for ticker in all_related:
            try:
                self.AddEquity(ticker, Resolution.Minute)
            except:
                self.Debug(f"Could not add {ticker}")
        
        # Schedule function to check for second-order opportunities
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(9, 45),
            self.DetectSecondOrderEffects
        )
        
        # Risk management
        self.max_positions = 10
        self.position_size = 0.1  # 10% per position
        self.second_order_multiplier = 0.6  # Smaller size for indirect plays
        
        # Track events and positions
        self.active_events = {}
        self.second_order_positions = {}
    
    def OnData(self, data):
        """Process incoming data and look for primary events"""
        
        # Detect significant moves in primary stocks
        for symbol in self.primary_movers:
            if symbol not in data:
                continue
                
            # Check for significant price movement (> 5% intraday)
            if symbol in data.Bars:
                current_price = data[symbol].Close
                daily_return = self.Securities[symbol].Holdings.UnrealizedProfitPercent
                
                # Detect primary event (simplified - would use news in production)
                if abs(daily_return) > 0.05:
                    self.Debug(f"Primary event detected: {symbol} moved {daily_return:.2%}")
                    self.TriggerSecondOrderTrades(symbol, daily_return, data)
    
    def DetectSecondOrderEffects(self):
        """Scheduled function to analyze market for second-order opportunities"""
        
        # Get recent performance of primary movers
        history = self.History(self.primary_movers, 5, Resolution.Daily)
        
        if history.empty:
            return
        
        # Find significant movers
        for symbol in self.primary_movers:
            try:
                symbol_data = history.loc[symbol]
                returns = symbol_data['close'].pct_change()
                
                # If 5-day return > 10%, significant event
                five_day_return = (symbol_data['close'].iloc[-1] / symbol_data['close'].iloc[0]) - 1
                
                if abs(five_day_return) > 0.10:
                    self.Debug(f"Multi-day event: {symbol} moved {five_day_return:.2%} over 5 days")
                    self.AnalyzeSecondOrderOpportunities(symbol, five_day_return)
            except:
                continue
    
    def TriggerSecondOrderTrades(self, primary_symbol, primary_move, data):
        """Execute second-order trades based on primary event"""
        
        if primary_symbol not in self.supply_chains:
            return
        
        chain = self.supply_chains[primary_symbol]
        
        # Logic for second-order effects
        if primary_move > 0:  # Primary stock up
            # Suppliers benefit
            for supplier in chain.get("suppliers", []):
                if data.ContainsKey(supplier):
                    self.ExecuteSecondOrderTrade(
                        supplier, 
                        "LONG", 
                        f"{primary_symbol} rally benefits supplier",
                        confidence=0.7
                    )
            
            # Competitors might suffer
            for competitor in chain.get("competitors", []):
                if data.ContainsKey(competitor):
                    self.ExecuteSecondOrderTrade(
                        competitor,
                        "SHORT",
                        f"{primary_symbol} rally hurts competitor",
                        confidence=0.5
                    )
        
        else:  # Primary stock down
            # Suppliers suffer
            for supplier in chain.get("suppliers", []):
                if data.ContainsKey(supplier):
                    self.ExecuteSecondOrderTrade(
                        supplier,
                        "SHORT", 
                        f"{primary_symbol} decline hurts supplier",
                        confidence=0.6
                    )
            
            # Some competitors might benefit
            for competitor in chain.get("competitors", []):
                if data.ContainsKey(competitor):
                    self.ExecuteSecondOrderTrade(
                        competitor,
                        "LONG",
                        f"{primary_symbol} decline helps competitor",
                        confidence=0.4
                    )
    
    def ExecuteSecondOrderTrade(self, symbol, direction, reason, confidence=0.5):
        """Execute a second-order effect trade with appropriate sizing"""
        
        # Skip if already have position
        if self.Portfolio[symbol].Invested:
            return
        
        # Check position limits
        current_positions = len([x for x in self.Portfolio.Values if x.Invested])
        if current_positions >= self.max_positions:
            return
        
        # Calculate position size based on confidence
        base_size = self.position_size * self.second_order_multiplier
        adjusted_size = base_size * confidence
        
        # Execute trade
        if direction == "LONG":
            self.SetHoldings(symbol, adjusted_size)
            self.Debug(f"Second-order LONG: {symbol} ({reason}) - Size: {adjusted_size:.2%}")
            
            # Set stop loss and take profit
            current_price = self.Securities[symbol].Price
            self.StopMarketOrder(symbol, -self.Portfolio[symbol].Quantity, current_price * 0.95)
            
        elif direction == "SHORT":
            self.SetHoldings(symbol, -adjusted_size)
            self.Debug(f"Second-order SHORT: {symbol} ({reason}) - Size: {adjusted_size:.2%}")
            
            # Set stop loss
            current_price = self.Securities[symbol].Price
            self.StopMarketOrder(symbol, self.Portfolio[symbol].Quantity, current_price * 1.05)
        
        # Track position
        self.second_order_positions[symbol] = {
            "entry_time": self.Time,
            "direction": direction,
            "reason": reason,
            "confidence": confidence
        }
    
    def AnalyzeSecondOrderOpportunities(self, primary_symbol, multi_day_return):
        """Analyze longer-term second-order opportunities"""
        
        if primary_symbol not in self.supply_chains:
            return
        
        chain = self.supply_chains[primary_symbol]
        
        # Look for lagging related stocks
        for category, tickers in chain.items():
            for ticker in tickers:
                try:
                    # Get correlation and recent performance
                    ticker_history = self.History([ticker], 20, Resolution.Daily)
                    if ticker_history.empty:
                        continue
                    
                    ticker_return = (ticker_history['close'].iloc[-1] / ticker_history['close'].iloc[-5]) - 1
                    
                    # If primary moved significantly but related hasn't, opportunity exists
                    return_differential = abs(multi_day_return) - abs(ticker_return)
                    
                    if return_differential > 0.05:  # 5% differential
                        direction = "LONG" if multi_day_return > 0 else "SHORT"
                        
                        # Adjust for category
                        if category == "competitors":
                            direction = "SHORT" if direction == "LONG" else "LONG"
                        
                        self.ExecuteSecondOrderTrade(
                            ticker,
                            direction,
                            f"Lagging {category} to {primary_symbol}",
                            confidence=0.6
                        )
                
                except:
                    continue
    
    def OnEndOfDay(self, symbol):
        """End of day cleanup and position management"""
        
        # Check holding periods for second-order positions
        positions_to_close = []
        
        for sym, info in self.second_order_positions.items():
            holding_period = (self.Time - info["entry_time"]).days
            
            # Close positions after 5 days (second-order effects are short-term)
            if holding_period > 5:
                positions_to_close.append(sym)
        
        # Close old positions
        for sym in positions_to_close:
            if self.Portfolio[sym].Invested:
                self.Liquidate(sym)
                self.Debug(f"Closed second-order position: {sym} after 5 days")
                del self.second_order_positions[sym]
    
    def OnOrderEvent(self, orderEvent):
        """Track order execution"""
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug(f"Order filled: {orderEvent.Symbol} - Quantity: {orderEvent.FillQuantity}")
