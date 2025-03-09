package main

import (
	"database/sql"
	"html/template"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"

	"os"

	"strconv"

	"github.com/golang-jwt/jwt/v4"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

type server struct {
	db *sql.DB
}

var templates *template.Template

func initDatabase() {
	// Create the database
	db, err := sql.Open("sqlite3", "/state/zoo.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create the users table
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		balance INTEGER NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Create the tickets table
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS tickets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		event_name TEXT NOT NULL,
		price INTEGER NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Insert some sample tickets if the table is empty
	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM tickets").Scan(&count)
	if err != nil {
		log.Fatal("Error checking tickets table:", err)
	}

	if count == 0 {
		_, err = db.Exec("INSERT INTO tickets (event_name, price) VALUES (?, ?)", "Входной билет в зоопарк (взрослый)", 100)
		if err != nil {
			log.Fatal("Error inserting ticket:", err)
		}
	}

}

func main() {

	initDatabase()

	db, err := sql.Open("sqlite3", "/state/zoo.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	s := server{db: db}

	// Initialize templates
	templates = template.Must(template.ParseGlob("templates/*.html"))

	// serve static files
	http.Handle("/{token}/static/", s.StripParts(3, http.FileServer(http.Dir("static"))))
	// Set up routes

	// add 404 handler
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		//render 404 page
		if err := templates.ExecuteTemplate(w, "404.html", nil); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error executing template:", err)
		}
	})

	http.HandleFunc("/{token}/login", s.handleLogin)
	http.HandleFunc("/{token}/register", s.handleRegister)
	http.HandleFunc("/{token}/logout", s.handleLogout)
	http.HandleFunc("/{token}/add-to-cart", s.addToCart)
	http.HandleFunc("/{token}/checkout", s.handleCheckout)
	http.HandleFunc("/{token}/topup", s.handleTopup)
	http.HandleFunc("/{token}", s.handleIndex)
	http.HandleFunc("/{token}/{$}", s.handleIndex)
	// Add more handlers as needed

	//try to obtain the port from the environment
	port := "8080"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}

	// Start the server
	log.Printf("Server listening on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
	defer db.Close()
}

func (s *server) StripParts(parts int, h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		p := strings.Split(r.URL.Path, "/")
		rp := strings.Split(r.URL.RawPath, "/")
		if len(p) < parts+1 {
			http.NotFound(w, r)
		} else {
			r2 := new(http.Request)
			*r2 = *r
			r2.URL = new(url.URL)
			*r2.URL = *r.URL
			r2.URL.Path = strings.Join(p[parts:], "/")
			if r.URL.RawPath == "" {
				r2.URL.RawPath = ""
			} else {
				r2.URL.RawPath = strings.Join(rp[parts:], "/")
			}
			h.ServeHTTP(w, r2)
		}
	})
}

func (s *server) authenticateUser(username, password string) bool {
	var dbPassword string

	// Query the database for the password of the user with the given username
	err := s.db.QueryRow("SELECT password FROM users WHERE username = ?", username).Scan(&dbPassword)
	if err != nil {
		if err == sql.ErrNoRows {
			// User not found
			log.Print("Authentication failed: user not found")
		} else {
			// Database error
			log.Printf("Database error: %v", err)
		}
		return false
	}

	// Compare the password with the hashed password from the database
	err = bcrypt.CompareHashAndPassword([]byte(dbPassword), []byte(password))
	if err != nil {
		// Password does not match
		log.Print("Authentication failed: password does not match")
		return false
	}

	// Authentication successful
	return true
}

func (s *server) registerUser(username string, password string) (bool, error) {
	// Hash the password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		log.Printf("Error hashing password: %v", err)
		return false, err
	}

	// Insert the new user into the database
	_, err = s.db.Exec("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", username, string(hashedPassword), 0)
	if err != nil {
		log.Printf("Error inserting user: %v", err)
		return false, err
	}

	return true, nil
}

