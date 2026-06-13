/// Takes a slice (borrow), not an owned Vec, and returns a borrow — no clone needed.
pub fn longest<'a>(items: &'a [String]) -> Option<&'a str> {
    items.iter().map(String::as_str).max_by_key(|s| s.len())
}

/// Mutates in place through a mutable borrow rather than taking + returning ownership.
pub fn normalize(tags: &mut Vec<String>) {
    tags.iter_mut().for_each(|t| *t = t.trim().to_lowercase());
    tags.retain(|t| !t.is_empty());
}
