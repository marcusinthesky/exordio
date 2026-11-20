// Package greet supplies the greeting shared by the example command and callers.
package greet

// Message returns a greeting, using "world" when name is empty.
func Message(name string) string {
	if name == "" {
		name = "world"
	}
	return "Hello, " + name + "!"
}
