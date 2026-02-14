import asyncio
import websocket
import json
from order_book import OrderBook
from display import BookDisplay


def on_message(ws, message):
    data = json.loads(message)
    orderBook.update(
            bid_updates=[(float(bid[0]), float(bid[1])) for bid in data.get('b', [])],
            ask_updates=[(float(ask[0]), float(ask[1])) for ask in data.get('a', [])]
        )
    tick = orderBook.to_tick()
    display.render(orderBook, tick)

def on_open(ws):
    print("WS conneciton openeed")
    subscribe_message = { 
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@depth@100ms",
        ],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))

def on_ping(ws, message):
    print(f"Received ping: {message}")
    ws.send(message, websocket.ABNF.OPCODE_PONG)
    print(f"Sent pong: {message}")

if __name__ == "__main__":
    socket = "wss://stream.binance.com:9443/ws"
    orderBook = OrderBook()
    orderBook.symbol = "BTCUSDT"
    display = BookDisplay()
    display.start()
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_ping=on_ping)
    try:
        ws.run_forever()
    finally:
        display.stop()
