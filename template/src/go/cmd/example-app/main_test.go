package main

import (
	"bytes"
	"errors"
	"testing"
)

func TestRun(t *testing.T) {
	tests := []struct {
		name string
		args []string
		want string
	}{
		{name: "default", want: "Hello, world!\n"},
		{name: "named", args: []string{"Ada"}, want: "Hello, Ada!\n"},
		{name: "empty", args: []string{""}, want: "Hello, world!\n"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var output bytes.Buffer
			if err := run(tt.args, &output); err != nil {
				t.Fatal(err)
			}
			if got := output.String(); got != tt.want {
				t.Errorf("run() output = %q, want %q", got, tt.want)
			}
		})
	}
}

type failingWriter struct {
	err error
}

func (w failingWriter) Write([]byte) (int, error) {
	return 0, w.err
}

func TestRunReportsWriteError(t *testing.T) {
	want := errors.New("output unavailable")
	if err := run(nil, failingWriter{err: want}); !errors.Is(err, want) {
		t.Fatalf("run() error = %v, want %v", err, want)
	}
}
