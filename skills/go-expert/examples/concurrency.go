package examples

import (
	"context"
	"fmt"
)

// FanIn runs work for each input and stops early if ctx is cancelled, without
// leaking goroutines: every send is guarded by a select on ctx.Done().
func FanIn(ctx context.Context, inputs []int) ([]int, error) {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range inputs {
			select {
			case out <- n * 2:
			case <-ctx.Done():
				return
			}
		}
	}()

	var results []int
	for {
		select {
		case v, ok := <-out:
			if !ok {
				return results, nil
			}
			results = append(results, v)
		case <-ctx.Done():
			return results, fmt.Errorf("fan-in: %w", ctx.Err())
		}
	}
}
