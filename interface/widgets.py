import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from analysis.core import TechnicalAnalysis

class InteractiveAnalysis:
    def __init__(self):
        self.analyzer = None
        
    def create_widgets(self):
        """Create interactive widgets"""
        self.ticker_input = widgets.Text(
            value='AAPL',
            placeholder='Enter stock symbol',
            description='Ticker:',
            disabled=False
        )
        
        self.period_dropdown = widgets.Dropdown(
            options=['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','max'],
            value='1y',
            description='Period:',
            disabled=False
        )
        
        self.chart_type = widgets.Dropdown(
            options=['Technical', 'Candlestick'],
            value='Technical',
            description='Chart Type:'
        )
        
        self.run_button = widgets.Button(
            description='Analyze',
            button_style='success',
            tooltip='Run analysis'
        )
        
        self.plot_button = widgets.Button(
            description='Plot',
            button_style='info',
            tooltip='Plot results',
            disabled=True
        )
        
        self.output = widgets.Output()
        
        # set up event handlers
        self.run_button.on_click(self.on_run_click)
        self.plot_button.on_click(self.on_plot_click)
        
    def on_run_click(self, b):
        """Handle run button click"""
        with self.output:
            clear_output(wait=True)
            try:
                self.analyzer = TechnicalAnalysis(
                    self.ticker_input.value,
                    self.period_dropdown.value
                ).run_full_analysis()
                
                print(f"✅ Analysis completed for {self.ticker_input.value}")
                self.plot_button.disabled = False
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                self.plot_button.disabled = True
    
    # def on_plot_click(self, b):
    #     """Handle plot button click"""
    #     with self.output:
    #         clear_output(wait=True)
    #         try:
    #             chart_type = self.chart_type.value.lower()
    #             self.analyzer.plot_analysis(chart_type=chart_type)
    #             plt.show()
    #         except Exception as e:
    #             print(f"❌ Plotting error: {str(e)}")
    def on_plot_click(self, b):
        with self.output:
            clear_output(wait=True)
            try:
                self.analyzer.plot_analysis()
                plt.show()
            except Exception as e:
                print(f"❌ Plotting error: {str(e)}")
    
    def display(self):
        """Display the interface"""
        self.create_widgets()
        display(widgets.VBox([
            widgets.HBox([self.ticker_input, self.period_dropdown, self.chart_type]),
            widgets.HBox([self.run_button, self.plot_button]),
            self.output
        ]))