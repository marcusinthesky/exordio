//! Print a greeting using the shared library.

use std::io::{self, Write};

fn main() -> io::Result<()> {
    let name = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "world".to_owned());
    writeln!(io::stdout().lock(), "{}", example_app::greet(&name))
}
