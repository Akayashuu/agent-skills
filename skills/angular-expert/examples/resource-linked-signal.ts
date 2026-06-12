// resource() for reactive async reads, linkedSignal() for resettable derived
// state. resource re-fetches when params() change, cancels stale loads, and
// exposes value()/isLoading()/error() as signals.
import { Component, input, linkedSignal, resource } from '@angular/core';

interface User {
  id: string;
  name: string;
}

declare function fetchUser(id: string): Promise<User>;

@Component({
  selector: 'app-user-card',
  template: `
    @if (user.isLoading()) {
      <p>Loading…</p>
    } @else {
      <p>{{ user.value()?.name }}</p>
      <select [value]="selected()">
        @for (opt of options(); track opt) {
          <option [value]="opt">{{ opt }}</option>
        }
      </select>
    }
  `,
})
export class UserCard {
  userId = input.required<string>();
  options = input<string[]>([]);

  user = resource({
    params: () => ({ id: this.userId() }),
    loader: ({ params }) => fetchUser(params.id),
  });

  // Derived BUT writable: resets to the first option when options change, yet
  // the user can still .set() a choice. computed() can't be written; an effect()
  // that writes a signal would be a hack.
  selected = linkedSignal(() => this.options()[0]);
}
