package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/jackc/pgx/v5"
)

// package-level variable — all handlers in this package can access it
var db *pgx.Conn

func main() {
	var err error
	db, err = connectToDatabase() // = not := because db is already declared above
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close(context.Background())

	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/candles", candlesHandler)

	fmt.Println("Starting REST API on port 8080...")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal(err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func candlesHandler(w http.ResponseWriter, r *http.Request) {
	symbol := r.URL.Query().Get("symbol")
	if symbol == "" {
		symbol = "BTCUSDT"
	}

	limit := r.URL.Query().Get("limit")
	if limit == "" {
		limit = "100"
	}

	if !isNumber(limit) {
		http.Error(w, "invalid limit value", http.StatusBadRequest)
		return
	}

	offset := r.URL.Query().Get("offset")
	if offset == "" {
		offset = "0"
	}
	
	if !isNumber(offset) {
		http.Error(w, "invalid offset value", http.StatusBadRequest)
		return
	}

	rows, err := db.Query(r.Context(),
		"SELECT symbol, open_time, open_price, high_price, low_price, close_price, volume, close_time, number_of_trades FROM candles WHERE symbol = $1 ORDER BY open_time ASC LIMIT $2 OFFSET $3",
		symbol, limit, offset)
	if err != nil {
		http.Error(w, "database query failed", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	candles := []Candle{}
	for rows.Next() {
		var c Candle
		err := rows.Scan(&c.Symbol, &c.OpenTime, &c.OpenPrice, &c.HighPrice,
			&c.LowPrice, &c.ClosePrice, &c.Volume, &c.CloseTime, &c.NumberOfTrades)
		if err != nil {
			http.Error(w, "failed to read row", http.StatusInternalServerError)
			return
		}
		candles = append(candles, c)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(CandleResponse{
		Data:   candles,
		Limit:  limit,
		Offset: offset,
		Count:  len(candles),
	})
}

func connectToDatabase() (*pgx.Conn, error) {
	conn, err := pgx.Connect(context.Background(), "postgres://postgres:password@localhost:6543/postgres")
	if err != nil {
		return nil, fmt.Errorf("unable to connect to database: %w", err)
	}
	fmt.Println("Successfully connected to database!")
	return conn, nil
}

func isNumber(s string) bool {
	for _, ch := range s {
		if ch < '0' || ch > '9' {
			return false
		}
	}
	return true
}

type CandleResponse struct {
	Data   []Candle `json:"data"`
	Limit  string   `json:"limit"`
	Offset string   `json:"offset"`
	Count  int      `json:"count"`
}

type Candle struct {
	Symbol         string  `json:"symbol"`
	OpenTime       int64   `json:"open_time"`
	OpenPrice      float64 `json:"open_price"`
	HighPrice      float64 `json:"high_price"`
	LowPrice       float64 `json:"low_price"`
	ClosePrice     float64 `json:"close_price"`
	Volume         float64 `json:"volume"`
	CloseTime      int64   `json:"close_time"`
	NumberOfTrades int     `json:"number_of_trades"`
}
