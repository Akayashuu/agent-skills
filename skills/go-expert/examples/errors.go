package examples

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("not found")

type ValidationError struct{ Field string }

func (e *ValidationError) Error() string { return "invalid field: " + e.Field }

// LoadUser wraps sentinel and typed errors with %w so callers can match them.
func LoadUser(id string) error {
	if id == "" {
		return fmt.Errorf("load user: %w", &ValidationError{Field: "id"})
	}
	return fmt.Errorf("load user %q: %w", id, ErrNotFound)
}

// Classify shows the two idiomatic matchers: Is for sentinels, As for typed errors.
func Classify(err error) string {
	var ve *ValidationError
	switch {
	case errors.As(err, &ve):
		return "validation:" + ve.Field
	case errors.Is(err, ErrNotFound):
		return "not-found"
	default:
		return "unknown"
	}
}