func (s *server) handleIndex(w http.ResponseWriter, r *http.Request) {
	var userdata struct {
		Username   string
		Balance    int
		IsLoggedIn bool
		Cart       [][]int
	}

	// Get user data from token
	username, cart, err := s.checkUserToken(r)
	if err != nil {
		// user not logged in
		userdata.IsLoggedIn = false
		userdata.Username = ""
		userdata.Balance = 0
		userdata.Cart = [][]int{}
	}
	// log.Print("Username:", username)

	if username != "" {
		// user logged in
		userdata.IsLoggedIn = true
		userdata.Username = username
		userdata.Cart = cart

		// get user balance
		err := s.db.QueryRow("SELECT balance FROM users WHERE username = ?", username).Scan(&userdata.Balance)
		if err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error getting user balance:", err)
			return
		}
	}
	// log.Print("Userdata:", userdata)

	rows, err := s.db.Query("SELECT id, event_name, price FROM tickets")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print("Error getting tickets:", err)
		return
	}
	defer rows.Close()

	var tickets []struct {
		ID          int
		EventName   string
		Price       int
		InCartCount int
	}

	for rows.Next() {
		var t struct {
			ID          int
			EventName   string
			Price       int
			InCartCount int
		}
		// scan the cart for each ticket

		if err := rows.Scan(&t.ID, &t.EventName, &t.Price); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error scanning tickets:", err)
			return
		}
		t.InCartCount = 0
		for _, item := range userdata.Cart {
			if item[0] == t.ID {
				t.InCartCount = item[2]
				break
			}
		}

		tickets = append(tickets, t)
	}

	data := struct {
		Tickets []struct {
			ID          int
			EventName   string
			Price       int
			InCartCount int
		}
		User struct {
			Username   string
			Balance    int
			IsLoggedIn bool
			Cart       [][]int
		}
		Token string
	}{
		Tickets: tickets,
		User:    userdata,
		Token:   r.PathValue("token"),
	}

	// Render template with tickets data
	if err := templates.ExecuteTemplate(w, "index.html", data); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print("Error executing template:", err)
	}
}

func (s *server) handleRegister(w http.ResponseWriter, r *http.Request) {

	switch r.Method {
	case "GET":
		data := struct {
			Token string
		}{
			Token: r.PathValue("token"),
		}

		// Serve the registration page
		err := templates.ExecuteTemplate(w, "register.html", data)
		if err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error executing template:", err)
		}

	case "POST":
		// Process registration
		username := r.FormValue("username")
		password := r.FormValue("password")
		confirmPassword := r.FormValue("confirmPassword")
		if password != confirmPassword {
			http.Error(w, "Passwords do not match", http.StatusBadRequest)
			return
		}
		if len(password) < 10 {
			http.Error(w, "Password must be at least 10 characters long", http.StatusBadRequest)
			return
		}
		if len(username) < 4 {
			http.Error(w, "Username must be at least 4 characters long", http.StatusBadRequest)
			return
		}

		if username == "" || password == "" {
			http.Error(w, "Username and password are required", http.StatusBadRequest)
			return
		}

		// check if user already exists
		var count int
		err := s.db.QueryRow("SELECT COUNT(*) FROM users WHERE username = ?", username).Scan(&count)
		if err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error checking user:", err)
			return
		}
		if count > 0 {
			http.Error(w, "User already exists", http.StatusBadRequest)
			return
		}

		success, err := s.registerUser(username, password)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			log.Print("Error registering user:", err)
			return
		}

		if !success {
			http.Error(w, "Registration failed", http.StatusBadRequest)
			log.Print("Registration failed")
			return
		}

		// Redirect or inform the user of successful registration
		http.Redirect(w, r, "/"+r.PathValue("token")+"/login", http.StatusSeeOther)

	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func (s *server) handleLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		data := struct {
			Token string
		}{
			Token: r.PathValue("token"),
		}
		// Serve the login page
		err := templates.ExecuteTemplate(w, "login.html", data)
		if err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error executing template:", err)
		}
		return
	}

	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	username := r.FormValue("username")
	password := r.FormValue("password")

	// Placeholder for actual authentication logic
	if !s.authenticateUser(username, password) {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}

	// Create a new token object

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": username,
		"cart":     [][]int{},
		"exp":      time.Now().Add(time.Hour * 72).Unix(),
	})

	// Sign and get the complete encoded token as a string using the secret
	tokenString, err := token.SignedString([]byte("super_secret_ugra_key_noone_guess112121"))
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	// rediret to home page with token in cookie
	http.SetCookie(w, &http.Cookie{
		Name:   "token",
		Value:  tokenString,
		MaxAge: 60 * 60 * 72,
	})
	http.Redirect(w, r, "/"+r.PathValue("token"), http.StatusSeeOther)
}

