// One file holding MANY entries → use file() instead of glob().
// Each top-level key/array item becomes an entry; its `id` comes from the data.
import { defineCollection, z } from 'astro:content';
import { file } from 'astro/loaders';

const dogs = defineCollection({
  loader: file('src/data/dogs.json'), // [{ id, breed, size }, ...]
  schema: z.object({
    id: z.string(),
    breed: z.string(),
    size: z.enum(['small', 'medium', 'large']),
  }),
});

export const collections = { dogs };
