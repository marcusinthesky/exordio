//! Reusable greeting logic, independent of the command-line interface.

/// Return a greeting, using "world" when `name` is empty.
///
/// # Examples
///
/// ```
/// assert_eq!(example_app::greet("Ada"), "Hello, Ada!");
/// assert_eq!(example_app::greet(""), "Hello, world!");
/// ```
#[must_use]
pub fn greet(name: &str) -> String {
    let name = if name.is_empty() { "world" } else { name };
    format!("Hello, {name}!")
}

#[cfg(test)]
mod tests {
    use super::greet;

    #[test]
    fn greets_names_and_defaults() {
        for (name, expected) in [
            ("Ada", "Hello, Ada!"),
            ("", "Hello, world!"),
            ("Ada Lovelace", "Hello, Ada Lovelace!"),
            ("世界", "Hello, 世界!"),
        ] {
            assert_eq!(greet(name), expected);
        }
    }
}
