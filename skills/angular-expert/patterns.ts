// Modern Angular reference component (v20+, verified against angular.dev).
// Every primitive here is STABLE: signals + signal inputs/outputs/queries (v20),
// linkedSignal/effect (v20), resource() (v22). Designed for zoneless (default v21+).
//
// This file is a teaching reference. It is structured to compile under strict
// templates with @angular/core >= 20; trim imports your project doesn't need.

import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  linkedSignal,
  model,
  output,
  resource,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';

interface User {
  id: string;
  name: string;
  active: boolean;
}

declare function fetchUser(id: string): Promise<User>;

@Component({
  selector: 'app-user-card',
  // OnPush is the floor for signal-driven components: a template only re-renders
  // when a signal it READ changes. This is precisely the zoneless model, so an
  // OnPush-everywhere codebase is zoneless-ready with no markForCheck() calls.
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (user.isLoading()) {
      <p>Loading…</p>
    } @else if (user.error()) {
      <p>Failed to load.</p>
    } @else if (user.value(); as u) {
      <h2>{{ greeting() }}</h2>
      <!-- @for REQUIRES track: stable identity preserves DOM, focus, animations -->
      <ul>
        @for (tag of tags(); track tag) {
          <li>{{ tag }}</li>
        } @empty {
          <li>No tags</li>
        }
      </ul>
      <button (click)="select(u)">Select</button>
    }
  `,
})
export class UserCard {
  // inject() over constructor params: works in field initializers, base classes,
  // and standalone functions; no constructor boilerplate.
  private readonly route = inject(ActivatedRoute);

  // Signal input: reactive and typed. required() makes absence a compile error.
  // Reading it (userId()) inside computed/resource creates a dependency edge —
  // something @Input() + ngOnChanges can't do.
  userId = input.required<string>();

  // Two-way bindable state via model() — replaces the @Input()/@Output() pair.
  selectedId = model<string | null>(null);

  // Typed event out. Leaner than `new EventEmitter()` and not a decorator.
  selected = output<User>();

  // Plain local signal — the unit of writable state.
  tags = signal<string[]>([]);

  // computed(): read-only derived value, recomputes lazily only when deps change.
  // Prefer this over a getter/method in the template (those run every CD pass).
  greeting = computed(() => `Hello, user ${this.userId()}`);

  // resource(): reactive async read. Re-runs loader when params() change and
  // cancels in-flight loads. Exposes value()/isLoading()/error() as signals —
  // no manual subscribe, no loading-boolean bookkeeping.
  user = resource({
    params: () => ({ id: this.userId() }),
    loader: ({ params }) => fetchUser(params.id),
  });

  // linkedSignal(): derived BUT writable. Resets to the latest user's id whenever
  // the resource reloads, yet select() can still override it. A computed() can't
  // be written, and an effect() that writes a signal is an anti-pattern here.
  activeId = linkedSignal(() => this.user.value()?.id ?? null);

  constructor() {
    // takeUntilDestroyed() ties the subscription to the component lifecycle, so
    // it auto-unsubscribes on destroy. Call it in an injection context (here, the
    // constructor) — it reads the current DestroyRef. Prefer signals/async pipe,
    // but this is the right tool when you must imperatively subscribe.
    this.route.fragment.pipe(takeUntilDestroyed()).subscribe((frag) => {
      if (frag) this.tags.update((t) => [...t, frag]); // .update, never mutate in place
    });
  }

  select(u: User): void {
    this.activeId.set(u.id);
    this.selectedId.set(u.id);
    this.selected.emit(u);
  }
}
