use std::fmt;

#[derive(Debug)]
pub enum LoadError {
    Empty,
    NotFound(String),
}

impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LoadError::Empty => write!(f, "id was empty"),
            LoadError::NotFound(id) => write!(f, "user {id} not found"),
        }
    }
}

impl std::error::Error for LoadError {}

/// Returns Result and uses `?`; no unwrap/expect on fallible paths.
pub fn load_user(id: &str) -> Result<String, LoadError> {
    if id.is_empty() {
        return Err(LoadError::Empty);
    }
    Err(LoadError::NotFound(id.to_string()))
}

/// Combinator style instead of a verbose match.
pub fn display_name(id: &str) -> String {
    load_user(id).unwrap_or_else(|e| format!("<{e}>"))
}
