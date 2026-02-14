from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text


class BookDisplay:
    def __init__(self):
        self.live = Live(refresh_per_second=10)

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()

    def render(self, order_book, tick):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="book"),
            Layout(name="footer", size=3),
        )

        # Header with tick summary
        header_text = Text()
        header_text.append(f"  {tick.symbol}", style="bold white")
        header_text.append(f"   Mid: {tick.mid_price:.2f}", style="bold yellow")
        header_text.append(f"   Spread: {tick.spread:.2f}", style="bold cyan")
        layout["header"].update(Panel(header_text, title="Market Data Feed"))

        # Order book table
        table = Table(show_header=True, header_style="bold", expand=True)
        table.add_column("Bid Qty", justify="right", style="green")
        table.add_column("Bid Price", justify="right", style="bold green")
        table.add_column("Ask Price", justify="left", style="bold red")
        table.add_column("Ask Qty", justify="left", style="red")

        # Get top 10 levels
        bid_keys = list(order_book.bids.keys())
        ask_keys = list(order_book.asks.keys())

        # Bids: highest first (reverse), Asks: lowest first
        top_bids = bid_keys[-10:] if len(bid_keys) >= 10 else bid_keys
        top_bids = list(reversed(top_bids))
        top_asks = ask_keys[:10]

        rows = max(len(top_bids), len(top_asks))
        for i in range(rows):
            bid_price = f"{top_bids[i]:.2f}" if i < len(top_bids) else ""
            bid_qty = f"{order_book.bids[top_bids[i]]:.5f}" if i < len(top_bids) else ""
            ask_price = f"{top_asks[i]:.2f}" if i < len(top_asks) else ""
            ask_qty = f"{order_book.asks[top_asks[i]]:.5f}" if i < len(top_asks) else ""
            table.add_row(bid_qty, bid_price, ask_price, ask_qty)

        layout["book"].update(Panel(table, title="Order Book (Top 10)"))

        # Footer
        footer_text = Text()
        footer_text.append(f"  Best Bid: {tick.bid:.2f} ({tick.bid_qty:.5f})", style="green")
        footer_text.append(f"   |   ", style="dim")
        footer_text.append(f"Best Ask: {tick.ask:.2f} ({tick.ask_qty:.5f})", style="red")
        layout["footer"].update(Panel(footer_text))

        self.live.update(layout)
