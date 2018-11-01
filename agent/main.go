package main

import (
	"encoding/json"

	"fmt"

	"io/ioutil"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/urfave/negroni"
)

func main() {

	r := mux.NewRouter()

	r.HandleFunc("/api/runCon", action(runConHandler)).Methods("POST")

	r.HandleFunc("/api/destroyCon", action(destroyConHandler)).Methods("POST")

	n := negroni.New()

	n.Use(negroni.NewRecovery())

	n.Use(logger)

	n.UseHandler(r)

	n.Run(":8005")

}

var logger = newLogger()

type myHandlerFunc func(http.ResponseWriter, *http.Request) error

func action(f myHandlerFunc) http.HandlerFunc {

	return func(rw http.ResponseWriter, r *http.Request) {

		if err := f(rw, r); err != nil {

			fmt.Printf("[ERROR] %v\n", err)

			http.Error(rw, err.Error(), http.StatusInternalServerError)

			return

		}

	}

}

func newLogger() *negroni.Logger {

	l := negroni.NewLogger()

	return l

}

func runConHandler(rw http.ResponseWriter, r *http.Request) error {

	body, err := ioutil.ReadAll(r.Body)

	if err != nil {

		fmt.Println(err)

		return err

	}

	defer r.Body.Close()

	var con ContainerType

	if err := json.Unmarshal(body, &con); err != nil {

		fmt.Println(err)

		return err

	}

	con.RunContainer()

	return nil

}

func destroyConHandler(rw http.ResponseWriter, r *http.Request) error {

	body, err := ioutil.ReadAll(r.Body)

	if err != nil {

		fmt.Println(err)

		return err

	}

	defer r.Body.Close()

	var con ContainerType

	if err := json.Unmarshal(body, &con); err != nil {

		fmt.Println(err)

		return err

	}

	con.DestroyContainer()

	return nil

}
