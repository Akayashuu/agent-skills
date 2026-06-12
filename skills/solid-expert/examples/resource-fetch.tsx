import { createResource, Show, type Accessor } from "solid-js";

// createResource for async: when source changes (and isn't false/null/undefined)
// the fetcher re-runs. Returns [resource, { mutate, refetch }].
export default function UserCard(props: { userId: Accessor<number> }) {
  const [user] = createResource(props.userId, (id) =>
    fetch(`/u/${id}`).then((r) => r.json()),
  );
  // mutate(v) writes optimistically; refetch() reloads.
  return (
    <Show when={!user.loading} fallback={<span>Loading…</span>}>
      <p>{user()?.name}</p>
    </Show>
  );
}
