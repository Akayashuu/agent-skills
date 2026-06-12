// Reset state on identity change with `key`, not an effect. A different user
// is a different form; changing the key remounts the subtree and discards old
// state, with no stale frame between the switch and an effect firing.

import { useState } from 'react'

function ProfileForm() {
  const [draft, setDraft] = useState('')
  return <textarea value={draft} onChange={(e) => setDraft(e.target.value)} />
}

function Profile({ userId }: { userId: string }) {
  return <ProfileForm key={userId} />
}

export { Profile }
