// Signal inputs/outputs over decorators: reactive and typed, and they compose
// with computed() — no ngOnChanges to derive state.
import { Component, computed, input, output } from '@angular/core';

@Component({
  selector: 'app-greet',
  template: `
    <h2>{{ upper() }}</h2>
    <button (click)="saved.emit(name())">Save</button>
  `,
})
export class Greet {
  // input.required<T>() makes a missing binding a compile error.
  name = input.required<string>();
  // Reading name() inside computed() wires a reactive dependency edge —
  // something @Input() + ngOnChanges can't do.
  upper = computed(() => this.name().toUpperCase());
  saved = output<string>();
}
