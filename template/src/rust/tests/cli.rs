//! Exercise the compiled command-line application.

use std::io;
use std::process::Command;

#[test]
fn greets_from_the_command_line() -> io::Result<()> {
    for (args, expected) in [
        (vec![], "Hello, world!\n"),
        (vec!["Ada"], "Hello, Ada!\n"),
        (vec!["Ada Lovelace"], "Hello, Ada Lovelace!\n"),
        (vec![""], "Hello, world!\n"),
    ] {
        let output = Command::new(env!("CARGO_BIN_EXE_example-app"))
            .args(args)
            .output()?;
        assert!(output.status.success());
        assert_eq!(output.stdout, expected.as_bytes());
        assert!(output.stderr.is_empty());
    }
    Ok(())
}