func (s *server) checkUserToken(r *http.Request) (string, [][]int, error) {
	cookie, err := r.Cookie("token")
	if err != nil {
		return "", nil, err
	}

	tokenString := cookie.Value
	if tokenString == "" {
		return "", nil, err
	}
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		return []byte("super_secret_ugra_key_noone_guess112121"), nil
	})
	if err != nil {
		return "", nil, err
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		return "", nil, err
	}

	username, ok := claims["username"].(string)
	if !ok {
		return "", nil, err
	}

	// get user data from db
	var count int
	err = s.db.QueryRow("SELECT COUNT(*) FROM users WHERE username = ?", username).Scan(&count)
	if err != nil {
		log.Print("Error checking user:", err)
		return "", nil, err
	}
	if count == 0 {
		log.Print("User not found")
		return "", nil, err
	}
	// log.Print("User found, count:", count)

	// get cart from token
	cart := [][]int{}
	if claims["cart"] != nil {
		cartInterface := claims["cart"].([]interface{})
		for _, item := range cartInterface {
			cartItem := item.([]interface{})
			intSlice := make([]int, len(cartItem))
			for i, v := range cartItem {
				intSlice[i] = int(v.(float64))
			}
			cart = append(cart, intSlice)
		}
	}
	// log.Print("Cart:", cart)

	return username, cart, nil
}

func (s *server) handleLogout(w http.ResponseWriter, r *http.Request) {
	http.SetCookie(w, &http.Cookie{
		Name:   "token",
		Value:  "",
		MaxAge: -1,
	})
	http.Redirect(w, r, "/"+r.PathValue("token"), http.StatusSeeOther)
}

func (s *server) addToCart(w http.ResponseWriter, r *http.Request) {
	// check if user is logged in
	username, cart, err := s.checkUserToken(r)
	if err != nil {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}

	// get ticket id from request
	ticketID_str := r.FormValue("ticketID")
	count_str := r.FormValue("count")
	if ticketID_str == "" || count_str == "" {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	// convert ticket id to int
	ticketID, err := strconv.Atoi(ticketID_str)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	redirect := r.FormValue("redirect")
	if redirect == "" {
		redirect = "/" + r.PathValue("token")
	}

	// convert count to int
	count, err := strconv.Atoi(count_str)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if ticketID <= 0 {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}
	var remove_ticketID bool

	if count > 92233720368547759 {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}
	if count < 0 {
		remove_ticketID = true
	}

	// get ticket data from db
	var ticket struct {
		Price     int
		EventName string
	}
	err = s.db.QueryRow("SELECT price, event_name FROM tickets WHERE id = ?", ticketID).Scan(&ticket.Price, &ticket.EventName)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	ticketAlreadyInCart := false
	// check if ticket already in cart
	for _, entry := range cart {
		if entry[0] == ticketID {
			ticketAlreadyInCart = true
			if remove_ticketID {
				cart = append(cart[:0], cart[1:]...)
			} else {
				entry[2] += count
				if entry[2] < 0 {
					http.Error(w, "Bad request", http.StatusBadRequest)
					return
				}
			}
			break
		}
	}

	if !ticketAlreadyInCart && !remove_ticketID {
		cart = append(cart, []int{ticketID, ticket.Price, count})
	}

	// update token with new cart
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": username,
		"cart":     cart,
		"exp":      time.Now().Add(time.Hour * 72).Unix(),
	})

	// Sign and get the complete encoded token as a string using the secret
	tokenString, err := token.SignedString([]byte("super_secret_ugra_key_noone_guess112121"))
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	// rediret to home page with token in cookie
	http.SetCookie(w, &http.Cookie{
		Name:   "token",
		Value:  tokenString,
		MaxAge: 60 * 60 * 72,
	})

	http.Redirect(w, r, redirect, http.StatusSeeOther)
}

