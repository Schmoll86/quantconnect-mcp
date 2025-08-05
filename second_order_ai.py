"""
AI-Powered Second Order Effects Detector
Integrates Perplexity Sonar and Claude for advanced market analysis
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

load_dotenv()

class SecondOrderAI:
    """AI system for detecting and analyzing second-order market effects"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.cache = {}  # Simple cache for API responses
        
    async def detect_primary_event(self, news_items: List[Dict]) -> Dict:
        """Use Perplexity to identify primary market-moving events"""
        
        prompt = f"""Analyze these recent market news items and identify the PRIMARY market-moving event.
        
News items:
{json.dumps(news_items, indent=2)}

Identify:
1. The most significant market-moving event
2. Primary ticker affected
3. Event category (earnings, M&A, regulatory, macro, innovation, crisis)
4. Magnitude (1-10 scale)
5. Expected duration of impact

Return as JSON:
{{
    "event_description": "...",
    "primary_ticker": "SYMBOL",
    "category": "...",
    "magnitude": 7,
    "duration_days": 5,
    "timestamp": "2024-XX-XX"
}}"""
        
        response = await self._query_perplexity(prompt)
        return json.loads(response)
    
    async def map_second_order_effects(self, primary_event: Dict) -> Dict:
        """Use Claude to map comprehensive second-order effects"""
        
        prompt = f"""You are an expert market analyst specializing in identifying second-order effects.

Primary Event:
{json.dumps(primary_event, indent=2)}

Analyze and identify ALL second-order effects:

1. SUPPLY CHAIN IMPACTS
   - Direct suppliers (who provides components/services to primary)
   - Direct customers (who buys from primary)
   - Supply chain bottlenecks created

2. COMPETITIVE DYNAMICS
   - Direct competitors (market share shifts)
   - Substitute products/services
   - New entrants enabled/blocked

3. SECTOR ROTATIONS
   - Money flow predictions (where will capital move?)
   - Correlated sectors
   - Inverse correlations

4. OPTIONS MARKET PREDICTIONS
   - Expected volatility changes in related names
   - Likely hedging flows
   - Calendar spread opportunities

5. MACRO IMPLICATIONS
   - Currency impacts
   - Commodity effects
   - Interest rate sensitive sectors

For each affected entity, provide:
{{
    "ticker": "SYMBOL",
    "relationship": "supplier|customer|competitor|correlated|inverse",
    "impact_direction": "positive|negative",
    "impact_magnitude": 0.0-1.0,
    "confidence": 0.0-1.0,
    "time_lag_days": 0-30,
    "rationale": "brief explanation"
}}

Return as JSON with all affected entities grouped by category."""
        
        response = await self._query_claude(prompt)
        return json.loads(response)
    
    async def analyze_options_flow(self, ticker: str, related_tickers: List[str]) -> Dict:
        """Analyze options flow for unusual activity in second-order names"""
        
        prompt = f"""Analyze potential options flow for second-order effect trading.

Primary mover: {ticker}
Related tickers: {related_tickers}

Suggest optimal options strategies for each ticker:
1. If high confidence + short timeframe → ATM calls/puts
2. If moderate confidence → Spreads (vertical, calendar)
3. If correlation play → Pairs (long one, short other)
4. If volatility play → Straddles/strangles

Consider:
- Current IV percentile
- Term structure
- Skew
- Optimal expiration dates

Return structured strategies for each ticker."""
        
        response = await self._query_claude(prompt)
        return json.loads(response)
    
    async def generate_trade_signals(self, second_order_map: Dict) -> List[Dict]:
        """Generate specific trade signals from second-order analysis"""
        
        signals = []
        
        for category, entities in second_order_map.items():
            for entity in entities:
                if entity['confidence'] > 0.6:  # Confidence threshold
                    signal = {
                        'ticker': entity['ticker'],
                        'action': 'BUY' if entity['impact_direction'] == 'positive' else 'SELL',
                        'strategy': self._determine_strategy(entity),
                        'size_multiplier': entity['confidence'] * entity['impact_magnitude'],
                        'time_horizon': entity['time_lag_days'],
                        'stop_loss': 0.05 if entity['confidence'] > 0.8 else 0.03,
                        'take_profit': 0.1 if entity['impact_magnitude'] > 0.7 else 0.07,
                        'rationale': entity['rationale']
                    }
                    signals.append(signal)
        
        return sorted(signals, key=lambda x: x['size_multiplier'], reverse=True)[:10]
    
    def _determine_strategy(self, entity: Dict) -> str:
        """Determine optimal trading strategy based on characteristics"""
        
        if entity['confidence'] > 0.8 and entity['time_lag_days'] < 5:
            return 'DIRECT_EQUITY'
        elif entity['confidence'] > 0.7 and entity['time_lag_days'] < 10:
            return 'OPTIONS_DIRECTIONAL'
        elif entity['relationship'] in ['competitor', 'inverse']:
            return 'PAIRS_TRADE'
        else:
            return 'OPTIONS_SPREAD'
    
    async def _query_perplexity(self, prompt: str) -> str:
        """Query Perplexity Sonar Pro"""
        
        # Check cache
        cache_key = f"perplexity_{hash(prompt)}"
        if cache_key in self.cache:
            if (datetime.now() - self.cache[cache_key]['timestamp']).seconds < 300:
                return self.cache[cache_key]['response']
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "You are a financial analyst. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            result = response.json()["choices"][0]["message"]["content"]
            
            # Cache response
            self.cache[cache_key] = {
                'response': result,
                'timestamp': datetime.now()
            }
            
            return result
    
    async def _query_claude(self, prompt: str) -> str:
        """Query Claude 3.5 Sonnet"""
        
        # Check cache
        cache_key = f"claude_{hash(prompt)}"
        if cache_key in self.cache:
            if (datetime.now() - self.cache[cache_key]['timestamp']).seconds < 300:
                return self.cache[cache_key]['response']
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            result = response.json()["content"][0]["text"]
            
            # Cache response
            self.cache[cache_key] = {
                'response': result,
                'timestamp': datetime.now()
            }
            
            return result


# Example usage
async def main():
    ai = SecondOrderAI()
    
    # Example news items
    news = [
        {
            "headline": "NVIDIA Reports Record Data Center Revenue, Raises Guidance",
            "timestamp": "2024-11-20T16:00:00Z",
            "source": "Reuters"
        }
    ]
    
    # Detect primary event
    primary_event = await ai.detect_primary_event(news)
    print(f"Primary Event: {json.dumps(primary_event, indent=2)}")
    
    # Map second-order effects
    second_order_map = await ai.map_second_order_effects(primary_event)
    print(f"\nSecond-Order Effects: {json.dumps(second_order_map, indent=2)}")
    
    # Generate trade signals
    signals = await ai.generate_trade_signals(second_order_map)
    print(f"\nTrade Signals: {json.dumps(signals, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
