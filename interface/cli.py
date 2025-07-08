from analysis.core import TechnicalAnalysis
import matplotlib.pyplot as plt

class CommandLineInterface:
    def __init__(self):
        self.analyzer = None
        
    def show_analysis_summary(self):
        """Display detailed analysis results including indicator values"""
        if not self.analyzer or not hasattr(self.analyzer, 'processed_data'):
            print("No analysis results available. Run analysis first.")
            return
            
        data = self.analyzer.processed_data
        perf = getattr(self.analyzer, 'performance', None)
        
        print("\n📊 Technical Indicators:")
        print("="*50)
        # Show last 5 days of key indicators
        print(data[['close', 'sma_20', 'rsi_14', 'bb_upper', 'bb_middle', 'bb_lower']].tail().to_string())
        
        if perf:
            print("\n💰 Performance Metrics:")
            print("="*50)
            print(f"Initial Capital: ${perf['initial_capital']:,.2f}")
            print(f"Final Value: ${perf['final_value']:,.2f}")
            print(f"Total Return: {perf['total_return_pct']:.2f}%")
            print(f"Max Drawdown: {perf['max_drawdown_pct']:.2f}%")
            
            # Show latest signal if available
            if hasattr(self.analyzer, 'signals'):
                last_signal = self.analyzer.signals.iloc[-1]
                signal_type = "BUY" if last_signal['signal'] > 0 else "SELL" if last_signal['signal'] < 0 else "NEUTRAL"
                print(f"\n🚦 Latest Signal: {signal_type} (Score: {last_signal['composite_score']:.2f})")

    def run(self):
        """Run CLI interface"""
        print("🚀 Technical Analysis Tool")
        print("="*50)
        
        while True:
            ticker = input("\nEnter stock symbol (or 'q' to quit): ").strip()
            if ticker.lower() == 'q':
                break
                
            period = input("Time period [1y]: ").strip() or '1y'
            self.analyzer = TechnicalAnalysis(ticker, period)
            
            while True:
                print("\nOptions:")
                print("1. Run full analysis")
                print("2. Plot technical chart")
                print("3. Plot candlestick chart")
                print("4. Show analysis details")
                print("5. Change stock/period")
                print("6. Exit")
                
                choice = input("Select option: ").strip()
                
                try:
                    if choice == '1':
                        print("\n⏳ Running analysis...")
                        self.analyzer.run_full_analysis()
                        print("✅ Analysis completed!")
                        self.show_analysis_summary()
                        
                    elif choice == '2':
                        print("\n📊 Generating technical chart...")
                        self.analyzer.plot_analysis('technical')
                        plt.show()
                        
                    elif choice == '3':
                        print("\n🕯 Generating candlestick chart...")
                        self.analyzer.plot_analysis('candlestick')
                        plt.show()
                        
                    elif choice == '4':
                        self.show_analysis_summary()
                        
                    elif choice == '5':
                        break
                        
                    elif choice == '6':
                        print("\nGoodbye!")
                        return
                        
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    CommandLineInterface().run()

# python -m interface.cli