func (s *server) handleCheckout(w http.ResponseWriter, r *http.Request) {
	// check if user is logged in
	username, cart, err := s.checkUserToken(r)
	if err != nil {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}

	// get user balance
	var balance int
	err = s.db.QueryRow("SELECT balance FROM users WHERE username = ?", username).Scan(&balance)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	tickets := []struct {
		ID        int
		Price     int
		EventName string
		Count     int
	}{}

	// calculate total price
	totalPrice := 0
	for _, entry := range cart {
		totalPrice += entry[1] * entry[2]
		// get name of event
		var eventName string
		err = s.db.QueryRow("SELECT event_name FROM tickets WHERE id = ?", entry[0]).Scan(&eventName)
		if err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print(err)
			return
		}

		tickets = append(tickets, struct {
			ID        int
			Price     int
			EventName string
			Count     int
		}{entry[0], entry[1], eventName, entry[2]})
	}

	// if GET request, render checkout page
	if r.Method == "GET" {
		data := struct {
			TotalPrice int
			Balance    int
			Tickets    []struct {
				ID        int
				Price     int
				EventName string
				Count     int
			}
			Token string
		}{
			TotalPrice: totalPrice,
			Balance:    balance,
			Tickets:    tickets,
			Token:      r.PathValue("token"),
		}

		if err := templates.ExecuteTemplate(w, "checkout.html", data); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			log.Print("Error executing template:", err)
		}
		return
	}

	// check if cart is not empty
	if len(cart) == 0 {
		http.Error(w, "Cart is empty", http.StatusBadRequest)
		return
	}

	if totalPrice > balance {
		http.Error(w, "Insufficient balance", http.StatusBadRequest)
		return
	}

	// update user balance
	_, err = s.db.Exec("UPDATE users SET balance = ? WHERE username = ?", balance-totalPrice, username)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	// clear cart
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": username,
		"cart":     [][]int{},
		"exp":      time.Now().Add(time.Hour * 72).Unix(),
	})

	// Sign and get the complete encoded token as a string using the secret
	tokenString, err := token.SignedString([]byte("super_secret_ugra_key_noone_guess112121"))
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	// render template with success message
	http.SetCookie(w, &http.Cookie{
		Name:   "token",
		Value:  tokenString,
		MaxAge: 60 * 60 * 72,
	})

	confirmationCode, err := os.ReadFile("/flag.txt")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print(err)
		return
	}

	data := struct {
		TotalPrice   int
		Balance      int
		Confirmation string
		Token        string
	}{
		TotalPrice:   totalPrice,
		Balance:      balance - totalPrice,
		Confirmation: string(confirmationCode),
		Token:        r.PathValue("token"),
	}

	if err := templates.ExecuteTemplate(w, "confirmation.html", data); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print("Error executing template:", err)
	}
}

func (s *server) handleTopup(w http.ResponseWriter, r *http.Request) {
	// check if user is logged in
	username, _, err := s.checkUserToken(r)
	if err != nil {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}

	if username == "" {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}
	if r.Method != "GET" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	// return rendered topup page

	data := struct {
		Username string
		Token    string
	}{
		Username: username,
		Token:    r.PathValue("token"),
	}

	if err := templates.ExecuteTemplate(w, "topup.html", data); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		log.Print("Error executing template:", err)
	}
}
